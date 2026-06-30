# accounts/ai_utils.py

import json
import re
import requests
from django.conf import settings
from .models import Profile



TIMEOUT = getattr(settings, "GAPGPT_TIMEOUT", 60)


# ═══════════════════════════════════════════════════════════════
# ساختار داده‌های مورد انتظار (Schema)
# ═══════════════════════════════════════════════════════════════

"""
    Extract structured profile data from raw Persian text using an LLM.

    Returns a dict matching the schema below. All fields are optional unless marked required.

    Schema:
    {
      "profile": {
        "first_name": str,                    # required
        "last_name": str,                     # required
        "gender": "مرد" | "زن",              # required
        "marital_status": "مجرد" | "متأهل" | "",
        "military_status": "" | "معاف" | "طرح پزشکی" | "سرباز" | "پایان خدمت",
        "job_title": str,
        "birth_date": str,                    # Jalali e.g. "۱۳۷۸/۰۳/۱۵"
        "country": str,
        "city": str,
        "phone": str,
        "email": str,
        "website": str,
        "national_id": str,
        "orcid": str,
        "proposal_count": int | null,
        "proposal_status": "" | "همه در جریان" | "همه خاتمه‌یافته" | "ترکیبی",
        "software_skills": str,
        "writing_skills": str,
        "clinical_certs": str,
        "clinical_exp": str,
        "procedures": str,
        "native_lang": str,
        "english_level": "" | "A1" | "A2" | "B1" | "B2" | "C1" | "C2",
        "lang_cert": str,
        "other_langs": str,
        "extracurricular": str,
        "goal": "استعداد درخشان" | "۴۰ امتیازی" | "هیات علمی" | "ریسرچ پوزیشن / فلوشیپ خارج",  # required
        "specialty": str,
        "goal_notes": str,
        "service_plan": "" | "مشمول نیستم" | "در حال گذراندن" | "پایان یافته"
      },
      "social_profiles": [
        {
          "social_type": "LinkedIn" | "GitHub" | "Google Scholar" | "ResearchGate" | "Dribbble" | "Twitter / X" | "Instagram" | "سایر",
          "url": str
        }
      ],
      "educations": [
        {
          "field": "پزشکی" | "دندان‌پزشکی" | "داروسازی" | "پرستاری" | "فیزیوتراپی" | "سایر",
          "degree": "کارشناسی" | "کارشناسی ارشد" | "دکتری عمومی" | "دکتری تخصصی",
          "university": str,
          "uni_type": "تیپ ۱" | "تیپ ۲" | "تیپ ۳" | "",
          "start_date": str,   # Jalali
          "end_date": str,     # Jalali or ""
          "stage": "علوم پایه" | "فیزیوپات" | "استاژری" | "اینترنی" | "فارغ‌التحصیل" | "",
          "current_term": int | null,     # 1–20
          "remaining_terms": int | null,  # 0–20
          "gpa": float | null             # 0–20
        }
      ],
      "articles": [
        {
          "title": str,
          "journal": str,
          "impact_factor": float | null,
          "quartile": "Q1" | "Q2" | "Q3" | "Q4" | "",
          "year": int | null,   # Jalali year e.g. 1402
          "author_rank": int | null,
          "total_authors": int | null,
          "index": "ISI / Web of Science" | "Scopus" | "PubMed" | "ISI + Scopus" | "سایر" | ""
        }
      ],
        "presentations": [
            {
                "title": "",
                "event": "",
                "level": "",   # بین‌المللی | ملی | قطبی | دانشگاهی
                "result": ""   # برگزیده / جایزه | ارائه عادی
            }
        ],
      "executive_records": [
        {
          "title": str,
          "start_date": str,  # Jalali
          "end_date": str     # Jalali or ""
        }
      ],
      "training_courses": [
        {
          "title": str,
          "category": "پژوهشی" | "بالینی" | "آموزشی" | "نرم‌افزاری" | "زبان" | "سایر" | "",
          "status": "تکمیل‌شده" | "در حال گذراندن" | "ناتمام" | "",
          "organizer": str,
          "date": str,        # Jalali
          "certificate": "دارد" | "ندارد" | "",
          "skills_gained": str
        }
      ]
    }
"""


# ═══════════════════════════════════════════════════════════════
# تابع کمکی برای ارتباط با API
# ═══════════════════════════════════════════════════════════════

import logging
import time

logger = logging.getLogger(__name__)

# می‌تونی در settings تعریفش کنی
DEFAULT_TIMEOUT = 60   # read timeout
CONNECT_TIMEOUT = 10   # connect timeout
MAX_RETRIES = 2


