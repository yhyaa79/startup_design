# course/models.py

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Course, Category
from .data import VIDEO_DATABASE


def get_all_courses_from_db_or_data():
    """Return courses from DB; fall back to static data dict if DB is empty."""
    if Course.objects.exists():
        return None  # use ORM queries in views
    return VIDEO_DATABASE


# ── helpers ──────────────────────────────────────────────────────────────────

CATEGORY_LABELS = {
    'olampiad_elmi': 'المپیاد علمی',
    'tahghighat': 'تحقیقات',
    'maghaleh': 'مقاله‌نویسی',
    'maghale_congress': 'کنگره',
    'ketab': 'تألیف کتاب',
    'ekhtera': 'ثبت اختراع',
    'noavari': 'نوآوری',
    'jashnvare': 'جشنواره',
    'bedone_dastebandi': 'متفرقه',
}


def _flatten(db: dict, category_filter=None, q=None):
    """Flatten VIDEO_DATABASE dict to a list of dicts with extra fields."""
    result = []
    for cat_key, courses in db.items():
        if category_filter and cat_key != category_filter:
            continue
        for c in courses:
            if not c.get('active', True):
                continue
            if q:
                haystack = (c.get('title', '') + c.get('shortDesc', '') +
                            c.get('instructor', '') + c.get('longDesc', '')).lower()
                if q.lower() not in haystack:
                    continue
            c['category_label'] = CATEGORY_LABELS.get(cat_key, cat_key)
            c['category_key'] = cat_key
            result.append(c)
    return result


# ── views ─────────────────────────────────────────────────────────────────────

def course_list(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    courses = _flatten(VIDEO_DATABASE, category_filter=category or None, q=query or None)

    # counts per category for sidebar
    cat_counts = {}
    for c in _flatten(VIDEO_DATABASE):
        k = c['category_key']
        cat_counts[k] = cat_counts.get(k, 0) + 1

    categories = [
        {'key': k, 'label': v, 'count': cat_counts.get(k, 0)}
        for k, v in CATEGORY_LABELS.items()
        if cat_counts.get(k, 0) > 0
    ]

    context = {
        'courses': courses,
        'query': query,
        'selected_category': category,
        'categories': categories,
        'total_count': len(courses),
    }
    return render(request, 'course/course_list.html', context)


def course_detail(request, course_id):
    # search in flat data
    all_courses = _flatten(VIDEO_DATABASE)
    course = next((c for c in all_courses if c['id'] == course_id), None)

    if course is None:
        from django.http import Http404
        raise Http404("دوره یافت نشد")

    # related courses – same category, exclude current
    related = [
        c for c in _flatten(VIDEO_DATABASE, category_filter=course['category_key'])
        if c['id'] != course_id
    ][:4]

    context = {
        'course': course,
        'related': related,
    }
    return render(request, 'course/course_detail.html', context)