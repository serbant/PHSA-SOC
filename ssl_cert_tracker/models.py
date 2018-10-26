"""
.. _models:

django models for the ssl_certificates app

:module:    ssl_certificates.models

:copyright:

    Copyright 2018 Provincial Health Service Authority
    of British Columbia

:contact:    ali.rahmat@phsa.ca

"""
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from simple_history.models import HistoricalRecords

from p_soc_auto_base.models import BaseModel
from orion_integration.models import OrionNode


class NmapCertsData(BaseModel, models.Model):
    """
    SSL certificate data class

    #TODO: change all xml.dom objects to something readable by humans 
    """
    node_id = models.BigIntegerField(
        'orion node local id', blank=False, null=False, db_index=True,
        help_text='this is the primary keyof the orion node instance as'
        ' defined in the orion_integration application')
    addresses = models.CharField(max_length=100, blank=False, null=False)
    not_before = models.DateTimeField(
        'not before', db_index=True, null=False, blank=False,
        help_text='certificate not valid before this date')
    not_after = models.DateTimeField(
        'not after', db_index=True, null=False, blank=False,
        help_text='certificate not valid after this date')
    xml_data = models.TextField()
    common_name = models.CharField(
        'common name', db_index=True, max_length=100, blank=False, null=False,
        help_text='the CN part of an SSL certificate')
    organization_name = models.CharField(
        'organization', db_index=True, max_length=100, blank=True, null=True,
        help_text='the O part of the SSL certificate')
    country_name = models.CharField(max_length=100, blank=True, null=True)
    sig_algo = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    bits = models.CharField(max_length=100, blank=True, null=True)
    md5 = models.CharField(
        'md5', unique=True, db_index=True, max_length=100, blank=False,
        null=False)
    sha1 = models.CharField(
        'sha1', unique=True, db_index=True, max_length=100, blank=False,
        null=False)
    history = HistoricalRecords()

    @property
    @mark_safe
    def node_admin_url(self):
        """
        admin link to the Orion node where the certificate resides
        """
        orion_node = OrionNode.objects.filter(pk=self.node_id)
        if orion_node.exists():
            orion_node = orion_node.get()
            return '<a href="%s">m%s</>' % (
                reverse('admin:orion_integration_orionnodecategory_change',
                        args=(orion_node.id, )),
                orion_node.node_caption)

        return 'acquired outside the Orion infrastructure'

    @property
    @mark_safe
    def orion_node_url(self):
        """
        link to the Orion Node object on the Orion server
        """
        orion_node = OrionNode.objects.filter(pk=self.node_id)
        if orion_node.exists():
            orion_node = orion_node.get().details_url
            return '<a href="%s/%s' % (settings.ORION_SHORT_URL, orion_node)

        return 'acquired outside the Orion infrastructure'

    def __str__(self):
        return 'O: %s, CN: %s' % (self.organization_name, self.common_name)

    class Meta:
        verbose_name = 'SSL Certificate'
        verbose_name_plural = 'SSL Certificates'