def _call_gpt_api(messages: list, max_tokens: int = 1000) -> str:
    """
    Calls GapGPT Chat Completion API with retry & proper error handling.
    """

    if settings.GAPGPT_API_KEY == "YOUR_API_KEY_HERE" or not settings.GAPGPT_API_KEY:
        logger.error("GAPGPT_API_KEY is not configured.")
        raise ValueError("API Key تنظیم نشده است.")

    url = f"{settings.GAPGPT_API_BASE}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GAPGPT_API_KEY}",
    }

    payload = {
        "model": settings.GAPGPT_MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Calling GPT API (attempt %s/%s)", attempt, MAX_RETRIES)

            start_time = time.monotonic()

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=(CONNECT_TIMEOUT, DEFAULT_TIMEOUT),
            )

            elapsed = time.monotonic() - start_time
            logger.info("GPT API responded in %.2f seconds", elapsed)

            # اگر موفق بود
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]

            # اگر 5xx بود → retry
            if response.status_code in (502, 503, 504):
                logger.warning(
                    "Upstream error %s on attempt %s",
                    response.status_code,
                    attempt,
                )

                if attempt == MAX_RETRIES:
                    raise TimeoutError(
                        "سرویس هوش مصنوعی موقتاً در دسترس نیست. لطفاً چند دقیقه بعد دوباره تلاش کنید."
                    )

                time.sleep(2 ** attempt)  # exponential backoff
                continue

            # سایر خطاهای HTTP
            logger.error("HTTP error %s: %s", response.status_code, response.text)
            raise ValueError(
                f"خطای سرویس هوش مصنوعی: {response.status_code}"
            )

        except requests.exceptions.ReadTimeout:
            logger.warning("Read timeout on attempt %s", attempt)

            if attempt == MAX_RETRIES:
                raise TimeoutError(
                    "سرویس هوش مصنوعی دیر پاسخ داد. لطفاً دوباره تلاش کنید."
                )

            time.sleep(2 ** attempt)

        except requests.exceptions.ConnectionError:
            logger.exception("Connection error while calling GPT API.")
            raise ConnectionError("خطا در اتصال به سرویس هوش مصنوعی.")

        except (KeyError, IndexError, json.JSONDecodeError):
            logger.exception("Invalid API response structure.")
            raise ValueError("پاسخ دریافتی از سرویس هوش مصنوعی نامعتبر است.")

        except Exception:
            logger.exception("Unexpected error in _call_gpt_api.")
            raise


def _parse_json_response(response_text: str) -> dict:
    text = response_text.strip()

    # بررسی بلوک کد ```json ... ```
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        text = json_match.group(1)

    # بررسی بلوک کد ``` ... ```
    code_match = re.search(r'```\s*([\s\S]*?)\s*```', text)
    if code_match:
        text = code_match.group(1)

    return json.loads(text)


# ═══════════════════════════════════════════════════════════════
# تابع اصلی: استخراج پروفایل از متن
# ═══════════════════════════════════════════════════════════════


