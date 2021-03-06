"""
citrus_borg.tasks
-----------------

This module contains the `Celery tasks
<https://docs.celeryproject.org/en/latest/userguide/tasks.html>`__
used by the :ref:`Citrus Borg Application`.

:copyright:

    Copyright 2018 Provincial Health Service Authority
    of British Columbia

:contact:    serban.teodorescu@phsa.ca

:updated: Nov. 22, 2018

"""
from smtplib import SMTPConnectError

from django.utils import timezone

from celery import shared_task, group
from celery.utils.log import get_task_logger

from citrus_borg.dynamic_preferences_registry import get_preference
from citrus_borg.locutus.assimilation import process_borg
from citrus_borg.locutus.communication import (
    get_dead_bots, get_dead_brokers, get_dead_sites,
    get_logins_by_event_state_borg_hour, raise_failed_logins_alarm,
    login_states_by_site_host_hour, raise_ux_alarm, get_failed_events,
    get_failed_ux_events,
)
from citrus_borg.models import (
    WindowsLog, AllowedEventSource, WinlogbeatHost, KnownBrokeringDevice,
    WinlogEvent, BorgSite,
)

from p_soc_auto_base import utils as base_utils


LOGGER = get_task_logger(__name__)


# pylint: disable=W0703,R0914


@shared_task(queue='citrus_borg', rate_limit='10/s')
def store_borg_data(body):
    """
    task responsible for saving the data collected from remote `ControlUp`
    monitoring bot to various models in the :mod:`citrus_borg.models` module

    :arg dict body: the event data

    :returns: the value of the :attr:`uuid`
        attribute of the :class:`citrus_borg.models.WinlogEvent` instance
        saved by the task

    We are raising and logging multiple generic :exc:`Exceptions <Exception>`
    if things go wrong.
    """
    def reraise(msg, body, error):
        LOGGER.error('%s %s: %s', msg, body, str(error))
        raise error

    try:
        borg = process_borg(body, LOGGER)
    except Exception as error:
        reraise('cannot save event data from event', body, error)

    try:
        event_host = WinlogbeatHost.get_or_create_from_borg(borg)
    except Exception as error:
        reraise('cannot retrieve bot info from event', body, error)

    try:
        event_broker = KnownBrokeringDevice.get_or_create_from_borg(borg)
    except Exception as error:
        reraise('cannot retrieve session host info from event', body, error)

    try:
        event_source = AllowedEventSource.objects.get(
            source_name=borg.event_source)
    except Exception as error:
        reraise('cannot match event source for event', body, error)

    try:
        windows_log = WindowsLog.objects.get(log_name=borg.windows_log)
    except Exception as error:
        reraise('cannot match windows log info for event', body, error)

    user = WinlogEvent.get_or_create_user(
        get_preference('citrusborgcommon__service_user'))
    winlogevent = WinlogEvent(
        source_host=event_host, record_number=borg.record_number,
        event_source=event_source, windows_log=windows_log,
        event_state=borg.borg_message.state, xml_broker=event_broker,
        event_test_result=borg.borg_message.test_result,
        storefront_connection_duration=borg.borg_message.
        storefront_connection_duration,
        receiver_startup_duration=borg.borg_message.receiver_startup_duration,
        connection_achieved_duration=borg.borg_message.
        connection_achieved_duration,
        logon_achieved_duration=borg.borg_message.logon_achieved_duration,
        logoff_achieved_duration=borg.borg_message.logoff_achieved_duration,
        failure_reason=borg.borg_message.failure_reason,
        failure_details=borg.borg_message.failure_details,
        raw_message=borg.borg_message.raw_message,
        created_by=user, updated_by=user
    )

    try:
        winlogevent.save()
    except Exception as error:
        reraise('cannot save data collected from event', body, error)

    return 'saved event: %s' % winlogevent.uuid
# pylint: enable=R0914


@shared_task(queue='citrus_borg', rate_limit='3/s')
def get_orion_id(pk):  # pylint: disable=invalid-name
    """
    task that is responsible for maintaining Orion information in the
    :class:`citrus_borg.models.WinlogbeatHost` model

    This task is a wrapper for the :meth:`models.WinlogbeatHost.get_orion_id`
    instance method.

    :arg int pk: the values of the primary key attribute of the
        :class:citrus_borg.models.WinlogbeatHost`

    :raises: generic :exc:`Exception`

    """
    instance = WinlogbeatHost.objects.get(pk=pk)

    try:
        return instance.get_orion_id()
    except Exception as error:
        raise error


