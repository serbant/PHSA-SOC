"""
ssl_cert_tracker.models
-----------------------

This module contains the :class:`models <django.db.models.Model>` and :class:`model
managers <django.db.models.Manager>` used by the :ref:`SSL Certificate Tracker
Application`.

:copyright:

    Copyright 2018 - 2019 Provincial Health Service Authority
    of British Columbia

:contact:    serban.teodorescu@phsa.ca

"""
import socket

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from citrus_borg.dynamic_preferences_registry import get_preference
from orion_integration.models import OrionNode
from p_soc_auto_base.models import BaseModel

from .lib import expires_in, has_expired, is_not_yet_valid


# pylint: disable=too-few-public-methods, no-self-use


class ExpiresIn(models.Manager):
    """
    `Custom manager
    <https://docs.djangoproject.com/en/2.2/topics/db/managers/#custom-managers>`_
    class used in the :class:`SslExpiresIn` model
    """

    def get_queryset(self):
        """
        override :meth:`django.db.models.Manager.get_queryset`

        See `Modifying a manager's initial QuerySet
        <https://docs.djangoproject.com/en/2.2/topics/db/managers/#modifying-a-manager-s-initial-queryset>`__
        in the `Django` docs.
        """
        return expires_in()


class ExpiredSince(models.Manager):
    """
    `Custom manager
    <https://docs.djangoproject.com/en/2.2/topics/db/managers/#custom-managers>`_
    class used in the :class:`SslHasExpired` model
    """

    def get_queryset(self):
        """
        override :meth:`django.db.models.Manager.get_queryset`

        See `Modifying a manager's initial QuerySet
        <https://docs.djangoproject.com/en/2.2/topics/db/managers/#modifying-a-manager-s-initial-queryset>`__
        in the `Django` docs.
        """
        return has_expired()


class NotYetValid(models.Manager):
    """
    `Custom manager
    <https://docs.djangoproject.com/en/2.2/topics/db/managers/#custom-managers>`_
    class used in the :class:`SslNotYetValid` model
    """

    def get_queryset(self):
        """
        override :meth:`django.db.models.Manager.get_queryset`

        See `Modifying a manager's initial QuerySet
        <https://docs.djangoproject.com/en/2.2/topics/db/managers/#modifying-a-manager-s-initial-queryset>`__
        in the `Django` docs.
        """
        return is_not_yet_valid()

# pylint: enable=too-few-public-methods, no-self-use


class SslCertificateBase(BaseModel, models.Model):
    """
    `Abstract base
    <https://docs.djangoproject.com/en/2.2/topics/db/models/#abstract-base-classes>`__
    :class:`django.db.models.Model` used by some
    :class:`models <django.db.models.Model>` in this module
    """
    common_name = models.CharField(
        _('common name'), db_index=True, max_length=253, blank=True,
        null=True, help_text=_('SSL certificate commonName field'))
    organization_name = models.CharField(
        _('organization name'), db_index=True, max_length=253, blank=True,
        null=True, help_text=_('SSL certificate organizationName field'))
    country_name = models.CharField(
        _('country name'), db_index=True, max_length=2, blank=True, null=True,
        help_text=_('SSL certificate countryName field'))

    class Meta:
        abstract = True


class SslProbePort(BaseModel, models.Model):
    """
    :class:`django.db.models.Model` class used for storing network port
    information in the database

    Under normal use, only `enabled` instances of this `model` are used for
    running `NMAP <https://nmap.org/>`__ `SSL server certificates
    <https://en.wikipedia.org/wiki/Public_key_certificate#TLS/SSL_server_certificate>`__
    scans.

    `Network Port fields
    <../../../admin/doc/models/ssl_cert_tracker.sslprobeport/>`__
    """
    port = models.PositiveIntegerField(
        _('port'), unique=True, db_index=True, blank=False, null=False)

    def __str__(self):
        return '%s' % self.port

    class Meta:
        app_label = 'ssl_cert_tracker'
        verbose_name = _('Network Port')
        verbose_name_plural = _('Network Ports')


