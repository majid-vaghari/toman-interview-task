from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator

from rest_framework import serializers


def validate_positive_amount(value):
    if value <= 0:
        raise ValidationError(
            _("Positive value required, got %(show_value)s."),
            params={"show_value": value},
        )


validate_non_negative_amount = MinValueValidator(
    0,
    message=_("Non-negative value required, got %(show_value)s.")
)


class FutureDateValidator(MinValueValidator):

    def __init__(self, **time_delta_kwargs):
        timedelta = timezone.timedelta(**time_delta_kwargs)
        if timedelta <= timezone.timedelta(0):
            timedelta = timezone.timedelta(0)
            message = _(
                "Date must be in the future. Got %(show_value)s. Current time: %(limit_value)s.")
        else:
            seconds = timedelta.total_seconds()
            message = _(
                f"Date must be at least {seconds} seconds in the future. "
                "Got %(show_value)s. Current time: %(limit_value)s."
            )
        super().__init__(
            lambda: timezone.now() + timedelta,
            message=message,
        )
