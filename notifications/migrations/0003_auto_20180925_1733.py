# Generated by Django 2.1.1 on 2018-09-25 17:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_populate_levels'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notification_level',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='notifications.NotificationLevel', verbose_name='Notification Level'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='notifications.NotificationType', verbose_name='Notification Type'),
            preserve_default=False,
        ),
    ]