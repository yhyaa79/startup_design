# accounts/ai_utils.py

import json
import re
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# تنظیمات API - GapGPT
# ═══════════════════════════════════════════════════════════════

TIMEOUT = 120  # ثانیه

GAPGPT_API_URL = settings.GAPGPT_API_BASE
GAPGPT_API_KEY = settings.GAPGPT_API_KEY
GAPGPT_MODEL = settings.GAPGPT_MODEL_NAME

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
          "title": str,
          "event": str,
          "level": "بین‌المللی" | "ملی" | "قطبی" | "دانشگاهی" | "",
          "result": "برگزیده / جایزه" | "ارائه عادی" | ""
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
'''
def _call_gpt_api(messages: list, max_tokens: int = 4000) -> str:
    """MOCK - برای تست بدون تماس با API واقعی"""
    sample = {
        "profile": {
            "first_name": "علی",
            "last_name": "رضایی",
            "gender": "مرد",
            "marital_status": "مجرد",
            "military_status": "معاف",
            "job_title": "دانشجوی پزشکی",
            "birth_date": "۱۳۷۸/۰۳/۱۵",
            "country": "ایران",
            "city": "تهران",
            "phone": "09121234567",
            "email": "ali@example.com",
            "website": "",
            "national_id": "",
            "orcid": "",
            "proposal_count": 2,
            "proposal_status": "همه در جریان",
            "software_skills": "SPSS, Python",
            "writing_skills": "",
            "clinical_certs": "",
            "clinical_exp": "",
            "procedures": "",
            "native_lang": "فارسی",
            "english_level": "B2",
            "lang_cert": "IELTS 7",
            "other_langs": "",
            "extracurricular": "",
            "goal": "۴۰ امتیازی",
            "specialty": "قلب و عروق",
            "goal_notes": "",
            "service_plan": "در حال گذراندن"
        },
        "social_profiles": [
            {"social_type": "LinkedIn", "url": "https://linkedin.com/in/ali"}
        ],
        "educations": [
            {
                "field": "پزشکی",
                "degree": "دکتری عمومی",
                "university": "دانشگاه علوم پزشکی تهران",
                "uni_type": "تیپ ۱",
                "start_date": "۱۳۹۹/۰۶/۱۵",
                "end_date": "",
                "stage": "اینترنی",
                "current_term": 10,
                "remaining_terms": 4,
                "gpa": 17.5
            }
        ],
        "articles": [
            {
                "title": "بررسی تاثیر ...",
                "journal": "Journal of Cardiology",
                "impact_factor": 3.2,
                "quartile": "Q2",
                "year": 1402,
                "author_rank": 2,
                "total_authors": 4,
                "index": "Scopus"
            }
        ],
        "presentations": [
            {
                "title": "ارائه پوستر",
                "event": "کنگره سالانه قلب",
                "level": "ملی",
                "result": "ارائه عادی"
            }
        ],
        "executive_records": [
            {"title": "دبیر انجمن علمی", "start_date": "۱۴۰۰/۰۱/۰۱", "end_date": "۱۴۰۱/۰۱/۰۱"}
        ],
        "training_courses": [
            {
                "title": "دوره احیای قلبی ریوی",
                "category": "بالینی",
                "status": "تکمیل‌شده",
                "organizer": "دانشگاه علوم پزشکی تهران",
                "date": "۱۴۰۱/۰۵/۱۰",
                "certificate": "دارد",
                "skills_gained": "CPR"
            }
        ]
    }
    return json.dumps(sample, ensure_ascii=False)

'''



def _call_gpt_api(messages: list, max_tokens: int = 4000) -> str:
    """
    فراخوانی واقعی API با تضمین خروجی JSON معتبر
    """
    headers = {
        "Authorization": f"Bearer {GAPGPT_API_KEY}",
        "Content-Type": "application/json",
    }


    payload = {
        "model": GAPGPT_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }


    try:
        response = requests.post(
            GAPGPT_API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]

        finish_reason = data["choices"][0].get("finish_reason")
        if finish_reason == "length":
            logger.warning("خروجی مدل به دلیل کمبود max_tokens قطع شده است.")

        content = _strip_code_fences(content)

        # اعتبارسنجی سریع قبل از برگرداندن
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"خروجی مدل JSON معتبر نیست: {e}\nمتن خام: {content[:500]}")
            raise ValueError(f"پاسخ مدل JSON معتبر نبود: {e}")

        return content

    except requests.exceptions.Timeout:
        logger.error("درخواست به GapGPT API با تایم‌اوت مواجه شد.")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"خطا در فراخوانی GapGPT API: {e}")
        raise
    except (KeyError, IndexError) as e:
        logger.error(f"ساختار پاسخ API غیرمنتظره است: {e}")
        raise


import re

def _strip_code_fences(text: str) -> str:
    """
    حذف بلاک‌های کد مارک‌داون و برگرداندن محتوای داخل آن.
    """
    if not text or not text.strip():
        return text.strip()

    # حذف فنس‌های مارک‌داون با regex (قوی‌تر و تمیزتر)
    text = re.sub(r'^```(?:json|JSON)?\s*\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n```\s*$', '', text)
    
    return text.strip()


def _parse_json_response(response_text: str) -> dict:
    """
    پارس کردن پاسخ JSON از مدل.
    در صورتی که پاسخ داخل بلوک کد باشد، ابتدا آن را استخراج می‌کند.
    """
    # حتل کردن بلوک‌های کد markdown
    text = response_text.strip()
    
    # بررسی بلوک کد ```json ... ```
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        text = json_match.group(1)
    
    # بررسی بلوک کد ``` ... ```
    code_match = re.search(r'```\s*([\s\S]*?)\s*```', text)
    if code_match:
        text = code_match.group(1)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"خطا در پارس JSON: {str(e)}\n\nمتن دریافتی:\n{text}")


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
    import re
    
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

