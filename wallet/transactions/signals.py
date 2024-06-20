import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Transaction
from .tasks import process_withdrawal

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transaction)
def schedule_withdrawal(sender, instance: Transaction, created, **kwargs):

    logger.debug('Scheduling withdrawal for transaction %s', instance)

    if created and instance.status == Transaction.Status.PENDING:
        process_withdrawal.apply_async_on_commit(
            (instance.uuid,),
            eta=instance.scheduled_time,
        )