@shared_task(queue='citrus_borg')
def get_orion_ids():
    """
    task responsible for spawning :func:`get_orion_id` tasks

    This task will spawn a separate :func:`get_orion_id` task for each
    :class:`citrus_borg.models.WinlogbeatHost` instance that is `enabled`

    :returns: a status string containing the number of
        :class:`citrus_borg.models.WinlogbeatHost` instances

    """
    citrus_borg_pks = base_utils.get_pk_list(
        WinlogbeatHost.objects.filter(enabled=True))

    group(get_orion_id.s(pk) for pk in citrus_borg_pks)()

    return 'refreshing orion ids for %s citrix bots' % len(citrus_borg_pks)


@shared_task(queue='citrus_borg')
def expire_events():
    """
    task that marks :class:`citrus_borg.models.WinlogEvent` instances as
    expired; it will also delete `expired` instances if so configured

    This task is configured by:

    * `Mark Events As Expired If Older Than
      <../../../admin/dynamic_preferences/globalpreferencemodel/?q=expire_events_older_than>`__

       This preference is defined by
       :class:`citrus_borg.dynamic_preferences_registry.ExpireEvents`

    * `Delete Expired Events
      <../../../admin/dynamic_preferences/globalpreferencemodel/?q=delete_expired_events>`__

       The preference is defined by
       :class:`citrus_borg.dynamic_preferences_registry.DeleteExpireEvents`

    :returns: a status string about how many events were handles by the task,
        the types of operations performed, and the threshold used for marking
        events as expired (see `Mark Events As Expired If Older Than
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=expire_events_older_than>`__)
    :rtype: str

    """
    expired = WinlogEvent.objects.filter(
        created_on__lt=timezone.now()
        - get_preference('citrusborgevents__expire_events_older_than')
    ).update(is_expired=True)

    if get_preference('citrusborgevents__delete_expired_events'):
        WinlogEvent.objects.filter(is_expired=True).all().delete()
        return 'deleted %s events accumulated over the last %s' % (
            expired,
            get_preference('citrusborgevents__expire_events_older_than'))

    return 'expired %s events accumulated over the last %s' % (
        expired, get_preference('citrusborgevents__expire_events_older_than'))


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_dead_borgs_alert(now=None, send_no_news=None, **dead_for):
    """
    send out alerts about `Citrix` monitoring bots that have not been seen within
    the time interval defined by arguments `now` and `dead_for` via email

    :arg now: the initial moment

        By default (and in most useful cases for functions that return
        historical data), the initial moment should be the value of
        :meth:`datetime.datetime.now` (:meth:`django.utils.timezone.now` in
        `Django` applications).

        :Note:

            **We are not using this argument in the current implementation of the
            :ref:`Citrus Borg Application`.**

            The current code base expects that `now` is either a :class:`NoneType`
            object or a :class:`datetime.datetime` object.
            Unfortunately, :class:`datetime.datetime` objects cannot be serialized
            to `JSON <https://www.json.org/>`__ and the mechanism used to invoke this
            task is using `JSON` for passing arguments.

            .. todo::

                Extend :meth:`p_soc_auto_base.utils.MomentOfTime.now` to accept
                data types are `JSON` serializable.

            It is possible to use this argument if the task is `called
            <https://docs.celeryproject.org/en/latest/userguide/calling.html#basics>`__
            with `apply_async()
            <https://docs.celeryproject.org/en/latest/reference/celery.app.task.html#celery.app.task.Task.apply_async>`__
            with the `serializer` argument set to 'pickle'.

    :arg dict dead_for: optional `Keyword Arguments
        <https://docs.python.org/3.6/tutorial/controlflow.html#keyword-arguments>`__
        used for initializing a :class:`datetime.timedelta` object

        This is the equivalent of the `time_delta` argument used by
        :func:`citrus_borg.locutus.communication.get_dead_bots` and most of the
        other functions in that module.

        This argument must match the arguments required by the
        :class:`datetime.timedelta` constructor, e.g.

        .. ipython::

            In [5]: from django.utils import timezone

            In [6]: time_delta=timezone.timedelta(hours=4, minutes=10)

            In [7]: time_delta
            Out[7]: datetime.timedelta(0, 15000)

            In [8]: print(time_delta)
            4:10:00

            In [9]:

        The reason for this approach is the same as above.
        :class:`datetime.timedelta` objects are not `JSON` serializable.

        Valid names for the `Keyword Arguments
        <https://docs.python.org/3.6/tutorial/controlflow.html#keyword-arguments>`__
        defined by `dead_for` are `days`, `hours`, `minutes`, and `seconds`. All
        the values passed via these `keyword arguments` must be of type
        :class:`float` (or castable to :class:`float`, e.g. :class:`int`).

        By default the `dead_for` is not present. In this case, the function will
        pick the `time_delta` value from the dynamic preference
        `Bot not seen alert threshold
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=dead_bot_after>`__

    :arg bool send_no_news: this argument determines whether emails will be sent
        even if there are no alerts

        Sending emails with "all is well" is atractive because it provides
        something similar to a heartbeat for the application. The problem
        with that is the number of emails not containing any relevant information
        that will clog inboxes and reduce user attention.

        By default, the value of this argument will be picked from dynamic
        preference `Do not send empty citrix alert emails
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=send_no_news>`__

    This task used the subscription at `Dead Citrix monitoring bots
    <../../../admin/ssl_cert_tracker/subscription/?q=Dead+Citrix+monitoring+bots>`__
    to render the emails being sent.
    """
    now = base_utils.MomentOfTime.now(now)

    if not dead_for:
        time_delta = get_preference('citrusborgnode__dead_bot_after')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    if send_no_news is None:
        send_no_news = get_preference('citrusborgcommon__send_no_news')

    if not isinstance(send_no_news, bool):
        raise TypeError(
            'object {} type {} is not valid. must be boolean'.
            format(send_no_news, type(send_no_news))
        )

    data = get_dead_bots(now=now, time_delta=time_delta)
    if not data and send_no_news:
        return (
            'all monitoring bots were active between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data,
            subscription=base_utils.get_subscription(
                'Dead Citrix monitoring bots'),
            logger=LOGGER, time_delta=time_delta)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_dead_borgs_report(now=None, send_no_news=False, **dead_for):
    """
    generate and email reports about `Citrix` monitoring bots that have not been seen within
    the time interval defined by arguments `now` and `dead_for` via email

    This task is almost identical to :func:`email_dead_borgs_alert` with the
    exception of the default value for the :class:`datetime.timedelta` object
    created when `dead_for` is not present.
    This value is picked from dynamic preference `Reporting period for dead nodes
    <../../../admin/dynamic_preferences/globalpreferencemodel/?q=node_forgotten_after>`__

    This task used the subscription at `Dead Citrix monitoring bots
    <../../../admin/ssl_cert_tracker/subscription/?q=Dead+Citrix+monitoring+bots>`__
    to render the emails being sent.
    """
    now = base_utils.MomentOfTime.now(now)

    if not dead_for:
        time_delta = get_preference('citrusborgnode__node_forgotten_after')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    data = get_dead_bots(now=now, time_delta=time_delta)
    if not data and send_no_news:
        return (
            'all monitoring bots were active between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data,
            subscription=base_utils.get_subscription(
                'Dead Citrix monitoring bots'),
            logger=LOGGER, time_delta=time_delta)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_dead_sites_alert(now=None, send_no_news=None, **dead_for):
    """
    send out alerts about remote sites where all the `Citrix` monitoring bots that
    have not been seen within the time interval defined by arguments `now` and
    `dead_for` via email

    This task is almost identical to :func:`email_dead_borgs_alert` with the
    exception of the default value for the :class:`datetime.timedelta` object
    created when `dead_for` is not present.
    This value is picked from dynamic preference `Site not seen alert threshold
    <../../../admin/dynamic_preferences/globalpreferencemodel/?q=dead_site_after>`__.

    This task used the subscription at `Dead Citrix client sites
    <../../../admin/ssl_cert_tracker/subscription/?q=Dead+Citrix+client+sites>`__
    to render the emails being sent.
    """
    now = base_utils.MomentOfTime.now(now)

    if not dead_for:
        time_delta = get_preference('citrusborgnode__dead_site_after')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    if send_no_news is None:
        send_no_news = get_preference('citrusborgcommon__send_no_news')

    if not isinstance(send_no_news, bool):
        raise TypeError(
            'object {} type {} is not valid. must be boolean'.
            format(send_no_news, type(send_no_news))
        )

    data = get_dead_sites(now=now, time_delta=time_delta)
    if not data and send_no_news:
        return (
            'at least one monitoring bot on each site was active between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data,
            subscription=base_utils.get_subscription(
                'Dead Citrix client sites'),
            logger=LOGGER, time_delta=time_delta)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_dead_sites_report(now=None, send_no_news=False, **dead_for):
    """
    generate and email reports about remote sites where`Citrix` monitoring bots
    have not been seen within the time interval defined by arguments `now` and
    `dead_for` via email

    This task is almost identical to :func:`email_dead_borgs_alert` with the
    exception of the default value for the :class:`datetime.timedelta` object
    created when `dead_for` is not present.
    This value is picked from dynamic preference `Reporting period for dead nodes
    <../../../admin/dynamic_preferences/globalpreferencemodel/?q=node_forgotten_after>`__

    This task used the subscription at `Dead Citrix client sites
    <../../../admin/ssl_cert_tracker/subscription/?q=Dead+Citrix+client+sites>`__
    to render the emails being sent.
    """
    now = base_utils.MomentOfTime.now(now)

    if not dead_for:
        time_delta = get_preference('citrusborgnode__node_forgotten_after')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    data = get_dead_sites(now=now, time_delta=time_delta)
    if not data and send_no_news:
        return (
            'at least one monitoring bot on each site was active between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data,
            subscription=base_utils.get_subscription(
                'Dead Citrix client sites'),
            logger=LOGGER, time_delta=time_delta)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_dead_servers_report(now=None, send_no_news=False, **dead_for):
    """
    generate and email reports about `Citrix` application servers that have not
    service any requests during the time interval defined by arguments `now` and
    `dead_for` via email

    This task is almost identical to :func:`email_dead_borgs_alert` with the
    exception of the default value for the :class:`datetime.timedelta` object
    created when `dead_for` is not present.
    This value is picked from dynamic preference `Reporting period for dead nodes
    <../../../admin/dynamic_preferences/globalpreferencemodel/?q=node_forgotten_after>`__

    This task used the subscription at `Missing Citrix farm hosts
    <../../../admin/ssl_cert_tracker/subscription/?q=Missing+Citrix+farm+hosts>`__
    to render the emails being sent.
    """
    now = base_utils.MomentOfTime.now(now)

    if not dead_for:
        time_delta = get_preference('citrusborgnode__node_forgotten_after')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    data = get_dead_brokers(now=now, time_delta=time_delta)
    if not data and send_no_news:
        return (
            'all known Cerner session servers were active between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data,
            subscription=base_utils.get_subscription(
                'Missing Citrix farm hosts'),
            logger=LOGGER, time_delta=time_delta)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_dead_servers_alert(now=None, send_no_news=None, **dead_for):
    """
    send out alerts about `Citrix` application servers that have not
    service any requests during the time interval defined by arguments `now` and
    `dead_for` via email

    This task is almost identical to :func:`email_dead_borgs_alert` with the
    exception of the default value for the :class:`datetime.timedelta` object
    created when `dead_for` is not present.
    This value is picked from dynamic preference `Reporting period for dead nodes
    <../../../admin/dynamic_preferences/globalpreferencemodel/?q=node_forgotten_after>`__

    This task used the subscription at `Missing Citrix farm hosts
    <../../../admin/ssl_cert_tracker/subscription/?q=Missing+Citrix+farm+hosts>`__
    to render the emails being sent.
    """
    now = base_utils.MomentOfTime.now(now)

    if not dead_for:
        time_delta = get_preference('citrusborgnode__node_forgotten_after')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    if send_no_news is None:
        send_no_news = get_preference('citrusborgcommon__send_no_news')

    if not isinstance(send_no_news, bool):
        raise TypeError(
            'object {} type {} is not valid. must be boolean'.
            format(send_no_news, type(send_no_news))
        )

    data = get_dead_brokers(now=now, time_delta=time_delta)
    if not data and send_no_news:
        return (
            'all known Cerner session servers were active between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data,
            subscription=base_utils.get_subscription(
                'Missing Citrix farm hosts'),
            logger=LOGGER, time_delta=time_delta)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_borg_login_summary_report(now=None, **dead_for):
    """
    prepare and email a report with all the logon events generated by the `Citrix`
    bots

    The report includes events that occurred during the interval defined by the
    arguments `now` and `dead_for`. The report includes counts for `failed` and
    `successful` events.

    This task is almost identical to :func:`email_dead_borgs_alert` with the
    exception of the default value for the :class:`datetime.timedelta` object
    created when `dead_for` is not present.
    This value is picked from dynamic preference `Ignore events created older than
    <../../../admin/dynamic_preferences/globalpreferencemodel/?q=ignore_events_older_than>`__.

    This task used the subscription at `Citrix logon event summary
    <../../../admin/ssl_cert_tracker/subscription/?q=Citrix+logon+event+summary>`__
    to render the emails being sent.
    """
    if not dead_for:
        time_delta = get_preference(
            'citrusborgevents__ignore_events_older_than')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    try:
        return base_utils.borgs_are_hailing(
            data=get_logins_by_event_state_borg_hour(
                now=base_utils.MomentOfTime.now(now), time_delta=time_delta),
            subscription=base_utils.get_subscription(
                'Citrix logon event summary'),
            logger=LOGGER, time_delta=time_delta)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat')
