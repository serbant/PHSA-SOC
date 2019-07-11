# Generated by Django 2.1.4 on 2019-06-10 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail_collector', '0009_auto_20190606_1436'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeDatabase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('database', models.CharField(db_index=True, max_length=16, unique=True, verbose_name='Database')),
                ('last_access', models.DateTimeField(db_index=True, verbose_name='Last Access')),
            ],
            options={
                'verbose_name': 'Exchange Database',
                'verbose_name_plural': 'Exchange Databases',
                'ordering': ['-last_access'],
                'get_latest_by': '-last_access',
            },
        ),
        migrations.CreateModel(
            name='ExchangeServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange_server', models.CharField(db_index=True, max_length=16, unique=True, verbose_name='Exchange Server')),
                ('last_connection', models.DateTimeField(db_index=True, help_text='Last time an account connected successfully to this server', verbose_name='Last Connected')),
                ('last_send', models.DateTimeField(db_index=True, help_text='Last time a message was send via this server', verbose_name='Last Send')),
                ('last_inbox_access', models.DateTimeField(db_index=True, help_text='Can also be considered as last received', verbose_name='Last Inbox Access')),
                ('last_updated', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Updated')),
            ],
            options={
                'verbose_name': 'Exchange Server',
                'verbose_name_plural': 'Exchange Servers',
                'ordering': ['-last_updated'],
                'get_latest_by': '-last_updated',
            },
        ),
        migrations.AlterModelOptions(
            name='mailbotmessage',
            options={'get_latest_by': '-event__event_registered_on', 'ordering': ['-event__event_group_id', 'sent_from', 'event__event_type_sort'], 'verbose_name': 'Mail Monitoring Message', 'verbose_name_plural': 'Mail Monitoring Messages'},
        ),
        migrations.AddField(
            model_name='exchangedatabase',
            name='exchange_server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mail_collector.ExchangeServer', verbose_name='Exchange Server'),
        ),
    ]