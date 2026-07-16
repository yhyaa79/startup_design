# roadmap/checkpoint_generator.py
"""
تولید خودکار checkpoint های تمام فعالیت‌های یک رودمپ در یک فراخوانی واحد AI.

به‌جای یک کال جدا برای هر فعالیت، تمام فعالیت‌های رودمپ (با شناسه/index)
در یک درخواست به AI داده می‌شوند و AI برای هرکدام، با توجه به duration_days
و دوره‌های آموزشی مرتبط، تعداد و محتوای چک‌پوینت مناسب را تعیین می‌کند.

اگر AI به‌طور کامل fail کند یا برای برخی فعالیت‌ها پاسخ معتبر نداشته باشد،
برای همان موارد از یک fallback قانون‌محور استفاده می‌شود تا ساخت رودمپ
هرگز به‌طور کامل متوقف نشود.
"""

import json
import logging
from datetime import timedelta

from .ai_roadmap import _call_gpt_api, _strip_code_fences

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# جمع‌آوری داده‌های دوره‌های آموزشی (کل کاتالوگ فعال)
# ═══════════════════════════════════════════════════════════════

def _collect_relevant_courses(activity_titles: list = None, limit: int = None) -> list:
    """
    جمع‌آوری تمام دوره‌های آموزشی فعال سیستم و ارسال کامل آن‌ها به AI،
    تا خود AI با دید کامل به کل کاتالوگ، مرتبط‌ترین دوره را برای هر
    فعالیت انتخاب و در چک‌پوینت‌ها استفاده کند (به‌جای فیلتر از پیش
    بر اساس تطابق کلمه‌ای که ممکن است دوره‌های مرتبط را حذف کند).
    """
    try:
        from course.models import Course
    except Exception:
        logger.warning("اپ course در دسترس نیست؛ لیست دوره‌ها خالی ارسال می‌شود.")
        return []

    try:
        qs = Course.objects.filter(active=True).select_related('category').order_by('category__name', 'title')
        if limit:
            qs = qs[:limit]

        courses = []
        for c in qs:
            courses.append({
                'id': c.id,
                'title': c.title,
                'short_desc': (c.short_desc or '')[:250],
                'category': c.category.name if c.category_id else '',
                'duration': c.duration or '',
                'instructor': c.instructor or '',
                'url': c.get_absolute_url(),
            })
        return courses

    except Exception:
        logger.exception("خطا در جمع‌آوری دوره‌های آموزشی برای ساخت چک‌پوینت‌ها.")
        return []




# ═══════════════════════════════════════════════════════════════
# Fallback قانون‌محور (به‌ازای هر فعالیتی که AI برایش پاسخ معتبر نداد)
# ═══════════════════════════════════════════════════════════════