def email_sites_login_ux_summary_reports(now=None, site=None,
                                         borg_name=None, **reporting_period):
    """
    spawn an instance of the :func:`email_login_ux_summary` task for a
    `site` and `borg_name`

    :arg str site: if `None`, spawn tasks for all sites

    :arg str borg_name: the short host name of the bot host

        If `None`, spawn a task for each `borg_name` on the `site`.

        Note that it is possible to pick `site` and `borg_name` combinations that
        will result in no data being generated.

        In most cases this `task` is used to spawn an instance of the
        :func:`email_login_ux_summary` task for each `enabled` bot on each
        `enabled` site known to the system.

    :arg now: see :func:`email_dead_borgs_alert`

    :arg dict reporting_period: see the `dead_for` argument of the
        :func:`email_dead_borgs_alert` task

        If this argument is  not present, the reporting interval is picked from
        dynamic preference `User experience reporting period
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=ux_reporting_period>`__

    """
    if not reporting_period:
        time_delta = get_preference('citrusborgux__ux_reporting_period')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**reporting_period)

    sites = BorgSite.objects.filter(enabled=True)
    if site:
        sites = sites.filter(site__iexact=site)
    if not sites.exists():
        return 'site {} does not exist. there is no report to diseminate.'.\
            format(site)
    sites = sites.order_by('site').values_list('site', flat=True)

    site_host_arg_list = []
    for borg_site in sites:
        borg_names = WinlogbeatHost.objects.filter(
            site__site__iexact=borg_site, enabled=True)
        if borg_name:
            borg_names = borg_names.filter(host_name__iexact=borg_name)
        if not borg_names.exists():
            LOGGER.info(
                'there is no bot named %s on site %s. skipping report...',
                borg_name, borg_site)
            continue

        borg_names = borg_names.\
            order_by('host_name').values_list('host_name', flat=True)

        for host_name in borg_names:

            site_host_arg_list.append((borg_site, host_name))

    group(email_login_ux_summary.s(now, time_delta, site_host_args) for
          site_host_args in site_host_arg_list)()

    return 'bootstrapped logon state counts and ux evaluation for {}'.\
        format(site_host_arg_list)


