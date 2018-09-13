# Generated by Django 2.0.7 on 2018-08-30 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules_engine', '0002_auto_20180827_1750'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='regexrule',
            options={'verbose_name': 'String Match Rule', 'verbose_name_plural': 'String Match Rules'},
        ),
        migrations.AlterField(
            model_name='notificationeventforruledemo',
            name='updated_on',
            field=models.DateTimeField(auto_now=True, db_index=True, help_text='object update time stamp', verbose_name='updated on'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='updated_on',
            field=models.DateTimeField(auto_now=True, db_index=True, help_text='object update time stamp', verbose_name='updated on'),
        ),
        migrations.AlterField(
            model_name='ruleapplies',
            name='updated_on',
            field=models.DateTimeField(auto_now=True, db_index=True, help_text='object update time stamp', verbose_name='updated on'),
        ),
        migrations.AlterField(
            model_name='tindataforruledemos',
            name='updated_on',
            field=models.DateTimeField(auto_now=True, db_index=True, help_text='object update time stamp', verbose_name='updated on'),
        ),
    ]