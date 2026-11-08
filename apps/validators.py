from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r"^\+?[0-9 ()-]{7,32}$",
    message="Enter a valid phone number using digits and standard separators.",
)
