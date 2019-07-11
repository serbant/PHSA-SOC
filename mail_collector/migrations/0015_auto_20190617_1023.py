# Generated by Django 2.1.4 on 2019-06-17 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail_collector', '0014_mailbetweendomains_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mailbetweendomains',
            options={'get_latest_by': '-last_verified', 'ordering': ['from_domain', 'to_domain', '-last_verified'], 'verbose_name': 'Domain to Domain Mail Verification', 'verbose_name_plural': 'Domain to Domain Mail Verifications'},
        ),
        migrations.AlterModelOptions(
            name='mailsite',
            options={'get_latest_by': '-winlogbeathost__excgh_last_seen', 'ordering': ['-winlogbeathost__excgh_last_seen'], 'verbose_name': 'Exchange Monitoring Site', 'verbose_name_plural': 'Exchange Monitoring Sites'},
        ),
    ]