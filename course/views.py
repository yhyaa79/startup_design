# course/views.py

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q
from .models import Course, Category


SORT_OPTIONS = {
    'newest': ('-created_at', 'جدیدترین'),
    'popular': ('-view_count', 'محبوب‌ترین'),
    'rating': ('-stars', 'بیشترین امتیاز'),
    'oldest': ('created_at', 'قدیمی‌ترین'),
}

PAGE_SIZE = 12


def course_list(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    sort_key = request.GET.get('sort', 'newest').strip()
    if sort_key not in SORT_OPTIONS:
        sort_key = 'newest'

    courses = Course.objects.filter(active=True).select_related('category')

    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(short_desc__icontains=query) |
            Q(instructor__icontains=query) |
            Q(long_desc__icontains=query)
        )

    order_field, _ = SORT_OPTIONS[sort_key]
    courses = courses.order_by(order_field)

    total_count = courses.count()

    paginator = Paginator(courses, PAGE_SIZE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    categories = (
        Category.objects
        .filter(courses__active=True)
        .distinct()
        .order_by('order')
    )
    categories = [
        {'key': cat.slug, 'label': cat.name, 'count': cat.courses.filter(active=True).count()}
        for cat in categories
    ]

    sort_choices = [
        {'key': key, 'label': label} for key, (_, label) in SORT_OPTIONS.items()
    ]

    # Build query string (without 'page') to keep filters when paginating
    params = request.GET.copy()
    params.pop('page', None)
    base_qs = params.urlencode()

    context = {
        'courses': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'query': query,
        'selected_category': category_slug,
        'selected_sort': sort_key,
        'categories': categories,
        'sort_choices': sort_choices,
        'total_count': total_count,
        'base_qs': base_qs,
    }
    return render(request, 'course/course_list.html', context)


def course_detail(request, course_id):
    course = get_object_or_404(
        Course.objects.select_related('category'),
        course_id=course_id,
        active=True,
    )

    Course.objects.filter(pk=course.pk).update(view_count=F('view_count') + 1)
    course.refresh_from_db(fields=['view_count'])

    related = (
        Course.objects
        .filter(category=course.category, active=True)
        .exclude(pk=course.pk)
        .select_related('category')[:4]
    )

    context = {
        'course': course,
        'related': related,
    }
    return render(request, 'course/course_detail.html', context)