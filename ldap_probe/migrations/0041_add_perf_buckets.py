# Generated by Django 2.2.6 on 2019-12-27 21:43
import decimal

from django.contrib.auth.models import User, UserManager
from django.db import migrations


def add_perf_buckets(apps, schema_editor):
    PerfBucket = apps.get_model('ldap_probe', 'ADNodePerfBucket')

    user = User.objects.filter(is_superuser=True)
    if user.exists():
        user = user.first()
    else:
        user = User.objects.create(
            username='soc_su', email='soc_su@phsa.ca',
            password='soc_su_password', is_active=True, is_staff=True,
            is_superuser=True)
        user.set_password('soc_su_password')
        user.save()

    user_dict = {'created_by_id': user.id,
                 'updated_by_id': user.id, }

    perf_buckets = [
        {'location': 'ARHCC',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Bella Bella',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Bella Coola',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Broadway',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'BUH',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Burnaby Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'C&W K0-160',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'CCP - Central City Podium',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Chilliwack General Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Delta Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Eagle Ridge Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'FHA',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'FCH - Virtual Center - RCH Cluster',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'IHA',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'IHA-IBM',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Island Health',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'JPN3',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'JPOCSC',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'KDC',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'KDC _ Virtual Center',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Langley Memorial Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': "Lion's Gate Hospital",
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Mission Memorial Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Cerner RHO Data Center',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': 'Ontario',
         'is_default': False,
         },
        {'location': 'Cerner RHO Q9 Data Center',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': 'Ontario',
         'is_default': False,
         },
        {'location': 'Cerner RHO SunGuard Data Center',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': 'Ontario',
         'is_default': False,
         },
        {'location': 'NHA',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'NHA-NE',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'NHA_NW',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Oak',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Peace Arch Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'PHSA',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'PHSA - Virtual Center',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'RCH',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'RH',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Ridge Meadows Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'SMH',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'SOCSC-Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Squamish',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'SSF',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': "St. Mary's Hospital Sechelt",
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': "St. Paul's Hospital",
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': "St. Paul's Hospital - Lab room",
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Support-Services-Facility',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Surrey-Memorial-Hospital',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Telus -TDC',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Telus - TDC1',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'Vancouver Cancer Center',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'VCH-PHC',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
        {'location': 'VIHA',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': '',
         'is_default': False,
         },
    ]

    for perf_bucket in perf_buckets:
        perf_bucket.update(user_dict)
        new_perf_bucket = PerfBucket(**perf_bucket)
        new_perf_bucket.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ldap_probe', '0040_beats_new_perf_reports'),
    ]

    operations = [
        migrations.RunPython(add_perf_buckets,
                             reverse_code=migrations.RunPython.noop)
    ]