@shared_task(
    queue='borg_chat', rate_limit='3/s', max_retries=3, serializer='pickle',
    retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_login_ux_summary(now, time_delta, site_host_args):
    """
    generate and send a report with login event state counts and user experience
    stats for the site and host combination specified by `site_host_args` over the
    interval defined by `now` and `time_delta`

    :arg tuple site_host_args: the `site` and `host_name`

    :arg datetime.datetime now: the initial moment for calculating the data in
        the report

    :arg datetime.timedelta time_delta: the reporting interval used for calculating
        the data in the report

    :raises: a generic :exc:`Exception`

    This report used the subscription at `Citrix logon event and ux summary
    <../../../admin/ssl_cert_tracker/subscription/?q=Citrix+logon+event+and+ux+summary>`__
    to render the emails being sent.
    """
    try:
        return base_utils.borgs_are_hailing(
            data=login_states_by_site_host_hour(
                now=now, time_delta=time_delta,
                site=site_host_args[0], host_name=site_host_args[1]),
            subscription=base_utils.get_subscription(
                'Citrix logon event and ux summary'),
            logger=LOGGER, time_delta=time_delta,
            site=site_host_args[0], host_name=site_host_args[1])
    except Exception as error:
        raise error


@shared_task(queue='borg_chat')
def email_ux_alarms(now=None, site=None, borg_name=None,  # pylint: disable=too-many-branches
                    send_no_news=None,
                    ux_alert_threshold=None, **reporting_period):
    """
    spawn an instance of the :func:`email_ux_alarm` task for the `site` and
    `borg_name` combination.

    If 'site' and/or `borg_name` are `None`, spawn an instance of the
    :func:`email_ux_alarm` task for each `enabled` `site` and `borg_name` known
    to the system

    :arg str site: if `None`, spawn tasks for all sites

    :arg str borg_name: the short host name of the bot host

        If `None`, spawn a task for each `borg_name` on the `site`.

        Note that it is possible to pick `site` and `borg_name` combinations that
        will result in no data being generated.

        In most cases this `task` is used to spawn an instance of the
        :func:`email_login_ux_summary` task for each `enabled` bot on each
        `enabled` site known to the system.

    :arg now: see :func:`email_dead_borgs_alert`

    :arg bool send_no_news: see :func:`email_dead_borgs_alert`

    :arg datetime.timedelta ux_alert_threshold: the threshold for triggering
        a user experience alert

        By default, this will be retrieved from the dynamic preference
        `Maximum acceptable response time for citrix events
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=ux_alert_threshold>`__

    :arg dict reporting_period: see the `dead_for` argument of the
        :func:`email_dead_borgs_alert` task

        If this argument is  not present, the reporting interval is picked from
        dynamic preference `alert monitoring interval for citrix events
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=ux_alert_interval>`__

    .. todo::

        see `<https://trello.com/c/FeGO5Vqf>`__

    """
    now = base_utils.MomentOfTime.now(now)

    if not reporting_period:
        time_delta = get_preference('citrusborgux__ux_alert_interval')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**reporting_period)

    if send_no_news is None:
        send_no_news = get_preference('citrusborgcommon__send_no_news')

    if not isinstance(send_no_news, bool):
        raise TypeError(
            'object {} type {} is not valid. must be boolean'.
            format(send_no_news, type(send_no_news))
        )

    if ux_alert_threshold is None:
        ux_alert_threshold = get_preference('citrusborgux__ux_alert_threshold')
    else:
        if not isinstance(ux_alert_threshold, dict):
            raise TypeError(
                'object {} type {} is not valid. must be a dictionary'
                ' suitable for datetime.timedelta() arguments'.format(
                    ux_alert_threshold, type(ux_alert_threshold)))

        ux_alert_threshold = base_utils.MomentOfTime.time_delta(
            **ux_alert_threshold)

    sites = BorgSite.objects.filter(enabled=True)
    if site:
        sites = sites.filter(site__iexact=site)
    if not sites.exists():
        return 'site {} does not exist. there is no report to diseminate.'.\
            format(site)
    sites = sites.order_by('site').values_list('site', flat=True)

    site_host_arg_list = []
    for borg_site in sites:
        borg_names = WinlogbeatHost.objects.filter(
            site__site__iexact=borg_site, enabled=True)
        if borg_name:
            borg_names = borg_names.filter(host_name__iexact=borg_name)
        if not borg_names.exists():
            LOGGER.info(
                'there is no bot named %s on site %s. skipping report...',
                borg_name, borg_site)
            continue

        borg_names = borg_names.\
            order_by('host_name').values_list('host_name', flat=True)

        for host_name in borg_names:

            site_host_arg_list.append((borg_site, host_name))

    group(email_ux_alarm.s(now, time_delta, send_no_news,
                           ux_alert_threshold, site_host_args) for
          site_host_args in site_host_arg_list)()

    return 'bootstrapped ux evaluation alarms for {}'.\
        format(site_host_arg_list)


