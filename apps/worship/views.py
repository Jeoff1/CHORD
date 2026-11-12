from django.contrib import messages
from django.db.models import Count, Prefetch, Q
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.accounts.mixins import AuthenticatedPermissionRequiredMixin
from apps.accounts.models import Role
from apps.events.services import visible_events_for
from apps.members.models import Member

from .chordpro import key_offset, parse_chordpro, wrap_semitones
from .forms import (
    AttendanceFormSet,
    ChoirAnnouncementForm,
    ChoirEnrollmentForm,
    PlanSongForm,
    RehearsalForm,
    SongAssignmentForm,
    SongForm,
    SongResourceForm,
    WorshipPlanForm,
)
from .models import (
    ChoirAnnouncement,
    ChoirEnrollment,
    PlanSong,
    Rehearsal,
    RehearsalAttendance,
    Song,
    SongAssignment,
    SongResource,
    WorshipPlan,
)
from .services import (
    add_plan_song,
    move_plan_song,
    record_rehearsal_attendance,
    remove_plan_song,
    save_song_resource,
)


class ChoirActivityView(AuthenticatedPermissionRequiredMixin, TemplateView):
    permission_required = "worship.view_choir_schedule"
    template_name = "worship/choir_activity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        can_view_announcements = self.request.user.has_perm(
            "worship.view_choir_announcements"
        )
        announcements = ChoirAnnouncement.objects.none()
        if can_view_announcements:
            announcements = ChoirAnnouncement.objects.filter(
                published_at__lte=now,
            ).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
            if not self.request.user.has_perm("worship.manage_choir_announcements"):
                announcements = announcements.filter(
                    audience__in=(
                        ChoirAnnouncement.Audience.ALL,
                        ChoirAnnouncement.Audience.MEMBERS,
                    )
                )

        rehearsals = (
            Rehearsal.objects.filter(
                starts_at__gte=now,
                status=Rehearsal.Status.SCHEDULED,
            )
            .select_related("event")
            .prefetch_related("songs")
        )
        assignments = (
            SongAssignment.objects.filter(
                enrollment__member__user=self.request.user,
                plan_song__plan__service_datetime__gte=now,
            )
            .select_related("plan_song__song", "plan_song__plan")
            .prefetch_related("plan_song__song__resources")
            .order_by("plan_song__plan__service_datetime", "plan_song__position")
        )
        can_view_roster = self.request.user.has_perm("worship.view_choir_roster")
        choir_summary = None
        if can_view_roster:
            choir_summary = ChoirEnrollment.objects.aggregate(
                total=Count("pk"),
                active=Count("pk", filter=Q(status=ChoirEnrollment.Status.ACTIVE)),
                on_leave=Count("pk", filter=Q(status=ChoirEnrollment.Status.ON_LEAVE)),
            )

        context.update(
            {
                "announcements": announcements[:5],
                "assignments": assignments[:8],
                "can_view_announcements": can_view_announcements,
                "can_view_roster": can_view_roster,
                "current_announcement_count": announcements.count(),
                "choir_leaders": Member.objects.filter(
                    user__is_active=True,
                    user__roles__code=Role.Code.CHOIR_LEADER,
                )
                .select_related("user")
                .distinct()
                .order_by("last_name", "first_name"),
                "choir_summary": choir_summary,
                "own_enrollment": ChoirEnrollment.objects.select_related("member")
                .filter(member__user=self.request.user)
                .first(),
                "rehearsals": rehearsals[:6],
                "upcoming_assignment_count": assignments.count(),
                "upcoming_rehearsal_count": rehearsals.count(),
            }
        )
        return context