class SslCertificateIssuer(SslCertificateBase, models.Model):
    """
    :class:`django.db.models.Model` class used for storing information about the
    `Certificate authorities
    <https://en.wikipedia.org/wiki/Public_key_certificate#Certificate_authorities>`__
    that have issued known :class:`SSL Certificates <SslCertificate>`

    `Issuing Authority for SSL Certificates fields
    <../../../admin/doc/models/ssl_cert_tracker.sslcertificateissuer>`__
    """
    is_trusted = models.BooleanField(
        _('is trusted'), db_index=True, default=False, null=False, blank=False,
        help_text=_('is this a known SSL issuing authority'
                    ' (like Verisign or DigiCert)?'))

    @classmethod
    def get_or_create(
            cls, ssl_issuer, username=settings.NMAP_SERVICE_USER):
        """
        create (if it doesn't exist already) and retrieve a
        :class:`SslCertificateIssuer` instance

        :arg dict ssl_issuer:

            data about the `Certificate authority
            <https://en.wikipedia.org/wiki/Public_key_certificate#Certificate_authorities>`__

        :arg str username:

            the key for the :class:`django.contrib.auth.models.User` (or its
            `replacement
            <https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#substituting-a-custom-user-model>`__)
            instance representing the user that is maintaining the
            :class:`SslCertificateIssuer` instance

            By default, this value is picked from
            :attr:`p_soc_auto.settings.NMAP_SERVICE_USER` and if that user doesn't
            exit, it will be created.

        :returns: a :class:`SslCertificateIssuer` instance
        """
        ssl_certificate_issuer = cls._meta.model.objects.\
            filter(common_name__iexact=ssl_issuer.get('commonName'))
        if ssl_certificate_issuer.exists():
            return ssl_certificate_issuer.get()

        user = cls.get_or_create_user(username)
        ssl_certificate_issuer = cls(
            common_name=ssl_issuer.get('commonName'),
            organization_name=ssl_issuer.get('organizationName'),
            country_name=ssl_issuer.get('countryName'),
            created_by=user, updated_by=user)
        ssl_certificate_issuer.save()

        return ssl_certificate_issuer

    def __str__(self):
        return 'commonName: %s, organizationName: %s' % \
            (self.common_name, self.organization_name)

    class Meta:
        app_label = 'ssl_cert_tracker'
        verbose_name = _('Issuing Authority for SSL Certificates')
        verbose_name_plural = _('Issuing Authorities for SSL Certificates')


