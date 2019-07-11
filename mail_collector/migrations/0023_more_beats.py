# Generated by Django 2.1.4 on 2019-07-03 17:55
import pytz

from django.db import migrations


def add_beats(apps, schema_editor):
    timezone = pytz.timezone('America/Vancouver')

    periodic_tasks = [
        {
            'name': ('Raise critical  alert for exchange client bots'),
            'task': 'mail_collector.tasks.bring_out_your_dead',
            'args': (
                '["mail_collector.mailhost","excgh_last_seen__lte",'
                '"Exchange Client Bots Not Seen"]'),
            'kwargs': (
                '{"url_annotate": false,'
                '"level": "CRITICAL",'
                '"filter_pref": "exchange__bot_error","enabled": true}'),
            'interval': {
                'every': 30,
                'period': 'minutes',
            },
        },
        {
            'name': ('Raise warning  alert for exchange client bots'),
            'task': 'mail_collector.tasks.bring_out_your_dead',
            'args': (
                '["mail_collector.mailhost","excgh_last_seen__lte",'
                '"Exchange Client Bots Not Seen"]'),
            'kwargs': (
                '{"url_annotate": false,'
                '"level": "WARNING",'
                '"filter_pref": "exchange__bot_warn","enabled": true}'),
            'interval': {
                'every': 30,
                'period': 'minutes',
            },
        },
        {
            'name': ('Raise warning  alert for exchange client sites'),
            'task': 'mail_collector.tasks.dead_mail_sites',
            'args': '["Exchange Client Bot Sites Not Seen"]',
            'kwargs': (
                '{"level": "WARNING",'
                '"time_delta_pref": "exchange__bot_warn"}'),
            'interval': {
                'every': 30,
                'period': 'minutes',
            },
        },
        {
            'name': ('Raise critical  alert for exchange client sites'),
            'task': 'mail_collector.tasks.dead_mail_sites',
            'args': (
                '["Exchange Client Bot Sites Not Seen"]'),
            'kwargs': (
                '{"level": "CRITICAL",'
                '"time_delta_pref": "exchange__bot_error"}'),
            'interval': {
                'every': 30,
                'period': 'minutes',
            },
        },

        {
            'name': ('Raise critical  alert for email not checked'),
            'task': 'mail_collector.tasks.bring_out_your_dead',
            'args': (
                '["mail_collector.mailbetweendomains","last_verified__lte",'
                '"Mail Unchecked On Site"]'),
            'kwargs': (
                '{"url_annotate": false,'
                '"level": "CRITICAL",'
                '"filter_pref": "exchange__bot_error","enabled": true, "is_expired": false}'),
            'interval': {
                'every': 30,
                'period': 'minutes',
            },
        },
        {
            'name': ('Raise critical  alert for email check failure'),
            'task': 'mail_collector.tasks.bring_out_your_dead',
            'args': (
                '["mail_collector.mailbetweendomains","last_verified__lte",'
                '"Mail Verification Failed"]'),
            'kwargs': (
                '{"url_annotate": false,'
                '"level": "CRITICAL",'
                '"filter_pref": "exchange__nil_duration","enabled": true, "is_expired": false, "status": "Failed"}'),
            'interval': {
                'every': 30,
                'period': 'minutes',
            },
        },
    ]

    cron_tasks = [


        {
            'name': ('Exchange verification report'),
            'task': 'mail_collector.tasks.bring_out_your_dead',
            'args': (
                '["mail_collector.mailbetweendomains","last_verified__gte",'
                '"Mail Unchecked On Site"]'),
            'kwargs': (
                '{"url_annotate": true,'
                '"level": null,'
                '"filter_pref": "exchange__report_interval","enabled": true, "is_expired": false}'),
            'crontab': {
                'minute': '45',
                'hour': '07,15,23',
                'day_of_week': '*',
                'day_of_month': '*',
                'month_of_year': '*',
                'timezone': timezone,
            },
        },

    ]

    CrontabSchedule = apps.get_model('django_celery_beat', 'CrontabSchedule')
    IntervalSchedule = apps.get_model(
        'django_celery_beat', 'IntervalSchedule')
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')

    for _task in cron_tasks:
        cron, _ = CrontabSchedule.objects.get_or_create(**_task['crontab'])

        _task['crontab'] = cron

        PeriodicTask.objects.create(**_task)

    for _task in periodic_tasks:
        interval, _ = IntervalSchedule.objects.get_or_create(
            **_task['interval'])

        _task['interval'] = interval

        PeriodicTask.objects.create(**_task)


class Migration(migrations.Migration):

    dependencies = [
        ('mail_collector', '0022_add_subs_bot_site'),
    ]

    operations = [
        migrations.RunPython(add_beats,
                             reverse_code=migrations.RunPython.noop)
    ]