# resume/views.py

import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST

from accounts.models import Profile
from .models import Resume
from .forms import ResumeCreateForm
from .pdf_generator import generate_pdf
from .docx_generator import generate_docx

logger = logging.getLogger(__name__)


# ── List of resumes ────────────────────────────────────────────────────────────
from django.db import OperationalError, ProgrammingError

@login_required
def resume_list(request):
    try:
        resumes = Resume.objects.filter(user=request.user)
        list(resumes[:1])  # trigger DB check safely
    except (OperationalError, ProgrammingError):
        resumes = []
    return render(request, 'resume/resume_list.html', {'resumes': resumes})


# ── Create / configure a new resume ───────────────────────────────────────────
# resume/views.py

@login_required
def resume_create(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'ابتدا پروفایل خود را تکمیل کنید.')
        return redirect('accounts:profile_edit')

    if request.method == 'POST':
        form = ResumeCreateForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            try:
                resume.save()
                return redirect('resume:resume_generate', pk=resume.pk)
            except (OperationalError, ProgrammingError) as e:
                logger.error(f'Database error saving resume: {e}')
                messages.error(request, 'خطا در ذخیره رزومه. لطفا دوباره تلاش کنید.')
                return redirect('resume:resume_create')
    else:
        form = ResumeCreateForm()

    templates_info = [
        {
            'value': 'classic',
            'label': 'کلاسیک حرفه‌ای',
            'desc': 'ساختار سنتی با رنگ‌بندی آبی ناوی. مناسب رزیدنتی و هیات علمی.',
            'colors': ['#1a3a5c', '#2e6da4', '#e8f0f7'],
        },
        {
            'value': 'modern',
            'label': 'مدرن',
            'desc': 'طراحی مدرن با تاکید رنگی. مناسب پوزیشن‌های بین‌المللی.',
            'colors': ['#1d2d44', '#c1121f', '#f0f4f8'],
        },
        {
            'value': 'academic',
            'label': 'آکادمیک پژوهشی',
            'desc': 'پالت سبز آرام. مناسب فلوشیپ و ریسرچ پوزیشن.',
            'colors': ['#2d6a4f', '#40916c', '#d8f3dc'],
        },
        {
            'value': 'minimal',
            'label': 'مینیمال',
            'desc': 'سیاه و سفید ساده. بیشترین سازگاری با سیستم‌های ATS.',
            'colors': ['#222222', '#555555', '#f0f0f0'],
        },
    ]

    return render(request, 'resume/resume_create.html', {
        'form': form,
        'profile': profile,
        'templates_info': templates_info,
    })


# ── Generate files ─────────────────────────────────────────────────────────────
@login_required
def resume_generate(request, pk):
    try:
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        profile = request.user.profile
    except (OperationalError, ProgrammingError) as e:
        logger.error(f'Database error: {e}')
        messages.error(request, 'خطا در دسترسی به اطلاعات.')
        return redirect('resume:resume_list')

    if resume.use_ai and not resume.ai_enhanced:
        try:
            from .ai_helper import generate_resume_summary
            summary = generate_resume_summary(profile, resume.purpose)
            resume.ai_summary = summary
            resume.ai_enhanced = True
            resume.save(update_fields=['ai_summary', 'ai_enhanced'])
        except Exception as e:
            logger.warning(f'AI summary failed: {e}')
            messages.warning(request, f'هوش مصنوعی در دسترس نبود؛ رزومه بدون AI ساخته می‌شود.')

    try:
        pdf_bytes = generate_pdf(profile, resume)
        fname_pdf = f'resume_{resume.pk}.pdf'
        if resume.pdf_file:
            resume.pdf_file.delete(save=False)
        resume.pdf_file.save(fname_pdf, ContentFile(pdf_bytes), save=False)
    except Exception as e:
        logger.error(f'PDF generation error: {e}')
        messages.error(request, f'خطا در ساخت PDF: {e}')
        try:
            resume.save()
        except (OperationalError, ProgrammingError):
            pass
        return redirect('resume:resume_detail', pk=resume.pk)

    try:
        docx_bytes = generate_docx(profile, resume)
        fname_docx = f'resume_{resume.pk}.docx'
        if resume.docx_file:
            resume.docx_file.delete(save=False)
        resume.docx_file.save(fname_docx, ContentFile(docx_bytes), save=False)
    except Exception as e:
        logger.error(f'DOCX generation error: {e}')
        messages.warning(request, f'فایل Word ساخته نشد: {e}')

    try:
        resume.save()
    except (OperationalError, ProgrammingError) as e:
        logger.error(f'Database error saving resume: {e}')
        messages.error(request, 'خطا در ذخیره رزومه.')
        return redirect('resume:resume_list')

    messages.success(request, 'رزومه با موفقیت ساخته شد!')
    return redirect('resume:resume_detail', pk=resume.pk)


# ── Detail / preview ───────────────────────────────────────────────────────────
@login_required
def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    profile = request.user.profile
    return render(request, 'resume/resume_detail.html', {
        'resume': resume,
        'profile': profile,
    })


# ── Download PDF ───────────────────────────────────────────────────────────────
@login_required
def download_pdf(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if not resume.pdf_file:
        messages.error(request, 'فایل PDF موجود نیست. ابتدا رزومه را بسازید.')
        return redirect('resume:resume_detail', pk=pk)
    response = HttpResponse(resume.pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resume_{pk}.pdf"'
    return response


# ── Download DOCX ──────────────────────────────────────────────────────────────
@login_required
def download_docx(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if not resume.docx_file:
        messages.error(request, 'فایل Word موجود نیست. ابتدا رزومه را بسازید.')
        return redirect('resume:resume_detail', pk=pk)
    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    response = HttpResponse(resume.docx_file.read(), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="resume_{pk}.docx"'
    return response


# ── Regenerate ─────────────────────────────────────────────────────────────────
@login_required
def resume_regenerate(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    resume.ai_enhanced = False  # allow AI to run again
    resume.save(update_fields=['ai_enhanced'])
    return redirect('resume:resume_generate', pk=pk)


# ── Edit settings ──────────────────────────────────────────────────────────────
@login_required
def resume_edit(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ResumeCreateForm(request.POST, instance=resume)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.ai_enhanced = False  # force re-generation
            resume.save()
            return redirect('resume:resume_generate', pk=resume.pk)
    else:
        form = ResumeCreateForm(instance=resume)
    return render(request, 'resume/resume_edit.html', {'form': form, 'resume': resume})


# ── Delete ─────────────────────────────────────────────────────────────────────
@login_required
def resume_delete(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        if resume.pdf_file:
            resume.pdf_file.delete()
        if resume.docx_file:
            resume.docx_file.delete()
        resume.delete()
        messages.success(request, 'رزومه حذف شد.')
        return redirect('resume:resume_list')
    return render(request, 'resume/resume_confirm_delete.html', {'resume': resume})