class SslCertificate(SslCertificateBase, models.Model):
    """
    :class:`django.db.models.Model` class used for storing information about
    `SSL server certificates
    <https://en.wikipedia.org/wiki/Public_key_certificate#TLS/SSL_server_certificate>`_

    `SSL Certificate fields
    <../../../admin/doc/models/ssl_cert_tracker.sslcertificate>`__

    """
    orion_id = models.BigIntegerField(
        _('orion node identifier'), blank=False, null=False, db_index=True,
        help_text=_('Orion Node unique identifier  on the Orion server'
                    ' used to show the node in the Orion web console'))
    port = models.ForeignKey(
        SslProbePort, db_index=True, blank=False, null=False,
        verbose_name=_('TCP port'), on_delete=models.PROTECT)
    issuer = models.ForeignKey(
        SslCertificateIssuer, db_index=True, blank=True, null=True,
        verbose_name=_('Issued By'), on_delete=models.PROTECT)
    hostnames = models.TextField(_('host names'), blank=False, null=False)
    not_before = models.DateTimeField(
        _('not valid before'), db_index=True, null=False, blank=False)
    not_after = models.DateTimeField(
        _('expires on'), db_index=True, null=False, blank=False)
    pem = models.TextField(_('PEM'), null=False, blank=False)
    pk_bits = models.CharField(
        _('private key bits'), max_length=4, db_index=True,
        blank=False, null=False)
    pk_type = models.CharField(
        _('primary key type'), max_length=4, db_index=True,
        blank=False, null=False)
    pk_md5 = models.CharField(
        _('primary key md5 fingerprint'), db_index=True,
        max_length=64, blank=False, null=False)
    pk_sha1 = models.TextField(
        _('primary key sha1 fingerprint'), blank=False, null=False)
    last_seen = models.DateTimeField(
        _('last seen'), db_index=True, blank=False, null=False)

    def __str__(self):
        return (
            'CN: {}, O: {}, c: {}'
        ).format(
            self.common_name, self.organization_name, self.country_name)

    @classmethod
    def create_or_update(cls, orion_id, ssl_certificate,
                         username=settings.NMAP_SERVICE_USER):
        """
        create or update a :class:`SslCertificate` instance

        Currently, we are uniquely identifying an `SSL` certificate by the
        ('network address', 'network port') tuple where the certificate is being
        served. This approach is fully justified from an operational perspective;
        it is not possible to serve more than one certificate per the network
        tuple.

        However, a (valid) SSL certificate is an ephemeral construct. When it
        expires, it cannot be extended. It can only be replaced by a new `SSL`
        certificate. This method needs to be able to detect such a change and
        handle the instance update accordingly.

        In this method, we look for the network tuple in the underlying table:

        * if not found, this is a new `SSL` certificate, the method creates a
          new :class:`SslCertificate` instance

        * if found, compare the `MD5 <https://en.wikipedia.org/wiki/MD5>`_
          checksum already present in the :class:`SslCertificate` instance as
          :attr:`pk_md5` with the one present in the :attr:`ssl_md5` attribute
          of the `ssl_certificate` argument

          * if the `MD5` values match, the whole `SSL` certificate matches; the
            mehtod will only update the :attr:`SslCertificate.last_seen` field

          * if the `MD5` values don't match, this is a new `SSL` certificate; the
            method will update all the fields in the :class:`SslCertificate`
            instance

        :Note:

            In :class:`SslCetificate`, the network address is hiding behind the
            :attr:`SslCertificate.orion_id` which is a
            :class:`django.db.models.ForeignKey` to
            :class:`orion_integration.models.OrionNode`.

        :arg int orion_id: the reference to the
            :class:`orion_integration.models.OrionNode` instance for the
            network node from where the `SSL` certificate is served

        :arg ssl_certificate: all the data collected by the `NMAP
            <https://nmap.org/>`_ scan
        :type ssl_certificate: :class:`ssl_cert_tracker.nmap.SslProbe`

        :arg str username: the :attr:`django.contrib.auth.models.User.username`
            of the user (or its
            `replacement
            <https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#substituting-a-custom-user-model>`__)
            maintaining the :class:`SslCertificate` instance

            The default value is picked from
            :attr:`p_soc_auto.settings.NMAP_SERVICE_USER`. If a matching
            :class:`django.contrib.auth.models.User` instance doesn't exist, one
            will be created.
        """
        user = cls.get_or_create_user(username)
        issuer = SslCertificateIssuer.get_or_create(
            ssl_certificate.ssl_issuer, username)

        ssl_obj = cls._meta.model.objects.filter(
            orion_id=orion_id, port__port=ssl_certificate.port)

        if ssl_obj.exists():
            ssl_obj = ssl_obj.get()
            if ssl_obj.pk_md5 != ssl_certificate.ssl_md5:
                """
                host and port are the same but the checksum has changed,
                ergo the certificate has been replaced. we need to save
                the new data
                """
                ssl_obj.common_name = ssl_certificate.ssl_subject.\
                    get('commonName')
                ssl_obj.organization_name = ssl_certificate.ssl_subject.\
                    get('organizationName')
                ssl_obj.country_name = ssl_certificate.ssl_subject.\
                    get('countryName')
                ssl_obj.issuer = issuer
                ssl_obj.hostnames = ssl_certificate.hostnames
                ssl_obj.not_before = ssl_certificate.ssl_not_before
                ssl_obj.not_after = ssl_certificate.ssl_not_after
                ssl_obj.pem = ssl_certificate.ssl_pem
                ssl_obj.pk_bits = ssl_certificate.ssl_pk_bits
                ssl_obj.pk_type = ssl_certificate.ssl_pk_type
                ssl_obj.pk_md5 = ssl_certificate.ssl_md5
                ssl_obj.pk_sha1 = ssl_certificate.ssl_sha1
                ssl_obj.updated_by = user

            ssl_obj.last_seen = timezone.now()
            ssl_obj.save()

            return False, ssl_obj

        port = SslProbePort.objects.get(port=int(ssl_certificate.port))
        ssl_obj = cls(
            common_name=ssl_certificate.ssl_subject.get('commonName'),
            organization_name=ssl_certificate.ssl_subject.get(
                'organizationName'),
            country_name=ssl_certificate.ssl_subject.get('countryName'),
            orion_id=orion_id, port=port, issuer=issuer,
            hostnames=ssl_certificate.hostnames,
            not_before=ssl_certificate.ssl_not_before,
            not_after=ssl_certificate.ssl_not_after,
            pem=ssl_certificate.ssl_pem, pk_bits=ssl_certificate.ssl_pk_bits,
            pk_type=ssl_certificate.ssl_pk_type,
            pk_md5=ssl_certificate.ssl_md5, pk_sha1=ssl_certificate.ssl_sha1,
            created_by=user, updated_by=user, last_seen=timezone.now())
        ssl_obj.save()

        return True, ssl_obj

    @property
    @mark_safe
    def node_admin_url(self):
        """
        absolute `URL` for the `Django admin change`
        :class:`django.contrib.admin.ModelAmin` form for the
        :class:`orion_integration.models.OrionNode` instance of the network node
        that is serving this `SSL` certificate
        """
        orion_node = OrionNode.objects.filter(orion_id=self.orion_id)
        if orion_node.exists():
            orion_node = orion_node.get()
            return '<a href="%s">%s on django</>' % (
                reverse('admin:orion_integration_orionnode_change',
                        args=(orion_node.id,)),
                orion_node.node_caption)

        return 'acquired outside the Orion infrastructure'

    @property
    @mark_safe
    def absolute_url(self):
        """
        absolute `URL` for the `Django admin change`
        :class:`django.contrib.admin.ModelAmin` form for this
        :class:`SslCertificate` instance
        """
        return '<a href="{proto}://{host}:{port}/{path}'.format(
            proto=settings.SERVER_PROTO, host=socket.getfqdn(),
            port=settings.SERVER_PROTO,
            path=reverse('admin:ssl_cert_tracker_sslcertificate_change',
                         args=(self.id,)))

    @property
    @mark_safe
    def orion_node_url(self):
        """
        absolute `SolarWinds Orion <https://www.solarwinds.com/solutions/orion>`__
        `URL` for the network node serving this :class:`SslCertificate` instance
        """
        orion_node = OrionNode.objects.filter(orion_id=self.orion_id)
        if orion_node.exists():
            orion_node = orion_node.values('node_caption', 'details_url')[0]
            return '<a href="%s%s">%s on Orion</>' % (
                get_preference('orionserverconn__orion_server_url'),
                orion_node.get('details_url'), orion_node.get('node_caption')
            )

        return 'acquired outside the Orion infrastructure'

    class Meta:
        app_label = 'ssl_cert_tracker'
        verbose_name = _('SSL Certificate')
        verbose_name_plural = _('SSL Certificates')
        unique_together = (('orion_id', 'port'),)