class ChoirRosterView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "worship.view_choir_roster"
    model = ChoirEnrollment
    template_name = "worship/choir_roster.html"
    context_object_name = "enrollments"
    paginate_by = 25

    def get_queryset(self):
        queryset = ChoirEnrollment.objects.select_related("member")
        status = self.request.GET.get("status", "").strip()
        voice_part = self.request.GET.get("voice_part", "").strip()
        query = self.request.GET.get("q", "").strip()
        if status in ChoirEnrollment.Status.values:
            queryset = queryset.filter(status=status)
        if voice_part in ChoirEnrollment.VoicePart.values:
            queryset = queryset.filter(voice_part=voice_part)
        if query:
            queryset = queryset.filter(
                Q(member__first_name__icontains=query)
                | Q(member__last_name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context.update(
            {
                "status_choices": ChoirEnrollment.Status.choices,
                "voice_choices": ChoirEnrollment.VoicePart.choices,
                "selected_status": self.request.GET.get("status", ""),
                "selected_voice": self.request.GET.get("voice_part", ""),
                "query": self.request.GET.get("q", ""),
                "pagination_query": params.urlencode(),
                "choir_leaders": Member.objects.filter(
                    user__is_active=True,
                    user__roles__code=Role.Code.CHOIR_LEADER,
                )
                .select_related("user")
                .distinct()
                .order_by("last_name", "first_name"),
                "roster_summary": ChoirEnrollment.objects.aggregate(
                    total=Count("pk"),
                    active=Count("pk", filter=Q(status=ChoirEnrollment.Status.ACTIVE)),
                    on_leave=Count(
                        "pk", filter=Q(status=ChoirEnrollment.Status.ON_LEAVE)
                    ),
                    inactive=Count(
                        "pk", filter=Q(status=ChoirEnrollment.Status.INACTIVE)
                    ),
                ),
            }
        )
        return context


class ChoirEnrollmentManageMixin(AuthenticatedPermissionRequiredMixin):
    model = ChoirEnrollment
    form_class = ChoirEnrollmentForm
    template_name = "worship/choir_enrollment_form.html"
    success_url = reverse_lazy("worship:choir-roster")
    slug_field = "public_id"
    slug_url_kwarg = "public_id"


class ChoirEnrollmentCreateView(ChoirEnrollmentManageMixin, CreateView):
    permission_required = (
        "worship.manage_choir",
        "worship.add_choirenrollment",
    )

    def form_valid(self, form):
        messages.success(self.request, "The choir member was enrolled.")
        return super().form_valid(form)


class ChoirEnrollmentUpdateView(ChoirEnrollmentManageMixin, UpdateView):
    permission_required = (
        "worship.manage_choir",
        "worship.change_choirenrollment",
    )

    def form_valid(self, form):
        messages.success(self.request, "The choir enrollment was updated.")
        return super().form_valid(form)


class RehearsalListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "worship.view_choir_schedule"
    model = Rehearsal
    template_name = "worship/rehearsal_list.html"
    context_object_name = "rehearsals"
    paginate_by = 25

    def get_queryset(self):
        queryset = (
            Rehearsal.objects.select_related("event")
            .prefetch_related("songs")
            .annotate(song_count=Count("songs", distinct=True))
        )
        status = self.request.GET.get("status", "").strip()
        timing = self.request.GET.get("timing", "upcoming").strip()
        query = self.request.GET.get("q", "").strip()
        if status in Rehearsal.Status.values:
            queryset = queryset.filter(status=status)
        if timing == "past":
            queryset = queryset.filter(starts_at__lt=timezone.now()).order_by(
                "-starts_at", "-id"
            )
        elif timing != "all":
            timing = "upcoming"
            queryset = queryset.filter(starts_at__gte=timezone.now()).order_by(
                "starts_at", "id"
            )
        else:
            queryset = queryset.order_by("starts_at", "id")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(location__icontains=query)
                | Q(event__title__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        now = timezone.now()
        selected_timing = self.request.GET.get("timing", "upcoming")
        if selected_timing not in {"upcoming", "past", "all"}:
            selected_timing = "upcoming"
        context.update(
            {
                "pagination_query": params.urlencode(),
                "query": self.request.GET.get("q", ""),
                "selected_status": self.request.GET.get("status", ""),
                "selected_timing": selected_timing,
                "status_choices": Rehearsal.Status.choices,
                "timing_counts": Rehearsal.objects.aggregate(
                    upcoming=Count("pk", filter=Q(starts_at__gte=now)),
                    past=Count("pk", filter=Q(starts_at__lt=now)),
                    all=Count("pk"),
                ),
            }
        )
        return context


class RehearsalDetailView(AuthenticatedPermissionRequiredMixin, DetailView):
    permission_required = "worship.view_choir_schedule"
    model = Rehearsal
    template_name = "worship/rehearsal_detail.html"
    context_object_name = "rehearsal"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_queryset(self):
        attendance_queryset = RehearsalAttendance.objects.select_related(
            "enrollment__member"
        )
        if not self.request.user.has_perm("worship.record_rehearsal_attendance"):
            attendance_queryset = attendance_queryset.filter(
                enrollment__member__user=self.request.user
            )
        return Rehearsal.objects.prefetch_related(
            Prefetch(
                "attendance_records",
                queryset=attendance_queryset,
            ),
            "songs__resources",
        ).select_related("event")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        can_record_attendance = self.request.user.has_perm(
            "worship.record_rehearsal_attendance"
        )
        attendance_records = list(self.object.attendance_records.all())
        context["can_record_attendance"] = can_record_attendance
        if can_record_attendance:
            context["attendance_summary"] = {
                "recorded": len(attendance_records),
                "present": sum(
                    record.status == RehearsalAttendance.Status.PRESENT
                    for record in attendance_records
                ),
                "late": sum(
                    record.status == RehearsalAttendance.Status.LATE
                    for record in attendance_records
                ),
                "absent": sum(
                    record.status == RehearsalAttendance.Status.ABSENT
                    for record in attendance_records
                ),
                "excused": sum(
                    record.status == RehearsalAttendance.Status.EXCUSED
                    for record in attendance_records
                ),
            }
        return context


class RehearsalManageMixin(AuthenticatedPermissionRequiredMixin):
    model = Rehearsal
    form_class = RehearsalForm
    template_name = "worship/rehearsal_form.html"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actor"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("worship:rehearsal-detail", args=(self.object.public_id,))


class RehearsalCreateView(RehearsalManageMixin, CreateView):
    permission_required = (
        "worship.manage_rehearsals",
        "worship.add_rehearsal",
    )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "The rehearsal was scheduled.")
        return super().form_valid(form)


class RehearsalUpdateView(RehearsalManageMixin, UpdateView):
    permission_required = (
        "worship.manage_rehearsals",
        "worship.change_rehearsal",
    )

    def form_valid(self, form):
        messages.success(self.request, "The rehearsal was updated.")
        return super().form_valid(form)


class RehearsalAttendanceView(AuthenticatedPermissionRequiredMixin, View):
    permission_required = (
        "worship.record_rehearsal_attendance",
        "worship.add_rehearsalattendance",
        "worship.change_rehearsalattendance",
    )
    template_name = "worship/rehearsal_attendance_form.html"

    def get_rehearsal(self):
        return get_object_or_404(Rehearsal, public_id=self.kwargs["public_id"])

    def get_enrollments(self, rehearsal):
        return (
            ChoirEnrollment.objects.filter(
                Q(status=ChoirEnrollment.Status.ACTIVE)
                | Q(attendance_records__rehearsal=rehearsal)
            )
            .select_related("member")
            .distinct()
        )

    def get_initial(self, rehearsal, enrollments):
        existing = {
            record.enrollment_id: record
            for record in rehearsal.attendance_records.all()
        }
        return [
            {
                "enrollment": enrollment,
                "status": existing[enrollment.pk].status
                if enrollment.pk in existing
                else "",
                "notes": existing[enrollment.pk].notes
                if enrollment.pk in existing
                else "",
            }
            for enrollment in enrollments
        ]

    def get(self, request, *args, **kwargs):
        rehearsal = self.get_rehearsal()
        enrollments = self.get_enrollments(rehearsal)
        formset = AttendanceFormSet(
            initial=self.get_initial(rehearsal, enrollments),
            form_kwargs={"enrollment_queryset": enrollments},
        )
        return self.render(request, rehearsal, formset)

    def post(self, request, *args, **kwargs):
        rehearsal = self.get_rehearsal()
        enrollments = self.get_enrollments(rehearsal)
        formset = AttendanceFormSet(
            request.POST,
            initial=self.get_initial(rehearsal, enrollments),
            form_kwargs={"enrollment_queryset": enrollments},
        )
        if formset.is_valid():
            record_rehearsal_attendance(
                rehearsal=rehearsal,
                entries=formset.cleaned_data,
                actor=request.user,
            )
            messages.success(request, "Rehearsal attendance was recorded.")
            return redirect("worship:rehearsal-detail", public_id=rehearsal.public_id)
        return self.render(request, rehearsal, formset)

    def render(self, request, rehearsal, formset):
        return render(
            request,
            self.template_name,
            {"rehearsal": rehearsal, "formset": formset},
        )


class AnnouncementListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "worship.view_choir_announcements"
    model = ChoirAnnouncement
    template_name = "worship/announcement_list.html"
    context_object_name = "announcements"
    paginate_by = 25

    def get_queryset(self):
        queryset = ChoirAnnouncement.objects.all()
        can_manage = self.request.user.has_perm("worship.manage_choir_announcements")
        now = timezone.now()
        if not can_manage:
            queryset = queryset.filter(published_at__lte=now).filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            )
            queryset = queryset.filter(
                audience__in=(
                    ChoirAnnouncement.Audience.ALL,
                    ChoirAnnouncement.Audience.MEMBERS,
                )
            )
        else:
            audience = self.request.GET.get("audience", "").strip()
            timing = self.request.GET.get("timing", "all").strip()
            if audience in ChoirAnnouncement.Audience.values:
                queryset = queryset.filter(audience=audience)
            if timing == "current":
                queryset = queryset.filter(published_at__lte=now).filter(
                    Q(expires_at__isnull=True) | Q(expires_at__gt=now)
                )
            elif timing == "scheduled":
                queryset = queryset.filter(published_at__gt=now)
            elif timing == "expired":
                queryset = queryset.filter(expires_at__lte=now)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(body__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context.update(
            {
                "audience_choices": ChoirAnnouncement.Audience.choices,
                "can_manage_announcements": self.request.user.has_perm(
                    "worship.manage_choir_announcements"
                ),
                "pagination_query": params.urlencode(),
                "query": self.request.GET.get("q", ""),
                "now": timezone.now(),
                "selected_audience": self.request.GET.get("audience", ""),
                "selected_timing": self.request.GET.get("timing", "all"),
            }
        )
        return context


class AnnouncementManageMixin(AuthenticatedPermissionRequiredMixin):
    model = ChoirAnnouncement
    form_class = ChoirAnnouncementForm
    template_name = "worship/announcement_form.html"
    success_url = reverse_lazy("worship:announcement-list")


class AnnouncementCreateView(AnnouncementManageMixin, CreateView):
    permission_required = (
        "worship.manage_choir_announcements",
        "worship.add_choirannouncement",
    )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "The choir announcement was published.")
        return super().form_valid(form)


class AnnouncementUpdateView(AnnouncementManageMixin, UpdateView):
    permission_required = (
        "worship.manage_choir_announcements",
        "worship.change_choirannouncement",
    )

    def form_valid(self, form):
        messages.success(self.request, "The choir announcement was updated.")
        return super().form_valid(form)


class SongListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "worship.view_song_library"
    model = Song
    template_name = "worship/song_list.html"
    context_object_name = "songs"
    paginate_by = 25

    SORT_OPTIONS = {
        "title": ("title", "artist"),
        "artist": ("artist", "title"),
        "newest": ("-created_at", "title"),
        "recently_updated": ("-updated_at", "title"),
    }

    def get_queryset(self):
        queryset = Song.objects.all()
        query = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "").strip()
        theme = self.request.GET.get("theme", "").strip().lower()
        sort = self.request.GET.get("sort", "title")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(artist__icontains=query)
            )
        if category in Song.Category.values:
            queryset = queryset.filter(category=category)
        if theme:
            queryset = queryset.filter(themes__contains=[theme])
        return queryset.order_by(
            *self.SORT_OPTIONS.get(sort, self.SORT_OPTIONS["title"])
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context.update(
            {
                "category_choices": Song.Category.choices,
                "query": self.request.GET.get("q", ""),
                "selected_category": self.request.GET.get("category", ""),
                "selected_theme": self.request.GET.get("theme", ""),
                "selected_sort": self.request.GET.get("sort", "title"),
                "sort_options": self.SORT_OPTIONS.keys(),
                "pagination_query": params.urlencode(),
            }
        )
        return context


class SongDetailView(AuthenticatedPermissionRequiredMixin, DetailView):
    permission_required = "worship.view_song_library"
    model = Song
    template_name = "worship/song_detail.html"
    context_object_name = "song"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_queryset(self):
        usage_queryset = PlanSong.objects.select_related("plan").order_by(
            "-plan__service_datetime"
        )
        if not self.request.user.has_perm(
            "worship.manage_worship_plans"
        ) and not self.request.user.has_perm("worship.manage_choir"):
            usage_queryset = usage_queryset.filter(
                plan__choir_participations__enrollment__member__user=self.request.user
            ).distinct()
        return Song.objects.prefetch_related(
            "resources",
            Prefetch(
                "plan_items",
                queryset=usage_queryset,
            ),
        )


class SongManageMixin(AuthenticatedPermissionRequiredMixin):
    model = Song
    form_class = SongForm
    template_name = "worship/song_form.html"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_success_url(self):
        return reverse("worship:song-detail", args=(self.object.public_id,))


class SongCreateView(SongManageMixin, CreateView):
    permission_required = (
        "worship.manage_song_library",
        "worship.add_song",
    )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "The song was added to the library.")
        return super().form_valid(form)


