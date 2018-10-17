"""
.. _utils:

utility  functions for the notification tasks

:module:    p_soc_auto.notification.utils

:copyright:

    Copyright 2018 Provincial Health Service Authority
    of British Columbia

:contact:    ali.rahmat@phsa.ca

:update:    Oct. 04 2018

"""
import logging
from django.utils import timezone
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Notification

class EmailBroadCast(EmailMessage):
    """
    EmailBroadCast class to Broadcast Email
    This class instanciated either by a third party or
    from signals.py through celery tasks worker
    """

    def __init__(self,
                 subject=settings.DEFAULT_EMAIL_SUBJECT,
                 message=settings.DEFAULT_EMAIL_MESSAGE,
                 email_from=settings.ADMINS[0][1],
                 email_to=[settings.ADMINS[1][1],
                           settings.ADMINS[2][1]],
                 cc=settings.DEFAULT_EMAIL_CC,
                 bcc=settings.DEFAULT_EMAIL_BCC,
                 connection=settings.DEFAULT_EMAIL_CONNECTION,
                 attachments=settings.DEFAULT_EMAIL_ATTACHMENTS,
                 reply_to=settings.DEFAULT_EMAIL_REPLY_TO, 
                 headers=settings.DEFAULT_EMAIL_HEADERS,
                 notification_pk=settings.DEFAULT_NOTIFICATION_PK,
                 email_type=settings.DEFAULT_EMAIL_TYPE,
                 *args,
                 **kwargs
                ):

        """
        All default parameters are comming from settings.py        
        """
        self.obj = None
        if connection is not None:
            self.notification_pk = notification_pk              
            if Notification.objects.filter(
                pk=self.notification_pk).exists():
                self.obj = Notification.objects.get(
                    pk=self.notification_pk)
                subject=self.obj.rule_msg
                message=self.obj.message
                if email_type == 0
                    email_to = self.obj.subscribers
                elif email_type == 1: # escalation
                    #email_to = self.obj.escalation
                    pass
                elif email_type == 2: # both esc, and broadcast
                    #email_to.
                    #        extend(self.obj.subscribers).
                    #        extend(self.obj.escalation)
                    pass
                else: # error
                    pass
            else:
                logger.debug('Invalid  object %s', 'Notification')
                return



        # if notification_pk is not None:
        #     if subject is None:
        #         logger.debug('Invalid None parameter %s',
        #         'Email Subject')
        #         return
        #     if message is None:
        #         logger.debug('Invalid None parameter %s',
        #         'Email Message')
        #         return

        if notification_pk is None:
            if subject is None:
                logger.debug('Invalid None parameter %s', 'Email Subject')
                return
            if message is None:
                logger.debug('Invalid None parameter %s', 'Email Message')
                return

            try:
                validate_email( email_from )
            except ValidationError:
                logger.debug('Invalid Email %s', 'Email From')
                return

            if not isinstance(email_to,(list,)):  
                logger.debug('Not a list instance %s', 'Email To')
                return
            elif email_to is []:
                logger.debug('Invalid Email %s', 'Email To')
                return
            else:
                for em in email_to:
                    try:
                        validate_email( em )
                    except ValidationError:
                        logger.debug('Invalid Email %s', 'Email To')
                        return

            if not isinstance(cc,(list,)):  
                logger.debug('Not a list instance %s', 'cc')
                return

            if not isinstance(bcc,(list,)):  
                logger.debug('Not a list instance %s', 'cc')
                return
            
            if not isinstance(attachments,(list,)):  
                logger.debug('Not a list instance %s', 'attachments')
                return

            if not isinstance(reply_to,(list,)):  
                logger.debug('Not a list instance %s', 'Reply To')
                return
            elif reply_to is []:
                logger.debug('Invalid Email %s', 'Reply To')
                return
            else:
                for em in reply_to:
                    try:
                        validate_email( em )
                    except ValidationError:
                        logger.debug('Invalid Email %s', 'Reply To')
                        return


        super().__init__(subject,
                         message,
                         email_from,
                         email_to,
                         bcc,
                         connection,
                         attachments,
                         cc,
                         reply_to,
                         headers,
                         *args, **kwargs)

    def post_send_mail_update(self):
        '''
        extend this to include the whole send and update logic
        
        update notification columns upon successful email sent
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return days, hours, minutes, seconds
        '''

        Notification.objects.filter(pk=self.notification_pk).update(
            broadcast_on=timezone.now())
        # we need to update escalated_on if no one paid
        #attension to email within
        # timezone.timedelta(instance.notification_type.escalate_within)


        # Notification.objects.filter(pk=self.notification_pk).update(
        #     escalated_on=timezone.now() +
        #     timezone.timedelta(instance.notification_type.escalate_within))

