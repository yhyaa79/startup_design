# event_hub/views.py

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Event

SORT_CHOICES = [
    {'key': 'newest', 'label': 'جدیدترین'},
    {'key': 'oldest', 'label': 'قدیمی‌ترین'},
    {'key': 'title', 'label': 'عنوان (الفبا)'},
]

SORT_MAP = {
    'newest': '-created_at',
    'oldest': 'created_at',
    'title': 'title',
}


ROW_PREVIEW_COUNT = 5  # هر دسته‌بندی در حالت ردیفی فقط ۵ رویداد نشان می‌دهد

OTHER_CATEGORY_KEY = 'سایر'


def ordered_categories():
    """Event.CATEGORY را برمی‌گرداند، با این تفاوت که دسته‌بندی «سایر»
    همیشه در انتهای لیست قرار می‌گیرد، صرف‌نظر از ترتیب آن در مدل."""
    others = [c for c in Event.CATEGORY if c[0] != OTHER_CATEGORY_KEY]
    saayer = [c for c in Event.CATEGORY if c[0] == OTHER_CATEGORY_KEY]
    return others + saayer


def event_list(request):
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_sort = request.GET.get('sort', 'newest').strip() or 'newest'

    # ---------------------------------------------------------------
    # حالت پیش‌فرض (بدون جستجو و بدون انتخاب دسته‌بندی):
    # ۷ ردیف افقی، یکی به ازای هر دسته‌بندی (سایر همیشه آخر)، هرکدام با ۵ رویداد آخر.
    # ---------------------------------------------------------------
    if not query and not selected_category:
        category_rows = []
        for key, label in ordered_categories():
            cat_qs = Event.objects.filter(category=key).order_by('-created_at')
            total = cat_qs.count()
            if total == 0:
                continue
            category_rows.append({
                'key': key,
                'label': label,
                'count': total,
                'events': cat_qs[:ROW_PREVIEW_COUNT],
                'has_more': total > ROW_PREVIEW_COUNT,
            })

        context = {
            'mode': 'rows',
            'category_rows': category_rows,
            'total_count': Event.objects.count(),
            'query': query,
            'selected_sort': selected_sort,
        }
        return render(request, 'event_hub/event_list.html', context)

    # ---------------------------------------------------------------
    # حالت گرید کامل: وقتی جستجو انجام شده یا یک دسته‌بندی انتخاب/فیلتر شده
    # (یعنی کاربر روی «مشاهده همه» یک دسته‌بندی زده یا جستجو کرده)
    # ---------------------------------------------------------------
    search_qs = Event.objects.all()
    if query:
        search_qs = search_qs.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(section__icontains=query)
            | Q(compiler__icontains=query)
        )

    events = search_qs
    if selected_category:
        events = events.filter(category=selected_category)

    events = events.order_by(SORT_MAP.get(selected_sort, '-created_at'))

    # شمارش رویدادهای هر دسته‌بندی برای نوار فیلتر داخل حالت گرید (سایر همیشه آخر)
    categories = [
        {
            'key': key,
            'label': label,
            'count': search_qs.filter(category=key).count(),
        }
        for key, label in ordered_categories()
    ]

    paginator = Paginator(events, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    qs_parts = []
    if query:
        qs_parts.append(f'q={query}')
    if selected_category:
        qs_parts.append(f'category={selected_category}')
    if selected_sort:
        qs_parts.append(f'sort={selected_sort}')
    base_qs = '&'.join(qs_parts)

    context = {
        'mode': 'grid',
        'events': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_label': next(
            (c['label'] for c in categories if c['key'] == selected_category), ''
        ),
        'query': query,
        'selected_sort': selected_sort,
        'sort_choices': SORT_CHOICES,
        'total_count': search_qs.count(),
        'base_qs': base_qs,
    }
    return render(request, 'event_hub/event_list.html', context)


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    related_events = (
        Event.objects.filter(category=event.category)
        .exclude(pk=event.pk)
        .order_by('-created_at')[:3]
    )
    context = {
        'event': event,
        'related_events': related_events,
    }
    return render(request, 'event_hub/event_detail.html', context)