class SongUpdateView(SongManageMixin, UpdateView):
    permission_required = (
        "worship.manage_song_library",
        "worship.change_song",
    )

    def form_valid(self, form):
        messages.success(self.request, "The song was updated.")
        return super().form_valid(form)


class SongResourceCreateView(AuthenticatedPermissionRequiredMixin, CreateView):
    permission_required = (
        "worship.manage_song_library",
        "worship.add_songresource",
    )
    model = SongResource
    form_class = SongResourceForm
    template_name = "worship/song_resource_form.html"

    def get_song(self):
        if not hasattr(self, "song"):
            self.song = get_object_or_404(
                Song,
                public_id=self.kwargs["public_id"],
            )
        return self.song

    def form_valid(self, form):
        self.object = save_song_resource(
            form=form,
            song=self.get_song(),
            actor=self.request.user,
        )
        messages.success(self.request, "The authorized song resource was added.")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["song"] = self.get_song()
        return context

    def get_success_url(self):
        return reverse("worship:song-detail", args=(self.get_song().public_id,))


class SongResourceUpdateView(AuthenticatedPermissionRequiredMixin, UpdateView):
    permission_required = (
        "worship.manage_song_library",
        "worship.change_songresource",
    )
    model = SongResource
    form_class = SongResourceForm
    template_name = "worship/song_resource_form.html"

    def get_queryset(self):
        return SongResource.objects.select_related("song")

    def form_valid(self, form):
        self.object = save_song_resource(
            form=form,
            song=self.object.song,
            actor=self.request.user,
        )
        messages.success(self.request, "The authorized song resource was updated.")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["song"] = self.object.song
        return context

    def get_success_url(self):
        return reverse("worship:song-detail", args=(self.object.song.public_id,))