@shared_task(
    queue='borg_chat', rate_limit='3/s', max_retries=3, serializer='pickle',
    retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_ux_alarm(
        now, time_delta, send_no_news, ux_alert_threshold, site_host_args):
    """
    raise user experience alert and send by email for each `site` and `host` in
    `site_host_args`

    :arg tuple site_host_args: `site` and `host_name` to which the alert is bound

    See the :func:`email_us_alarms` task for details about the other arguments.

    This alert used the subscription at `Citrix UX Alert
    <../../../admin/ssl_cert_tracker/subscription/?q=Citrix+UX+Alert>`__.
    """
    now = base_utils.MomentOfTime.now(now)
    site, host_name = site_host_args

    data = raise_ux_alarm(
        now=now, time_delta=time_delta,
        ux_alert_threshold=ux_alert_threshold,
        site=site, host_name=host_name)
    if not data and send_no_news:
        return (
            'Citrix response times on {} bot in {} were better than {} between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(host_name, site, ux_alert_threshold,
                   timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data, subscription=base_utils.get_subscription(
                'Citrix UX Alert'),
            logger=LOGGER, time_delta=time_delta,
            ux_alert_threshold=ux_alert_threshold,
            site=site_host_args[0], host_name=site_host_args[1])
    except Exception as error:
        raise error


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_failed_logins_alarm(now=None, failed_threshold=None, **dead_for):
    """
    raise alert about failed `Citrix` logon events and send it via email

    :arg int failed_threshold: the number of failed logons that will trigger the
        alert

        By default, this will be retrieved from the dynamic preference
        `Failed logon events count alert threshold
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=logon_alert_threshold>`__

    See the :func:`email_dead_borgs_alert` for details about the other arguments.

    This alert used the subscription at `Citrix logon alert
    <../../../admin/ssl_cert_tracker/subscription/?q=Citrix+logon+alert>`__.
    """
    if failed_threshold is None:
        failed_threshold = get_preference(
            'citrusborglogon__logon_alert_threshold')

    if not dead_for:
        time_delta = get_preference('citrusborglogon__logon_alert_after')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    now = base_utils.MomentOfTime.now(now)
    data = raise_failed_logins_alarm(
        now=now, time_delta=time_delta,
        failed_threshold=failed_threshold)

    if not data:
        return (
            'there were less than {} failed logon events between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(failed_threshold, timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data, subscription=base_utils.get_subscription(
                'Citrix logon alert'),
            logger=LOGGER, time_delta=time_delta,
            failed_threshold=failed_threshold)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_failed_logins_report(now=None, send_no_news=False, **dead_for):
    """
    generate and email a report with all the failed `Citrix` logon events

    See the :func:`email_dead_borgs_alert` for details about the arguments to this
    task.

    This report uses the subscription at `Citrix Failed Logins Report
    <../../../admin/ssl_cert_tracker/subscription/?q=Citrix+Failed+Logins+Report>`__.
    """
    if not dead_for:
        time_delta = get_preference('citrusborglogon__logon_report_period')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    now = base_utils.MomentOfTime.now(now)

    data = get_failed_events(now=now, time_delta=time_delta)

    if not data and send_no_news:
        return (
            'there were no failed logon events between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data,
            subscription=base_utils.get_subscription(
                'Citrix Failed Logins Report'),
            logger=LOGGER, time_delta=time_delta)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat', rate_limit='3/s', max_retries=3,
             retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_failed_ux_report(now=None, send_no_news=False,
                           ux_threshold_seconds=None, **dead_for):
    """
    prepare and email a report with all the `Citrix` logon timings that do not
    satisfy the user response time threshold

    :arg now: see :func:`email_dead_borgs_alert`

    :arg bool send_no_news: see :func:`email_dead_borgs_alert`

    :arg datetime.timedelta ux_alert_threshold: the threshold for triggering
        a user experience alert

        By default, this will be retrieved from the dynamic preference
        `Maximum acceptable response time for citrix events
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=ux_alert_threshold>`__

    :arg dict dead_for: see the `dead_for` argument of the
        :func:`email_dead_borgs_alert` task

        If this argument is  not present, the reporting interval is picked from
        dynamic preference `User experience reporting period
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=ux_reporitng_period>`__

    This report uses the subscription at `Citrix Failed UX Event Components Report
    <../../../admin/ssl_cert_tracker/subscription/?q=Citrix+Failed+UX+Event+Components+Report>`__
    to render the emails being sent.
    """
    if not dead_for:
        time_delta = get_preference('citrusborgux__ux_reporting_period')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**dead_for)

    if ux_threshold_seconds is None:
        ux_alert_threshold = get_preference(
            'citrusborgux__ux_alert_threshold')
    else:
        ux_alert_threshold = base_utils.MomentOfTime.time_delta(
            time_delta=None, seconds=ux_threshold_seconds)

    now = base_utils.MomentOfTime.now(now)

    data = get_failed_ux_events(
        now=now, time_delta=time_delta, ux_alert_threshold=ux_alert_threshold)

    if not data and send_no_news:
        return (
            'there were no response time logon event  components'
            ' longer than {:%S} seconds between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(ux_alert_threshold,
                   timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data,
            subscription=base_utils.get_subscription(
                'Citrix Failed UX Event Components Report'),
            logger=LOGGER, time_delta=time_delta,
            ux_alert_threshold=ux_alert_threshold)
    except Exception as error:
        raise error


