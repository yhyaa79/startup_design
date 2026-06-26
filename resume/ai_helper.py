# resume/ai_helper.py

import json
import requests
from django.conf import settings

TIMEOUT = getattr(settings, "GAPGPT_TIMEOUT", 60)


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


def generate_resume_summary(profile, purpose="") -> str:
    full_name = getattr(profile, "full_name", "") or getattr(profile.user, "get_full_name", lambda: "")()
    bio = getattr(profile, "bio", "") or getattr(profile, "about", "") or ""
    specialty = getattr(profile, "specialty", "") or getattr(profile, "field_of_study", "") or ""
    educations_count = profile.educations.count() if hasattr(profile, "educations") else 0
    articles_count = profile.articles.count() if hasattr(profile, "articles") else 0
    presentations_count = profile.presentations.count() if hasattr(profile, "presentations") else 0
    executive_records_count = profile.executive_records.count() if hasattr(profile, "executive_records") else 0
    training_courses_count = profile.training_courses.count() if hasattr(profile, "training_courses") else 0

    system_message = {
        "role": "system",
        "content": (
            "شما یک دستیار حرفه‌ای برای نگارش خلاصه رزومه فارسی هستید. "
            "فقط یک پاراگراف حرفه‌ای، روان و رسمی به زبان فارسی تولید کنید. "
            "متن باید کوتاه، دقیق، بدون بولت و مناسب ابتدای رزومه باشد."
        ),
    }

    user_message = {
        "role": "user",
        "content": (
            f"نام: {full_name}\n"
            f"هدف رزومه: {purpose}\n"
            f"حوزه/تخصص: {specialty}\n"
            f"توضیحات پروفایل: {bio}\n"
            f"تعداد سوابق تحصیلی: {educations_count}\n"
            f"تعداد مقالات: {articles_count}\n"
            f"تعداد ارائه‌ها: {presentations_count}\n"
            f"تعداد سوابق اجرایی: {executive_records_count}\n"
            f"تعداد دوره‌های آموزشی: {training_courses_count}\n\n"
            "بر اساس اطلاعات بالا یک خلاصه حرفه‌ای 3 تا 5 جمله‌ای برای رزومه بنویس."
        ),
    }

    return _call_gpt_api([system_message, user_message], max_tokens=500).strip()