class SslExpiresIn(SslCertificate):
    """
    `Proxy model
    <https://docs.djangoproject.com/en/2.2/topics/db/models/#proxy-models>`__
    for :class:`SslCertificate`

    Show valid `SSL` certificates sorted by expiration date.
    """
    objects = ExpiresIn()

    class Meta:
        proxy = True
        verbose_name = 'Valid SSL Certificate'
        verbose_name_plural = 'Valid SSL Certificates by expiration date'


class SslHasExpired(SslCertificate):
    """
    `Proxy model
    <https://docs.djangoproject.com/en/2.2/topics/db/models/#proxy-models>`__
    for :class:`SslCertificate`

    Show expired `SSL` certificates sorted by expiration date.
    """
    objects = ExpiredSince()

    class Meta:
        proxy = True
        verbose_name = 'SSL Certificate: expired'
        verbose_name_plural = 'SSL Certificates: expired'


class SslNotYetValid(SslCertificate):
    """
    `Proxy model
    <https://docs.djangoproject.com/en/2.2/topics/db/models/#proxy-models>`__
    for :class:`SslCertificate`

    Show not yet valid `SSL` certificates sorted by the `Not before` date.
   """
    objects = NotYetValid()

    class Meta:
        proxy = True
        verbose_name = 'SSL Certificate: not yet valid'
        verbose_name_plural = 'SSL Certificates: not yet valid'


