# Generated by Django 2.1.4 on 2019-01-24 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssl_cert_tracker', '0018_add_default_port'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sslcertificate',
            options={'verbose_name': 'SSL Certificate (new)', 'verbose_name_plural': 'SSL Certificates (new)'},
        ),
        migrations.AlterField(
            model_name='sslcertificate',
            name='common_name',
            field=models.CharField(blank=True, db_index=True, help_text='SSL certificate commonName field', max_length=253, null=True, verbose_name='common name'),
        ),
        migrations.AlterField(
            model_name='sslcertificateissuer',
            name='common_name',
            field=models.CharField(blank=True, db_index=True, help_text='SSL certificate commonName field', max_length=253, null=True, verbose_name='common name'),
        ),
    ]