@shared_task(queue='borg_chat')
def email_failed_login_sites_report(
        now=None, site=None, borg_name=None,
        send_no_news=False, **reporting_period):
    """
    spawn an instance of the :func:`email_failed_login_site_report` task for the
    `site` and `borg_name` combination.

    If `site` and/or `borg_name` are `None`, spawn an instance of the
    :func:`email_ux_alarm` task for each `enabled` `site` and `borg_name` known
    to the system

    :arg str site: if `None`, spawn tasks for all sites

    :arg str borg_name: the short host name of the bot host

        If `None`, spawn a task for each `borg_name` on the `site`.

        Note that it is possible to pick `site` and `borg_name` combinations that
        will result in no data being generated.

        In most cases this `task` is used to spawn an instance of the
        :func:`email_login_ux_summary` task for each `enabled` bot on each
        `enabled` site known to the system.

    :arg now: see :func:`email_dead_borgs_alert`

    :arg bool send_no_news: see :func:`email_dead_borgs_alert`

    :arg dict reporting_period: see the `dead_for` argument of the
        :func:`email_dead_borgs_alert` task

        If this argument is  not present, the reporting interval is picked from
        dynamic preference `Logon events reporting period
        <../../../admin/dynamic_preferences/globalpreferencemodel/?q=logon_report_period>`__

    """
    if not reporting_period:
        time_delta = get_preference('citrusborglogon__logon_report_period')
    else:
        time_delta = base_utils.MomentOfTime.time_delta(**reporting_period)

    sites = BorgSite.objects.filter(enabled=True)
    if site:
        sites = sites.filter(site__iexact=site)
    if not sites.exists():
        return 'site {} does not exist. there is no report to diseminate.'.\
            format(site)
    sites = sites.order_by('site').values_list('site', flat=True)

    site_host_arg_list = []
    for borg_site in sites:
        borg_names = WinlogbeatHost.objects.filter(
            site__site__iexact=borg_site, enabled=True)
        if borg_name:
            borg_names = borg_names.filter(host_name__iexact=borg_name)
        if not borg_names.exists():
            LOGGER.info(
                'there is no bot named %s on site %s. skipping report...',
                borg_name, borg_site)
            continue

        borg_names = borg_names.\
            order_by('host_name').values_list('host_name', flat=True)

        for host_name in borg_names:

            site_host_arg_list.append((borg_site, host_name))

    group(email_failed_login_site_report.s(now, time_delta,
                                           send_no_news, site_host_args) for
          site_host_args in site_host_arg_list)()

    return 'bootstrapped failed login reports for {}'.\
        format(site_host_arg_list)


