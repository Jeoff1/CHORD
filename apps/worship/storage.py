import os
from functools import cached_property

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class ProtectedResourceStorage(FileSystemStorage):
    """Store licensed resources outside the public media directory."""

    @cached_property
    def base_location(self):
        return settings.PROTECTED_MEDIA_ROOT

    @cached_property
    def location(self):
        return os.path.abspath(self.base_location)

    @cached_property
    def base_url(self):
        return None


protected_resource_storage = ProtectedResourceStorage()
