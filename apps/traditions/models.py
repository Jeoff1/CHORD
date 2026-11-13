from django.conf import settings
from django.db import models


class Tradition(models.Model):
    """A Christian tradition preset that configures CHORD (see GLOSSARY.md)."""

    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    terminology = models.JSONField(default=dict, blank=True)
    default_modules = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ChurchProfile(models.Model):
    """The single record describing this installation's church."""

    SINGLETON_ID = 1

    name = models.CharField(max_length=150, default="My Church")
    tradition = models.ForeignKey(
        Tradition, on_delete=models.PROTECT, related_name="church_profiles"
    )
    module_overrides = models.JSONField(
        default=dict,
        blank=True,
        help_text="Module code to enabled flag, where it differs from the preset.",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        permissions = [("manage_church_profile", "Can manage the church profile")]

    def save(self, *args, **kwargs):
        self.pk = self.SINGLETON_ID
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ThemeQuerySet(models.QuerySet):
    def available_for(self, tradition):
        """The common Themes plus ``tradition``'s own Themes."""
        return self.filter(
            models.Q(tradition__isnull=True) | models.Q(tradition=tradition)
        )


class Theme(models.Model):
    """A controlled-vocabulary topic; common when it has no Tradition (see GLOSSARY.md)."""

    code = models.SlugField(max_length=50)
    name = models.CharField(max_length=100)
    tradition = models.ForeignKey(
        Tradition,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="themes",
        help_text="Leave blank for a common Theme shared by every Tradition.",
    )

    objects = ThemeQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tradition", "code"], name="theme_code_unique_per_tradition"
            ),
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(tradition__isnull=True),
                name="common_theme_code_unique",
            ),
        ]

    @property
    def is_common(self):
        return self.tradition_id is None

    def __str__(self):
        return self.name