@shared_task(
    queue='borg_chat', rate_limit='3/s', max_retries=3, serializer='pickle',
    retry_backoff=True, autoretry_for=(SMTPConnectError,))
def email_failed_login_site_report(
        now, time_delta, send_no_news, site_host_args):
    """
    prepare and email a report with the `Citrix` failed logins details for the
    `site` and `bot` combination specified in `site_host_args`

    :arg tuple site_host_args: the `site` and 'bot` for which the report is
        prepared

    :arg now: see :func:`email_dead_borgs_alert`

    :arg bool send_no_news: see :func:`email_dead_borgs_alert`

    :arg dict reporting_period: see the `dead_for` argument of the
        :func:`email_dead_borgs_alert` task

    This report uses the subscription at `Citrix Failed Logins per Report
    <../../../admin/ssl_cert_tracker/subscription/?q=Citrix+Failed+Logins+per+Report>`__
    to render the emails being sent.
    """
    now = base_utils.MomentOfTime.now(now)
    site, host_name = site_host_args

    data = get_failed_events(
        now=now, time_delta=time_delta, site=site, host_name=host_name)
    if not data and send_no_news:
        return (
            'there were no failed logon events on the {} bot in {} between'
            ' {:%a %b %d, %Y %H:%M %Z} and {:%a %b %d, %Y %H:%M %Z}'.
            format(host_name, site, timezone.localtime(value=now),
                   timezone.localtime(now - time_delta))
        )

    try:
        return base_utils.borgs_are_hailing(
            data=data,
            subscription=base_utils.get_subscription(
                'Citrix Failed Logins per Site Report'),
            logger=LOGGER,
            time_delta=time_delta, site=site, host_name=host_name)
    except Exception as error:
        raise error


# pylint: enable=W0703
