from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from transactions.validators import (
    validate_positive_amount,
    validate_non_negative_amount,
    FutureDateValidator,
)


class ValidatorsTestCase(TestCase):
    def test_validate_positive_amount(self):
        # Test positive value
        validate_positive_amount(10)

        # Test zero value
        with self.assertRaises(ValidationError):
            validate_positive_amount(0)

        # Test negative value
        with self.assertRaises(ValidationError):
            validate_positive_amount(-10)

    def test_validate_non_negative_amount(self):
        # Test positive value
        validate_non_negative_amount(10)

        # Test zero value
        validate_non_negative_amount(0)

        # Test negative value
        with self.assertRaises(ValidationError):
            validate_non_negative_amount(-10)

    def test_FutureDateValidator(self):
        # Test future date
        future_date = timezone.now() + timezone.timedelta(days=1)
        FutureDateValidator()(future_date)

        # Test current date
        with self.assertRaises(ValidationError):
            FutureDateValidator()(timezone.now())

        # Test past date
        with self.assertRaises(ValidationError):
            FutureDateValidator()(timezone.now() - timezone.timedelta(days=1))
