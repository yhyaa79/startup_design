# project/views.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)

from .forms import ResearchProjectForm, ProjectApplicationForm
from .models import ResearchProject, ProjectApplication, ProjectMember


class ProjectListView(ListView):
    model = ResearchProject
    template_name = 'project/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        qs = (
            ResearchProject.objects
            .select_related('owner_user', 'owner_profile')
            .prefetch_related('members')
            .filter(is_active=True, visibility='public')
            .annotate(
                members_count=Count('members', distinct=True),
                applications_count=Count('applications', distinct=True),
            )
        )

        q = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '').strip()
        status = self.request.GET.get('status', '').strip()
        collaboration = self.request.GET.get('collaboration', '').strip()

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(short_description__icontains=q) |
                Q(description__icontains=q) |
                Q(keywords__icontains=q) |
                Q(field__icontains=q) |
                Q(institution__icontains=q)
            )

        if category:
            qs = qs.filter(category=category)

        if status:
            qs = qs.filter(status=status)

        if collaboration:
            qs = qs.filter(collaboration_status=collaboration)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = ResearchProject.CATEGORY_CHOICES
        context['status_choices'] = ResearchProject.STATUS_CHOICES
        context['collaboration_choices'] = ResearchProject.COLLABORATION_CHOICES
        context['q'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_collaboration'] = self.request.GET.get('collaboration', '')
        context['total_projects'] = self.get_queryset().count()
        return context


class MyProjectListView(LoginRequiredMixin, ListView):
    model = ResearchProject
    template_name = 'project/my_projects.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        if not hasattr(self.request.user, 'profile'):
            return ResearchProject.objects.none()

        return (
            ResearchProject.objects
            .filter(owner_user=self.request.user)
            .annotate(
                members_count=Count('members', distinct=True),
                applications_count=Count('applications', distinct=True),
            )
            .order_by('-created_at')
        )


class ProjectDetailView(DetailView):
    model = ResearchProject
    template_name = 'project/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        qs = (
            ResearchProject.objects
            .select_related('owner_user', 'owner_profile')
            .prefetch_related('members__profile', 'updates', 'files', 'applications')
        )

        if self.request.user.is_authenticated:
            return qs.filter(Q(visibility='public') | Q(owner_user=self.request.user))

        return qs.filter(visibility='public', is_active=True)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        context['can_edit'] = (
            self.request.user.is_authenticated and
            project.owner_user == self.request.user
        )

        context['has_applied'] = False
        context['is_member'] = False

        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
            context['has_applied'] = ProjectApplication.objects.filter(
                project=project,
                applicant_profile=profile
            ).exists()
            context['is_member'] = ProjectMember.objects.filter(
                project=project,
                profile=profile
            ).exists()

        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = ResearchProject
    form_class = ResearchProjectForm
    template_name = 'project/project_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'برای ثبت پروژه ابتدا باید پروفایل خود را تکمیل کنید.')
            return redirect('project:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner_user = self.request.user
        form.instance.owner_profile = self.request.user.profile
        messages.success(self.request, 'پروژه با موفقیت ثبت شد.')
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = ResearchProject
    form_class = ResearchProjectForm
    template_name = 'project/project_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return ResearchProject.objects.filter(owner_user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'پروژه با موفقیت بروزرسانی شد.')
        return super().form_valid(form)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = ResearchProject
    template_name = 'project/project_confirm_delete.html'
    success_url = reverse_lazy('project:my_projects')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return ResearchProject.objects.filter(owner_user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'پروژه حذف شد.')
        return super().delete(request, *args, **kwargs)


class ProjectApplyView(LoginRequiredMixin, FormView):
    template_name = 'project/project_apply.html'
    form_class = ProjectApplicationForm

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'برای ارسال درخواست همکاری ابتدا پروفایل خود را تکمیل کنید.')
            return redirect('project:list')

        self.project = ResearchProject.objects.filter(
            slug=kwargs.get('slug'),
            visibility='public',
            is_active=True
        ).first()

        if not self.project:
            raise Http404

        if self.project.owner_user == request.user:
            messages.warning(request, 'شما مالک این پروژه هستید.')
            return redirect(self.project.get_absolute_url())

        if not self.project.is_open_for_collaboration:
            messages.warning(request, 'این پروژه در حال حاضر جذب همکار ندارد.')
            return redirect(self.project.get_absolute_url())

        if ProjectApplication.objects.filter(
            project=self.project,
            applicant_profile=request.user.profile
        ).exists():
            messages.info(request, 'شما قبلاً برای این پروژه درخواست همکاری ارسال کرده‌اید.')
            return redirect(self.project.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        application = form.save(commit=False)
        application.project = self.project
        application.applicant_user = self.request.user
        application.applicant_profile = self.request.user.profile
        application.save()

        messages.success(self.request, 'درخواست همکاری شما با موفقیت ارسال شد.')
        return redirect(self.project.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