class Subscription(BaseModel):
    """
    Data model with all the details required to create and send an email
    message

    This :class:`django.db.models.Model` is used across all the applications
    running on the :ref:`SOC Automation Server`.
    """
    subscription = models.CharField(
        'subscription', max_length=64, unique=True, db_index=True, blank=False,
        null=False)
    """
    string uniquely identifying a :class:`Subscription` instance
    """

    emails_list = models.TextField('subscribers', blank=False, null=False)
    """
    comma-separated string with the email addresses to which the email will be
    sent
    """

    from_email = models.CharField(
        'from', max_length=255, blank=True, null=True,
        default=settings.DEFAULT_FROM_EMAIL)
    """
    email address to be placed in the `FROM` email header; default will be
    picked from :attr:`p_soc_auto.settings.DEFAULT_FROM_EMAIL`
    """

    template_dir = models.CharField(
        'email templates directory', max_length=255, blank=False, null=False)
    """
    directory for `Templates
    <https://docs.djangoproject.com/en/2.2/topics/templates/>`_

    In most cases this is an `application_directory/templates/` directory.
    """

    template_name = models.CharField(
        'email template name', max_length=64, blank=False, null=False)
    """
    the short name of the template file used to render this type of email

    The extension is picked from the configuration of the
    `django-templated-mail` package in `p_soc_auto.settings`.
    """

    template_prefix = models.CharField(
        'email template prefix', max_length=64, blank=False, null=False,
        default='email/')
    """
    the subdirectory under :attr:`templatedir` where email templates are
    located
    """

    email_subject = models.TextField(
        'email subject fragment', blank=True, null=True,
        help_text=('this is the conditional subject of the email template.'
                   ' it is normally just a fragment that will augmented'
                   ' by other variables'))
    """
    the strings to be used as the core of the email subject line

    The application will most probably pre-pend and/or append various other
    strings to the subject line.

    There is no limit on the length of the subject line but in this application
    but according to `RFC 2822
    <http://www.faqs.org/rfcs/rfc2822.html>`_, section 2.1.1, this field must
    not be longer than 998 characters, and should not be longer than
    78 characters (we are nowhere near respecting the later).

    This value is used as an email subject line only if the rendering template
    is invoked with a `context
    <https://docs.djangoproject.com/en/2.2/ref/templates/api/#rendering-a-context>`_
    that includes a reference to it.
    """

    alternate_email_subject = models.TextField(
        'fallback email subject', blank=True, null=True,
        help_text='this is the non conditional subject of the email template.')
    """
    an alternate value for the core of the email subject line

    This value is subject to the same rules as :attr:`email_subject`.

    We include this value because in some cases the same template will render
    with different subject lines based on various conditions. E.g. if the
    :attr:`data is not ``None``, the subject line will include some references
    to the its content, otherwise the subject line would be like 'Move along,
    nothing to see here'.
    """

    headers = models.TextField(
        'data headers', blank=False, null=False,
        default='common_name,expires_in,not_before,not_after')
    """
    a comma-separated list of field names to retrieve from the :attr:`data`
    `queryset`

    Note that if there are field names listed here that don't exist in the
    :attr:`data` `queryset`.

    """

    tags = models.TextField(
        'tags', blank=True, null=True,
        help_text=('email classification tags placed on the subject line'
                   ' and in the email body'))
    """
    a string af tags that will be pre-pended to the email subject line
    
    The application will not do any processing on this value. If one expects
    tags to look like[TAG1][TAG2], this value must be created using this
    pattern.
    """

    def __str__(self):
        return self.subscription

    class Meta:
        app_label = 'ssl_cert_tracker'