def _determine_checkpoint_count_fallback(duration_days: int) -> int:
    if duration_days <= 3:
        return 1
    elif duration_days <= 7:
        return 2
    elif duration_days <= 14:
        return 3
    elif duration_days <= 21:
        return 4
    elif duration_days <= 30:
        return 5
    else:
        return min(10, max(5, duration_days // 7))


def _build_fallback_checkpoints(activity_title: str, start_date, duration_days: int) -> list:
    duration_days = max(1, int(duration_days or 1))
    count = _determine_checkpoint_count_fallback(duration_days)
    interval = duration_days / (count + 1)

    checkpoints = []
    for i in range(1, count + 1):
        offset_days = min(round(interval * i), duration_days)
        due_date = start_date + timedelta(days=offset_days)
        checkpoints.append({
            'id': i,
            'source_type': 'manual',
            'title': f'چک‌پوینت {i} از {count} — {activity_title}',
            'description': f'بررسی و ثبت میزان پیشرفت فعالیت «{activity_title}» تا این تاریخ',
            'priority': 'medium',
            'due_date': str(due_date),
            'notes': '',
            'source_id': None,
            'source_url': None,
            'is_completed': False,
            'date': None,
            'extra_details': {},
        })
    return checkpoints


# ═══════════════════════════════════════════════════════════════
# پرامپ AI برای حالت Batch (کل رودمپ در یک کال)
# ═══════════════════════════════════════════════════════════════

_SYSTEM_PROMPT = """
تو یک مشاور ارشد آموزشی و پژوهشی در حوزه علوم پزشکی هستی. وظیفه‌ات طراحی «چک‌پوینت‌های اجرایی» (نقاط کنترل پیشرفت) برای تمام فعالیت‌های یک نقشه راه (رودمپ) رزومه‌ای است که در ادامه به‌صورت یک لیست شماره‌گذاری‌شده در اختیارت قرار می‌گیرد.

# وظیفه
برای **هر یک** از فعالیت‌های داده‌شده (بدون استثنا و بدون جا انداختن هیچ‌کدام)، باید:

1. تعداد چک‌پوینت مناسب همان فعالیت را با توجه به duration_days خودش تعیین کنی (نه یک عدد ثابت برای همه). راهنما:
   - فعالیت خیلی کوتاه (۱ تا ۳ روز) → معمولاً ۱ چک‌پوینت.
   - فعالیت کوتاه (۴ تا ۱۴ روز) → ۲ تا ۳ چک‌پوینت.
   - فعالیت میان‌مدت (۱۵ تا ۳۰ روز) → ۳ تا ۵ چک‌پوینت.
   - فعالیت بلندمدت (بیش از ۳۰ روز) → یک چک‌پوینت به‌ازای هر ۵ تا ۸ روز، حداکثر ۱۰ چک‌پوینت.
   این‌ها فقط راهنما هستند؛ با توجه به ماهیت واقعی هر فعالیت با قضاوت خودت تصمیم نهایی را بگیر، نه صرفاً یک فرمول خطی.

2. **توضیحات (description) هر چک‌پوینت باید کامل، عملی و چندجمله‌ای باشد، نه یک جمله کوتاه و کلی.** هر description باید حداقل شامل این موارد باشد:
   - دقیقاً چه کاری در این مرحله باید انجام شود (اقدام مشخص، نه کلی‌گویی).
   - چرا این گام در مسیر تکمیل فعالیت اهمیت دارد.
   - در صورت وجود، معیار قابل‌سنجش برای تشخیص تکمیل‌شدن آن گام (مثلاً چه چیزی باید تحویل داده شود یا چه سطحی از پیشرفت باید حاصل شود).
   - اگر این چک‌پوینت به یک دوره خاص از لیست دوره‌ها مرتبط است، نام دقیق آن دوره، برگزارکننده/مدرس و مدت آن را در توضیح ذکر کن.
   طول هر description باید حدود ۳ تا ۵ جمله باشد؛ از توضیحات یک‌خطی و ژنریک خودداری کن.

3. یک لیست کامل از تمام دوره‌های آموزشی فعال موجود در سیستم در اختیارت قرار می‌گیرد. وظیفه‌ی خودت این است که از بین این کاتالوگ کامل، برای هر فعالیت (بر اساس عنوان، توضیحات و دسته‌بندی آن فعالیت) مرتبط‌ترین دوره یا دوره‌ها را پیدا کنی و آن‌ها را مستقیماً به‌عنوان یک یا چند چک‌پوینت همان فعالیت پیشنهاد بدهی (مثلاً «ثبت‌نام و گذراندن دوره فلان از فلان مدرس»، «تکمیل بخش نظری دوره فلان»). اگر برای یک فعالیت، هیچ دوره‌ای در کل کاتالوگ به‌اندازه کافی مرتبط نبود، چک‌پوینت‌های آن فعالیت را صرفاً بر اساس ماهیت خودش (بدون ارجاع به دوره) بساز. هر دوره را فقط برای فعالیتی که واقعاً با موضوع آن هم‌خوانی دارد استفاده کن؛ از تکرار یک دوره برای فعالیت‌های نامرتبط خودداری کن.

4. برای هر چک‌پوینت، offset_days مشخص کن: تعداد روزهایی که از شروع همان فعالیت باید بگذرد تا آن چک‌پوینت سررسید شود (عدد صحیح بین ۱ و duration_days همان فعالیت، به ترتیب صعودی در هر فعالیت).

5. اولویت (priority) هر چک‌پوینت را بر اساس اهمیت آن گام در مسیر کلی همان فعالیت تعیین کن.

# نکته حیاتی درباره ایندکس‌ها
هر فعالیت در لیست ورودی یک "index" عددی یکتا دارد. در خروجی، برای هر فعالیت دقیقاً همان index را برگردان تا امکان تطبیق دقیق وجود داشته باشد. هیچ فعالیتی را حذف نکن؛ برای هر index ورودی، دقیقاً یک آبجکت خروجی متناظر باید وجود داشته باشد.

# خروجی
فقط یک JSON معتبر با این ساختار برگردان، بدون هیچ متن اضافه یا فنس مارک‌داون:
{
  "activities": [
    {
      "index": 0,
      "checkpoints": [
        {
          "title": "عنوان کوتاه و مشخص چک‌پوینت",
          "description": "توضیح کامل و چندجمله‌ای طبق قوانین بالا",
          "priority": "low | medium | high",
          "offset_days": 5
        }
      ]
    }
  ]
}
هیچ کلید اضافه‌ای اضافه نکن. عنوان‌ها و توضیحات نباید کلیشه‌ای یا کپی از فعالیت‌های دیگر باشند.
"""



def _build_user_prompt(activities_payload: list, courses: list) -> str:
    activities_json = json.dumps(activities_payload, ensure_ascii=False, indent=2)
    courses_json = json.dumps(courses, ensure_ascii=False, indent=2) if courses else "[]"

    return f"""لیست فعالیت‌های این رودمپ که باید برای هرکدام چک‌پوینت طراحی شود:
{activities_json}

لیست دوره‌های آموزشی مرتبط موجود در سیستم (در صورت وجود، در ساخت چک‌پوینت‌ها از آن‌ها استفاده کن، هرکدام فقط برای فعالیت واقعاً مرتبط):
{courses_json}

با توجه به قوانین system prompt، برای تک‌تک فعالیت‌های بالا (بدون جا انداختن هیچ‌کدام و با همان index) چک‌پوینت‌های مناسب طراحی کن و فقط JSON خروجی نهایی را برگردان."""


# ═══════════════════════════════════════════════════════════════
# تابع اصلی Batch: یک کال برای کل رودمپ
# ═══════════════════════════════════════════════════════════════

def generate_checkpoints_for_roadmap(activities: list) -> dict:
    """
    ساخت چک‌پوینت برای تمام فعالیت‌های یک رودمپ در یک فراخوانی واحد AI.
    """
    if not activities:
        return {}

    index_to_key = {}
    activities_payload = []
    for idx, act in enumerate(activities):
        index_to_key[idx] = act['key']
        activities_payload.append({
            'index': idx,
            'title': act['title'],
            'description': act.get('description') or '',
            'category': act.get('category') or '',
            'stage_title': act.get('stage_title') or '',
            'duration_days': max(1, int(act.get('duration_days') or 1)),
        })

    # ✅ کل کاتالوگ دوره‌های فعال (بدون فیلتر/محدودیت کلمه‌ای) به AI داده می‌شود
    courses = _collect_relevant_courses()

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(activities_payload, courses)},
    ]

    # ✅ چون توضیحات هر چک‌پوینت حالا چندجمله‌ای است و لیست دوره‌ها هم کامل ارسال می‌شود،
    # سقف max_tokens افزایش یافته تا خروجی به‌دلیل کمبود توکن قطع نشود
    estimated_tokens = min(16000, max(4000, len(activities) * 550))

    ai_result_by_index = {}
    try:
        response_text = _call_gpt_api(messages, max_tokens=estimated_tokens)
        cleaned = _strip_code_fences(response_text)
        data = json.loads(cleaned)
        raw_activities = data.get("activities") or []

        for item in raw_activities:
            if not isinstance(item, dict):
                continue
            try:
                idx = int(item.get("index"))
            except (TypeError, ValueError):
                continue
            if idx in index_to_key:
                ai_result_by_index[idx] = item.get("checkpoints") or []

    except Exception:
        logger.exception(
            "خطا در فراخوانی/پارس AI برای ساخت batch چک‌پوینت‌های رودمپ؛ "
            "برای تمام فعالیت‌ها از fallback استفاده می‌شود."
        )
        ai_result_by_index = {}

    valid_priorities = {"low", "medium", "high"}
    result = {}

    for idx, act in enumerate(activities):
        key = act['key']
        start_date = act['start_date']
        duration_days = max(1, int(act.get('duration_days') or 1))
        activity_title = act['title']

        raw_checkpoints = ai_result_by_index.get(idx)

        if not raw_checkpoints:
            logger.warning(
                f"AI برای فعالیت '{activity_title}' (index={idx}) چک‌پوینت معتبر برنگرداند؛ "
                f"از fallback استفاده می‌شود."
            )
            result[key] = _build_fallback_checkpoints(activity_title, start_date, duration_days)
            continue

        checkpoints = []
        for cp in raw_checkpoints:
            if not isinstance(cp, dict):
                continue
            title = (cp.get("title") or "").strip()
            if not title:
                continue

            priority = cp.get("priority")
            if priority not in valid_priorities:
                priority = "medium"

            try:
                offset_days = int(cp.get("offset_days", 1))
            except (TypeError, ValueError):
                offset_days = 1
            offset_days = max(1, min(offset_days, duration_days))

            due_date = start_date + timedelta(days=offset_days)

            checkpoints.append({
                'source_type': 'manual',
                'title': title,
                'description': cp.get("description") or "",
                'priority': priority,
                'due_date': str(due_date),
                'notes': '',
                'source_id': None,
                'source_url': None,
                'is_completed': False,
                'date': None,
                'extra_details': {},
            })

        if not checkpoints:
            logger.warning(
                f"پاسخ AI برای فعالیت '{activity_title}' (index={idx}) پس از پردازش خالی شد؛ "
                f"از fallback استفاده می‌شود."
            )
            checkpoints = _build_fallback_checkpoints(activity_title, start_date, duration_days)
        else:
            checkpoints.sort(key=lambda c: c['due_date'])

        for new_id, cp in enumerate(checkpoints, start=1):
            cp['id'] = new_id

        result[key] = checkpoints

    return result