class SongResourceDownloadView(AuthenticatedPermissionRequiredMixin, View):
    permission_required = "worship.view_song_resources"

    def get(self, request, *args, **kwargs):
        resource = get_object_or_404(SongResource, pk=kwargs["pk"])
        if not resource.file:
            raise Http404("This resource is an external link.")
        response = FileResponse(
            resource.file.open("rb"),
            as_attachment=True,
            filename=resource.file.name.rsplit("/", 1)[-1],
        )
        response["X-Content-Type-Options"] = "nosniff"
        return response


class SongResourcePreviewView(AuthenticatedPermissionRequiredMixin, View):
    permission_required = "worship.view_song_resources"
    template_name = "worship/song_resource_preview.html"

    CONTENT_TYPES = {
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
    }

    def get(self, request, *args, **kwargs):
        resource = get_object_or_404(
            SongResource.objects.select_related("song"),
            pk=kwargs["pk"],
        )
        if not resource.file:
            raise Http404("This resource is an external link.")

        if resource.preview_kind in {"pdf", "image"}:
            response = FileResponse(
                resource.file.open("rb"),
                as_attachment=False,
                filename=resource.file.name.rsplit("/", 1)[-1],
                content_type=self.CONTENT_TYPES[resource.file_extension],
            )
            response["X-Content-Type-Options"] = "nosniff"
            return response

        context = {"resource": resource, "preview_unavailable": False}
        if resource.preview_kind in {"text", "chordpro"}:
            resource.file.open("rb")
            try:
                content = resource.file.read().decode("utf-8-sig")
            except UnicodeDecodeError:
                context["preview_unavailable"] = True
            finally:
                resource.file.close()
            if not context["preview_unavailable"]:
                if resource.preview_kind == "chordpro":
                    context.update(self.transposition(request, resource))
                    context["chordpro"] = parse_chordpro(
                        content, semitones=context["semitones"]
                    )
                else:
                    context["text_content"] = content
        else:
            context["preview_unavailable"] = True
        return render(request, self.template_name, context)

    def transposition(self, request, resource):
        """Resolve the semitone offset from the setlist item and the viewer's choice."""
        plan_song = None
        plan_song_id = request.GET.get("plan_song", "")
        if plan_song_id.isdigit():
            plan_song = PlanSong.objects.filter(
                pk=plan_song_id,
                song=resource.song,
                plan__in=visible_worship_plans(request.user),
            ).first()
        planned_offset = (
            key_offset(resource.song.default_key, plan_song.planned_key)
            if plan_song
            else 0
        )
        try:
            semitones = int(request.GET["transpose"])
        except KeyError, ValueError:
            semitones = planned_offset
        semitones = wrap_semitones(semitones)
        return {
            "plan_song": plan_song,
            "semitones": semitones,
            "transpose_down": wrap_semitones(semitones - 1),
            "transpose_up": wrap_semitones(semitones + 1),
        }