def extract_profile_from_text(text: str) -> dict:
    """
    استخراج داده‌های ساختاریافته پروفایل از متن خام فارسی با استفاده از LLM.

    Args:
        text: متن خام شامل اطلاعات پروفایل کاربر

    Returns:
        دیکشنری با ساختار زیر:
        {
            "profile": {...},
            "social_profiles": [...],
            "educations": [...],
            "articles": [...],
            "presentations": [...],
            "executive_records": [...],
            "training_courses": [...]
        }
    """
    system_prompt = """تو یک دستیار هوشمند برای استخراج اطلاعات از متن‌های فارسی هستیت.
وظیفت این است که متن زیر را بخوانی و اطلاعات موجود در آن را به صورت ساختاریافته استخراج کنی.

قوانین مهم:
1. فقط اطلاعاتی را استخراج کن که صراحتاً در متن ذکر شده‌اند.
2. اگر اطلاعاتی وجود ندارد، آن فیلد را خالی ("") یا null بگذار.
3. تاریخ‌ها را به صورت جلالی بنویس (مثال: ۱۴۰۲/۰۳/۱۵).
4. اعداد را به صورت انگلیسی بنویس (مثال: 1402 نه ۱۴۰۲).
5. فقط و فقط یک شیء JSON خالص برگردان، بدون هیچ توضیح اضافی."""

    user_prompt = f"""لطفاً اطلاعات زیر را از متن استخراج کن و به صورت JSON برگردان:

{text}

خروجی باید دقیقاً با این ساختار باشد:
{{
  "profile": {{
    "first_name": "نام",
    "last_name": "نام خانوادگی",
    "gender": "مرد یا زن",
    "marital_status": "مجرد یا متأهل یا خالی",
    "military_status": "معاف یا طرح پزشکی یا سرباز یا پایان خدمت یا خالی",
    "job_title": "عنوان شغلی",
    "birth_date": "تاریخ تولد جلالی",
    "country": "کشور",
    "city": "شهر",
    "phone": "شماره تلفن",
    "email": "ایمیل",
    "website": "وب‌سایت",
    "national_id": "کد ملی",
    "orcid": "شناسه ORCID",
    "proposal_count": عدد یا null,
    "proposal_status": "همه در جریان یا همه خاتمه‌یافته یا ترکیبی یا خالی",
    "software_skills": "مهارت‌های نرم‌افزاری",
    "writing_skills": "مهارت‌های نگارشی",
    "clinical_certs": "گواهینامه‌های بالینی",
    "clinical_exp": "سوابق بالینی",
    "procedures": "مهارت‌های پروسیجرال",
    "native_lang": "زبان مادری",
    "english_level": "A1 یا A2 یا B1 یا B2 یا C1 یا C2 یا خالی",
    "lang_cert": "مدرک زبان",
    "other_langs": "سایر زبان‌ها",
    "extracurricular": "فعالیت‌های فوق برنامه",
    "goal": "استعداد درخشان یا ۴۰ امتیازی یا هیات علمی یا ریسرچ پوزیشن / فلوشیپ خارج",
    "specialty": "حوزه تخصصی",
    "goal_notes": "توضیحات اهداف",
    "service_plan": "مشمول نیستم یا در حال گذراندن یا پایان یافته یا خالی"
  }},
  "social_profiles": [
    {{"social_type": "LinkedIn یا GitHub یا Google Scholar یا ResearchGate یا Dribbble یا Twitter / X یا Instagram یا سایر", "url": "لینک"}}
  ],
  "educations": [
    {{"field": "پزشکی یا دندان‌پزشکی یا داروسازی یا پرستاری یا فیزیوتراپی یا سایر", "degree": "کارشناسی یا کارشناسی ارشد یا دکتری عمومی یا دکتری تخصصی", "university": "نام دانشگاه", "uni_type": "تیپ ۱ یا تیپ ۲ یا تیپ ۳ یا خالی", "start_date": "تاریخ شروع جلالی", "end_date": "تاریخ پایان جلالی", "stage": "علوم پایه یا فیزیوپات یا استاژری یا اینترنی یا فارغ‌التحصیل یا خالی", "current_term": عدد یا null, "remaining_terms": عدد یا null, "gpa": عدد یا null}}
  ],
  "articles": [
    {{"title": "عنوان مقاله", "journal": "نام ژورنال", "impact_factor": عدد یا null, "quartile": "Q1 یا Q2 یا Q3 یا Q4 یا خالی", "year": عدد یا null, "author_rank": عدد یا null, "total_authors": عدد یا null, "index": "ISI / Web of Science یا Scopus یا PubMed یا ISI + Scopus یا سایر یا خالی"}}
  ],
  "presentations": [
    {{"title": "عنوان ارائه", "event": "نام رویداد", "level": "بین‌المللی یا ملی یا قطبی یا دانشگاهی یا خالی", "result": "برگزیده / جایزه یا ارائه عادی یا خالی"}}
  ],
  "executive_records": [
    {{"title": "عنوان سمت", "start_date": "تاریخ شروع جلالی", "end_date": "تاریخ پایان جلالی"}}
  ],
  "training_courses": [
    {{"title": "عنوان دوره", "category": "پژوهشی یا بالینی یا آموزشی یا نرم‌افزاری یا زبان یا سایر یا خالی", "status": "تکمیل‌شده یا در حال گذراندن یا ناتمام یا خالی", "organizer": "برگزارکننده", "date": "تاریخ جلالی", "certificate": "دارد یا ندارد یا خالی", "skills_gained": "مهارت‌های کسب‌شده"}}
  ]
}}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response_text = _call_gpt_api(messages, max_tokens=4000)
    result = _parse_json_response(response_text)

    return result



def _sanitize_profile_data(data: dict) -> dict:
    """
    تبدیل مقادیر None به مقدار مناسب بر اساس نوع فیلد مدل،
    تا با محدودیت‌های NOT NULL دیتابیس تطابق داشته باشد.
    """
    numeric_null_fields = {'proposal_count'}

    text_null_fields = set()
    for field in Profile._meta.get_fields():
        if hasattr(field, 'blank') and field.blank and not field.null:
            text_null_fields.add(field.name)

    cleaned = {}
    for key, value in data.items():
        if value is None:
            cleaned[key] = None if key in numeric_null_fields else ''
        else:
            cleaned[key] = value
    return cleaned