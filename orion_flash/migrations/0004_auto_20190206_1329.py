# Generated by Django 2.1.4 on 2019-02-06 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orion_flash', '0003_auto_20190204_1052'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpiredSslAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orion_node_id', models.BigIntegerField(db_index=True, help_text='this is the value in this field to SQL join the Orion server database', verbose_name='Orion Node Id')),
                ('orion_node_port', models.BigIntegerField(db_index=True, verbose_name='Orion Node TCP Port')),
                ('cert_url', models.URLField(verbose_name='SSL certificate URL')),
                ('cert_subject', models.TextField(verbose_name='SSL certificate subject')),
                ('first_raised_on', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='alert first raised on')),
                ('last_raised_on', models.DateTimeField(auto_now=True, db_index=True, verbose_name='alert last raised on')),
                ('silenced', models.BooleanField(db_index=True, default=False, help_text='The Orion server will ignore this row when evaluating alert conditions. Note that this flag will be automatically reset every $configurable_interval', verbose_name='alert is silenced')),
                ('alert_body', models.TextField(verbose_name='alert body')),
                ('cert_issuer', models.TextField(verbose_name='SSL certificate issuing authority')),
                ('self_url', models.URLField(blank=True, null=True, verbose_name='Custom SSL alert URL')),
                ('md5', models.CharField(db_index=True, max_length=64, verbose_name='primary key md5 fingerprint')),
                ('not_before', models.DateTimeField(db_index=True, verbose_name='not valid before')),
                ('not_after', models.DateTimeField(db_index=True, verbose_name='expires on')),
                ('has_expired', models.BigIntegerField(db_index=True, verbose_name='has expired')),
            ],
            options={
                'verbose_name': 'Expired SSL Certificates Alert',
                'verbose_name_plural': 'Expired SSL Certificates Alerts',
            },
        ),
        migrations.CreateModel(
            name='ExpiresSoonSslAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orion_node_id', models.BigIntegerField(db_index=True, help_text='this is the value in this field to SQL join the Orion server database', verbose_name='Orion Node Id')),
                ('orion_node_port', models.BigIntegerField(db_index=True, verbose_name='Orion Node TCP Port')),
                ('cert_url', models.URLField(verbose_name='SSL certificate URL')),
                ('cert_subject', models.TextField(verbose_name='SSL certificate subject')),
                ('first_raised_on', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='alert first raised on')),
                ('last_raised_on', models.DateTimeField(auto_now=True, db_index=True, verbose_name='alert last raised on')),
                ('silenced', models.BooleanField(db_index=True, default=False, help_text='The Orion server will ignore this row when evaluating alert conditions. Note that this flag will be automatically reset every $configurable_interval', verbose_name='alert is silenced')),
                ('alert_body', models.TextField(verbose_name='alert body')),
                ('cert_issuer', models.TextField(verbose_name='SSL certificate issuing authority')),
                ('self_url', models.URLField(blank=True, null=True, verbose_name='Custom SSL alert URL')),
                ('md5', models.CharField(db_index=True, max_length=64, verbose_name='primary key md5 fingerprint')),
                ('not_before', models.DateTimeField(db_index=True, verbose_name='not valid before')),
                ('not_after', models.DateTimeField(db_index=True, verbose_name='expires on')),
                ('expires_in', models.BigIntegerField(db_index=True, verbose_name='expires in')),
                ('expires_in_lt', models.BigIntegerField(db_index=True, verbose_name='expires in less than')),
            ],
            options={
                'verbose_name': 'SSL Certificates Expiration Warning',
                'verbose_name_plural': 'SSL Certificates Expiration Warnings',
            },
        ),
        migrations.CreateModel(
            name='InvalidSslAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orion_node_id', models.BigIntegerField(db_index=True, help_text='this is the value in this field to SQL join the Orion server database', verbose_name='Orion Node Id')),
                ('orion_node_port', models.BigIntegerField(db_index=True, verbose_name='Orion Node TCP Port')),
                ('cert_url', models.URLField(verbose_name='SSL certificate URL')),
                ('cert_subject', models.TextField(verbose_name='SSL certificate subject')),
                ('first_raised_on', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='alert first raised on')),
                ('last_raised_on', models.DateTimeField(auto_now=True, db_index=True, verbose_name='alert last raised on')),
                ('silenced', models.BooleanField(db_index=True, default=False, help_text='The Orion server will ignore this row when evaluating alert conditions. Note that this flag will be automatically reset every $configurable_interval', verbose_name='alert is silenced')),
                ('alert_body', models.TextField(verbose_name='alert body')),
                ('cert_issuer', models.TextField(verbose_name='SSL certificate issuing authority')),
                ('self_url', models.URLField(blank=True, null=True, verbose_name='Custom SSL alert URL')),
                ('md5', models.CharField(db_index=True, max_length=64, verbose_name='primary key md5 fingerprint')),
                ('not_before', models.DateTimeField(db_index=True, verbose_name='not valid before')),
                ('not_after', models.DateTimeField(db_index=True, verbose_name='expires on')),
                ('invalid_for', models.BigIntegerField(db_index=True, verbose_name='will become valid in')),
            ],
            options={
                'verbose_name': 'Not Yet Valid SSL Certificates Alert',
                'verbose_name_plural': 'Not Yet Valid SSL Certificates Alert',
            },
        ),
        migrations.CreateModel(
            name='UntrustedSslAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orion_node_id', models.BigIntegerField(db_index=True, help_text='this is the value in this field to SQL join the Orion server database', verbose_name='Orion Node Id')),
                ('orion_node_port', models.BigIntegerField(db_index=True, verbose_name='Orion Node TCP Port')),
                ('cert_url', models.URLField(verbose_name='SSL certificate URL')),
                ('cert_subject', models.TextField(verbose_name='SSL certificate subject')),
                ('first_raised_on', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='alert first raised on')),
                ('last_raised_on', models.DateTimeField(auto_now=True, db_index=True, verbose_name='alert last raised on')),
                ('silenced', models.BooleanField(db_index=True, default=False, help_text='The Orion server will ignore this row when evaluating alert conditions. Note that this flag will be automatically reset every $configurable_interval', verbose_name='alert is silenced')),
                ('alert_body', models.TextField(verbose_name='alert body')),
                ('cert_issuer', models.TextField(verbose_name='SSL certificate issuing authority')),
                ('self_url', models.URLField(blank=True, null=True, verbose_name='Custom SSL alert URL')),
                ('md5', models.CharField(db_index=True, max_length=64, verbose_name='primary key md5 fingerprint')),
                ('not_before', models.DateTimeField(db_index=True, verbose_name='not valid before')),
                ('not_after', models.DateTimeField(db_index=True, verbose_name='expires on')),
                ('cert_is_trusted', models.BooleanField(db_index=True, verbose_name='is trusted')),
            ],
            options={
                'verbose_name': 'Custom Orion Alert for untrusted SSL certificates',
                'verbose_name_plural': 'Custom Orion Alerts for untrusted SSL certificates',
            },
        ),
        migrations.DeleteModel(
            name='SslInvalidAuxAlert',
        ),
        migrations.DeleteModel(
            name='SslUntrustedAuxAlert',
        ),
    ]