def visible_worship_plans(user):
    """Worship plans the user may see: all for managers, else their choir plans."""
    queryset = WorshipPlan.objects.select_related("created_by", "event")
    if user.has_perm("worship.manage_worship_plans") or user.has_perm(
        "worship.manage_choir"
    ):
        return queryset
    return queryset.filter(
        choir_participations__enrollment__member__user=user
    ).distinct()


class WorshipPlanQuerysetMixin:
    def get_queryset(self):
        return visible_worship_plans(self.request.user)


class WorshipPlanListView(
    WorshipPlanQuerysetMixin,
    AuthenticatedPermissionRequiredMixin,
    ListView,
):
    permission_required = "worship.view_worship_plans"
    model = WorshipPlan
    template_name = "worship/plan_list.html"
    context_object_name = "plans"
    paginate_by = 25

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .annotate(
                setlist_count=Count("setlist_items", distinct=True),
                participant_count=Count("choir_participations", distinct=True),
            )
        )
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        timing = self.request.GET.get("timing", "upcoming").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(location__icontains=query)
                | Q(event__title__icontains=query)
            )
        if status in WorshipPlan.Status.values:
            queryset = queryset.filter(status=status)
        now = timezone.now()
        if timing == "previous":
            queryset = queryset.filter(service_datetime__lt=now).order_by(
                "-service_datetime", "-id"
            )
        elif timing != "all":
            timing = "upcoming"
            queryset = queryset.filter(service_datetime__gte=now).order_by(
                "service_datetime", "id"
            )
        else:
            queryset = queryset.order_by("-service_datetime", "-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        selected_timing = self.request.GET.get("timing", "upcoming")
        if selected_timing not in {"upcoming", "previous", "all"}:
            selected_timing = "upcoming"
        now = timezone.now()
        scoped_plans = WorshipPlanQuerysetMixin.get_queryset(self)
        context.update(
            {
                "query": self.request.GET.get("q", ""),
                "selected_status": self.request.GET.get("status", ""),
                "selected_timing": selected_timing,
                "status_choices": WorshipPlan.Status.choices,
                "pagination_query": params.urlencode(),
                "plan_summary": scoped_plans.aggregate(
                    all=Count("pk"),
                    upcoming=Count("pk", filter=Q(service_datetime__gte=now)),
                    previous=Count("pk", filter=Q(service_datetime__lt=now)),
                    ready=Count("pk", filter=Q(status=WorshipPlan.Status.READY)),
                    preparing=Count(
                        "pk", filter=Q(status=WorshipPlan.Status.PREPARING)
                    ),
                ),
            }
        )
        return context


class WorshipPlanDetailView(
    WorshipPlanQuerysetMixin,
    AuthenticatedPermissionRequiredMixin,
    DetailView,
):
    permission_required = "worship.view_worship_plans"
    model = WorshipPlan
    template_name = "worship/plan_detail.html"
    context_object_name = "plan"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_queryset(self):
        assignment_queryset = SongAssignment.objects.select_related(
            "enrollment__member"
        )
        if not self.request.user.has_perm(
            "worship.manage_song_assignments"
        ) and not self.request.user.has_perm("worship.view_choir_roster"):
            assignment_queryset = assignment_queryset.filter(
                enrollment__member__user=self.request.user
            )
        return (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "setlist_items",
                    queryset=PlanSong.objects.select_related("song").prefetch_related(
                        Prefetch("assignments", queryset=assignment_queryset),
                        "song__resources",
                    ),
                ),
                "choir_participations__enrollment__member",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setlist_items = list(self.object.setlist_items.all())
        participations = list(self.object.choir_participations.all())
        can_view_full_team = self.request.user.has_perm("worship.view_choir_roster")
        can_manage_assignments = self.request.user.has_perm(
            "worship.manage_song_assignments"
        )
        assignment_count = sum(len(item.assignments.all()) for item in setlist_items)
        context.update(
            {
                "assignment_count": assignment_count,
                "can_manage_assignments": can_manage_assignments,
                "can_view_full_team": can_view_full_team,
                "linked_event_visible": bool(
                    self.object.event_id
                    and visible_events_for(self.request.user)
                    .filter(pk=self.object.event_id)
                    .exists()
                ),
                "own_participation": next(
                    (
                        participation
                        for participation in participations
                        if participation.enrollment.member.user_id
                        == self.request.user.pk
                    ),
                    None,
                ),
                "participant_count": len(participations),
                "setlist_count": len(setlist_items),
            }
        )
        return context


class WorshipPlanManageMixin(AuthenticatedPermissionRequiredMixin):
    model = WorshipPlan
    form_class = WorshipPlanForm
    template_name = "worship/plan_form.html"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actor"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("worship:plan-detail", args=(self.object.public_id,))


class WorshipPlanCreateView(WorshipPlanManageMixin, CreateView):
    permission_required = (
        "worship.manage_worship_plans",
        "worship.add_worshipplan",
        "worship.add_planchoirparticipation",
    )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "The worship plan was created.")
        return super().form_valid(form)


