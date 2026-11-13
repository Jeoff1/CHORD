from django import forms

from .models import ChurchRecord, ChurchRecordType
from .services import available_record_types


class ChurchRecordForm(forms.ModelForm):
    class Meta:
        model = ChurchRecord
        fields = (
            "record_type",
            "member",
            "name",
            "date",
            "officiant",
            "place",
            "notes",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "record_type": "Record type",
            "member": "Member",
            "name": "Name (if not a member)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        record_types = available_record_types()
        if self.instance.record_type_id:
            # A record made under a previous Tradition keeps its own type.
            record_types = record_types | ChurchRecordType.objects.filter(
                pk=self.instance.record_type_id
            )
        self.fields["record_type"].queryset = record_types
        for field in self.fields.values():
            class_name = (
                "form-select"
                if isinstance(field.widget, forms.Select)
                else "form-control"
            )
            field.widget.attrs.setdefault("class", class_name)
