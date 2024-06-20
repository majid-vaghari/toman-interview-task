from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator

from rest_framework import serializers


def validate_positive_amount(value):
    if value < 0:
        raise ValidationError(
            _("Positive value required, got %(show_value)s."),
            params={"show_value": value},
        )


validate_non_negative_amount = MinValueValidator(
    0,
    message=_("Non-negative value required, got %(show_value)s.")
)

validate_future_date = MinValueValidator(
    timezone.now,
    message=_(
        "Date must be in the future, got %(show_value)s. Current time: %(limit_value)s.")
)



def validate_sender_and_receiver_are_different(values):
    """
    Validates that the sender and receiver values are different.

    Args:
        values (dict): A dictionary containing the 'sender' and 'receiver' values.

    Raises:
        serializers.ValidationError: If the sender and receiver values are the same.
            This is a custom validation error for the Django Rest Framework serializers.
            It is different from the validation error raised by the `validate_sender_and_receiver_are_different`
            function used in the Django model's `clean` method.

    Returns:
        None
    """
    if values['sender'] == values['receiver']:
        raise serializers.ValidationError(
            _("Sender and receiver cannot be the same.")
        )