class WorshipPlanUpdateView(WorshipPlanManageMixin, UpdateView):
    permission_required = (
        "worship.manage_worship_plans",
        "worship.change_worshipplan",
        "worship.add_planchoirparticipation",
        "worship.delete_planchoirparticipation",
    )

    def form_valid(self, form):
        messages.success(self.request, "The worship plan was updated.")
        return super().form_valid(form)


class PlanSongCreateView(AuthenticatedPermissionRequiredMixin, CreateView):
    permission_required = (
        "worship.manage_worship_plans",
        "worship.add_plansong",
    )
    model = PlanSong
    form_class = PlanSongForm
    template_name = "worship/plan_song_form.html"

    def get_plan(self):
        if not hasattr(self, "plan"):
            self.plan = get_object_or_404(
                WorshipPlan,
                public_id=self.kwargs["public_id"],
            )
        return self.plan

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["plan"] = self.get_plan()
        return kwargs

    def form_valid(self, form):
        self.object = add_plan_song(
            plan=self.get_plan(),
            song=form.cleaned_data["song"],
            planned_key=form.cleaned_data["planned_key"],
            notes=form.cleaned_data["notes"],
        )
        messages.success(self.request, "The song was added to the setlist.")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["plan"] = self.get_plan()
        context["setlist_count"] = self.get_plan().setlist_items.count()
        return context

    def get_success_url(self):
        return reverse("worship:plan-detail", args=(self.get_plan().public_id,))


