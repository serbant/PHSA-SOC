# Generated by Django 2.1.4 on 2019-07-29 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssl_cert_tracker', '0003_remove_getnmapdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='tags',
            field=models.TextField(blank=True, help_text='email classification tags placed on the subject line and in the email body', null=True, verbose_name='tags'),
        ),
    ]
