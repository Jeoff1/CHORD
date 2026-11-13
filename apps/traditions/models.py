from django.conf import settings
from django.core.exceptions import ValidationError
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


class ServiceTemplate(models.Model):
    """A Tradition's structure for a service, with ordered Song Slots (see GLOSSARY.md)."""

    tradition = models.ForeignKey(
        Tradition, on_delete=models.CASCADE, related_name="service_templates"
    )
    code = models.SlugField(max_length=50)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["tradition__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tradition", "code"],
                name="service_template_code_unique_per_tradition",
            )
        ]

    def __str__(self):
        return self.name


class SongSlot(models.Model):
    """A named position in a Service Template that a song fills (see GLOSSARY.md)."""

    template = models.ForeignKey(
        ServiceTemplate, on_delete=models.CASCADE, related_name="slots"
    )
    name = models.CharField(max_length=100)
    position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["template", "position"]
        constraints = [
            models.UniqueConstraint(
                fields=["template", "position"], name="song_slot_position_unique"
            )
        ]

    def __str__(self):
        return self.name


class CalendarEntry(models.Model):
    """A dated Church Calendar entry belonging to one Tradition."""

    tradition = models.ForeignKey(
        Tradition, on_delete=models.CASCADE, related_name="%(class)ss"
    )
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(help_text="Inclusive; equal to the start for one day.")

    class Meta:
        abstract = True
        ordering = ["start_date", "name"]

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": "The end date cannot precede the start."}
            )

    def __str__(self):
        return self.name


class Season(CalendarEntry):
    """A Church Calendar period with a date range, e.g. Lent (see GLOSSARY.md)."""

    class Meta(CalendarEntry.Meta):
        pass

    def clean(self):
        super().clean()
        if not (self.tradition_id and self.start_date and self.end_date):
            return
        overlapping = (
            Season.objects.filter(
                tradition_id=self.tradition_id,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )
            .exclude(pk=self.pk)
            .first()
        )
        if overlapping:
            raise ValidationError(f"These dates overlap the Season {overlapping}.")


class Occasion(CalendarEntry):
    """A Church Calendar event that is not a Season, e.g. INC anniversary."""

    class Meta(CalendarEntry.Meta):
        pass
