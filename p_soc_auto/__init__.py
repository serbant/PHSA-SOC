"""
p_soc_auto
----------

The `Django project
<https://docs.djangoproject.com/en/2.2/intro/tutorial01/#creating-a-project>`__
for the :ref:`SOC Automation Project`

:copyright:

    Copyright 2018 - 2019 Provincial Health Service Authority
    of British Columbia

:contact:    serban.teodorescu@phsa.ca

:updated:    Oct. 29, 2019

"""
from .celery import app as celery_app

__all__ = ('celery_app',)
"""
the `Celery application
<https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html>`__
used by the :ref:`SOC Automation Server`
"""

__version__ = '0.7.6-dev'
"""
the :ref:`SOC Automation Server` version
"""
