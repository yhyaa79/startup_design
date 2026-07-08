# course/views.py

from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q
from .models import Course, Category


def course_list(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()

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

    context = {
        'courses': courses,
        'query': query,
        'selected_category': category_slug,
        'categories': categories,
        'total_count': courses.count(),
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