class PlanSongMoveView(AuthenticatedPermissionRequiredMixin, View):
    permission_required = (
        "worship.manage_worship_plans",
        "worship.change_plansong",
    )

    def post(self, request, *args, **kwargs):
        plan_song = get_object_or_404(
            PlanSong.objects.select_related("plan"),
            pk=kwargs["pk"],
            plan__public_id=kwargs["public_id"],
        )
        direction = kwargs["direction"]
        if direction not in {"up", "down"}:
            raise Http404("Unknown setlist movement.")
        move_plan_song(plan_song=plan_song, direction=direction)
        return redirect("worship:plan-detail", public_id=plan_song.plan.public_id)


class PlanSongRemoveView(AuthenticatedPermissionRequiredMixin, View):
    permission_required = (
        "worship.manage_worship_plans",
        "worship.delete_plansong",
    )

    def post(self, request, *args, **kwargs):
        plan_song = get_object_or_404(
            PlanSong.objects.select_related("plan"),
            pk=kwargs["pk"],
            plan__public_id=kwargs["public_id"],
        )
        plan_public_id = plan_song.plan.public_id
        remove_plan_song(plan_song=plan_song)
        messages.success(request, "The song was removed from the setlist.")
        return redirect("worship:plan-detail", public_id=plan_public_id)


class SongAssignmentUpdateView(AuthenticatedPermissionRequiredMixin, View):
    permission_required = (
        "worship.manage_song_assignments",
        "worship.add_songassignment",
        "worship.change_songassignment",
        "worship.delete_songassignment",
    )
    template_name = "worship/song_assignment_form.html"

    def get_plan_song(self):
        return get_object_or_404(
            PlanSong.objects.select_related("plan", "song").prefetch_related(
                "song__resources"
            ),
            pk=self.kwargs["pk"],
            plan__public_id=self.kwargs["public_id"],
        )

    def get(self, request, *args, **kwargs):
        plan_song = self.get_plan_song()
        form = SongAssignmentForm(plan_song=plan_song, actor=request.user)
        return self.render(request, plan_song, form)

    def post(self, request, *args, **kwargs):
        plan_song = self.get_plan_song()
        form = SongAssignmentForm(
            request.POST,
            plan_song=plan_song,
            actor=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Choir song assignments were updated.")
            return redirect("worship:plan-detail", public_id=plan_song.plan.public_id)
        return self.render(request, plan_song, form)

    def render(self, request, plan_song, form):
        return render(
            request,
            self.template_name,
            {"plan_song": plan_song, "form": form},
        )
