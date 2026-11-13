from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.mixins import AuthenticatedPermissionRequiredMixin

from .forms import ChurchRecordForm
from .models import ChurchRecord, ChurchRecordAuditEvent
from .services import available_record_types, record_church_record_event

VIEW_PERMS = ("records.view_church_records",)
MANAGE_PERMS = ("records.view_church_records", "records.manage_church_records")


def _date_param(params, key):
    """The ISO date in ``params[key]``, or None when absent or malformed."""
    try:
        return parse_date(params.get(key, "").strip())
    except ValueError:
        return None


class ChurchRecordListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = VIEW_PERMS
    template_name = "records/record_list.html"
    context_object_name = "records"
    paginate_by = 25

    def get_queryset(self):
        queryset = ChurchRecord.objects.select_related("record_type", "member")
        params = self.request.GET
        query = params.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(member__first_name__icontains=query)
                | Q(member__last_name__icontains=query)
            )
        record_type = params.get("type", "").strip()
        if record_type.isdigit():
            queryset = queryset.filter(record_type_id=record_type)
        date_from = _date_param(params, "date_from")
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        date_to = _date_param(params, "date_to")
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context.update(
            {
                "record_types": available_record_types(),
                "query": self.request.GET.get("q", ""),
                "selected_type": self.request.GET.get("type", ""),
                "date_from": self.request.GET.get("date_from", ""),
                "date_to": self.request.GET.get("date_to", ""),
                "pagination_query": params.urlencode(),
            }
        )
        return context


class ChurchRecordDetailView(AuthenticatedPermissionRequiredMixin, DetailView):
    permission_required = VIEW_PERMS
    template_name = "records/record_detail.html"
    context_object_name = "record"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"
    queryset = ChurchRecord.objects.select_related("record_type", "member")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.has_perm("records.view_churchrecordauditevent"):
            context["audit_events"] = self.object.audit_events.select_related("actor")
        return context


class ChurchRecordManageMixin(AuthenticatedPermissionRequiredMixin):
    model = ChurchRecord
    form_class = ChurchRecordForm
    template_name = "records/record_form.html"
    audit_action = None
    success_message = ""

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        record_church_record_event(
            record=self.object,
            actor=self.request.user,
            action=self.audit_action,
            fields_changed=form.changed_data,
        )
        messages.success(self.request, self.success_message)
        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


class ChurchRecordCreateView(ChurchRecordManageMixin, CreateView):
    permission_required = (*MANAGE_PERMS, "records.add_churchrecord")
    audit_action = ChurchRecordAuditEvent.Action.CREATED
    success_message = "The church record was created."


class ChurchRecordUpdateView(ChurchRecordManageMixin, UpdateView):
    permission_required = (*MANAGE_PERMS, "records.change_churchrecord")
    slug_field = "public_id"
    slug_url_kwarg = "public_id"
    audit_action = ChurchRecordAuditEvent.Action.UPDATED
    success_message = "The church record was updated."
