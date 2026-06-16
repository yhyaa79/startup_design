# accounts/ai_utils.py

import json
import re
import requests
from django.conf import settings



TIMEOUT = getattr(settings, "GAPGPT_TIMEOUT", 60)

# ═══════════════════════════════════════════════════════════════
# تنظیمات API - GapGPT
# ═══════════════════════════════════════════════════════════════



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



def _call_gpt_api(messages: list, max_tokens: int = 2000) -> str:
    if settings.GAPGPT_API_KEY == "YOUR_API_KEY_HERE" or not settings.GAPGPT_API_KEY:
        raise ValueError("API Key تنظیم نشده است.")

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

    try:
        response = requests.post(
            f"{settings.GAPGPT_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=(10, TIMEOUT),
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        raise TimeoutError("زمان انتظار برای پاسخ API به پایان رسید.")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("خطا در اتصال به API.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"خطای HTTP از API: {e.response.status_code} - {e.response.text}")
    except (KeyError, IndexError, ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"پاسخ API نامعتبر است: {str(e)}")






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
    system_prompt = """تو یک دستیار هوشمند برای استخراج اطلاعات از متن‌های فارسی هستیت.
وظیفت این است که متن زیر را بخوانی و اطلاعات موجود در آن را به صورت ساختاریافته استخراج کنی.

قوانین مهم:
1. فقط اطلاعاتی را استخراج کن که صراحتاً در متن ذکر شده‌اند.
2. اگر اطلاعاتی وجود ندارد، آن فیلد را خالی ("") یا null بگذار.
3. تاریخ‌ها را به صورت جلالی بنویس (مثال: 1402/03/15).
4. اعداد را به صورت انگلیسی بنویس.
5. فقط و فقط یک شیء JSON خالص برگردان، بدون هیچ توضیح اضافی."""

    user_prompt = f"""لطفاً اطلاعات زیر را از متن استخراج کن و به صورت JSON برگردان:

{text}

خروجی باید دقیقاً با این ساختار باشد:
{{
  "profile": {{
    "first_name": "",
    "last_name": "",
    "gender": "",
    "marital_status": "",
    "military_status": "",
    "job_title": "",
    "birth_date": "",
    "country": "",
    "city": "",
    "phone": "",
    "email": "",
    "website": "",
    "national_id": "",
    "orcid": "",
    "proposal_count": null,
    "proposal_status": "",
    "software_skills": "",
    "writing_skills": "",
    "clinical_certs": "",
    "clinical_exp": "",
    "procedures": "",
    "native_lang": "",
    "english_level": "",
    "lang_cert": "",
    "other_langs": "",
    "extracurricular": "",
    "goal": "",
    "specialty": "",
    "goal_notes": "",
    "service_plan": ""
  }},
  "social_profiles": [],
  "educations": [],
  "articles": [],
  "presentations": [],
  "executive_records": [],
  "training_courses": []
}}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response_text = _call_gpt_api(messages, max_tokens=2000)
    return _parse_json_response(response_text)











