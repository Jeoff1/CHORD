from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r"^\+?[0-9 ()-]{7,32}$",
    message="Enter a valid phone number using digits and standard separators.",
)


def validate_resource_file_size(value):
    """Limit protected worship resources to 10 MiB."""
    if value.size > 10 * 1024 * 1024:
        raise ValidationError("Resource files cannot exceed 10 MiB.")
