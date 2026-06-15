# roadmap/services/ai_roadmap.py

import json
import os
import re
import requests

from django.conf import settings

from roadmap.models import Activity
from roadmap.services.profile_data import _collect_profile_data


# ═══════════════════════════════════════════════════════════════
# تنظیمات API
# ═══════════════════════════════════════════════════════════════

API_BASE = "https://api.gapgpt.app/v1"
API_KEY = "sk-pIFI1SNGCgPOiY2vDP3kZAjVK0omTdYv7zBBbs32tsg9pgYg"

MODEL_NAME = "gapgpt-qwen-3.5"
TIMEOUT = 120  # ثانیه

# ═══════════════════════════════════════════════════════════════
# تابع کمکی ارتباط با API
# ═══════════════════════════════════════════════════════════════

def _call_gpt_api(messages: list, max_tokens: int = 4000) -> str:
    """
    ارسال درخواست به API و دریافت پاسخ مدل.
    """

    if not API_KEY:
        raise ValueError(
            "API Key تنظیم نشده است. "
            "لطفاً GAPGPT_API_KEY را در settings یا env تنظیم کنید."
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.25,
    }

    try:
        response = requests.post(
            f"{API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.ConnectionError:
        raise ConnectionError("خطا در اتصال به API. اتصال اینترنت یا دسترسی سرور را بررسی کنید.")

    except requests.exceptions.Timeout:
        raise TimeoutError("زمان انتظار برای پاسخ API به پایان رسید.")

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else ""
        response_text = e.response.text if e.response else ""
        raise ValueError(f"خطای HTTP از API: {status_code} - {response_text}")

    except (KeyError, IndexError) as e:
        raise ValueError(f"ساختار پاسخ API نامعتبر است: {str(e)}")


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
# فایل prompt مربوط به هدف
# ═══════════════════════════════════════════════════════════════

def _load_goal_prompt(goal: str) -> str:
    """
    بارگذاری فایل راهنمای هدف کاربر از مسیر roadmap/prompts.
    """

    goal_map = {
        "استعداد درخشان": "estedad_darakhshan.md",
        "۴۰ امتیازی": "40_emtiaz.md",
        "40 امتیازی": "40_emtiaz.md",
        "هیات علمی": "heyat_elmi.md",
        "هیأت علمی": "heyat_elmi.md",
        "ریسرچ پوزیشن / فلوشیپ خارج": "research_position.md",
    }

    filename = goal_map.get(goal)
    if not filename:
        return ""

    # چون این فایل داخل roadmap/services است، prompts داخل roadmap/prompts قرار می‌گیرد
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompts",
        filename,
    )

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


# ═══════════════════════════════════════════════════════════════
# محاسبه پیشرفت
# ═══════════════════════════════════════════════════════════════

def _calculate_progress(profile_data: dict, goal: str) -> dict:
    """
    محاسبه درصد پیشرفت کاربر بر اساس اطلاعات پروفایل و هدف.
    """

    progress = {
        "overall_percent": 0,
        "completed_items": [],
        "missing_items": [],
        "score_breakdown": {},
        "impact_analysis": {},
    }

    profile = profile_data.get("profile", {})
    educations = profile_data.get("educations", [])
    articles = profile_data.get("articles", [])
    presentations = profile_data.get("presentations", [])
    courses = profile_data.get("training_courses", [])

    if goal == "استعداد درخشان":
        score = 0
        score_details = {}

        current_degree = ""
        current_stage = ""

        for edu in educations:
            if edu.get("degree"):
                current_degree = edu.get("degree")
            if edu.get("stage"):
                current_stage = edu.get("stage")

        if current_degree == "کارشناسی":
            min_score = 55
        elif current_degree in ["دکتری عمومی", "کارشناسی ارشد"]:
            min_score = 95
        elif current_degree == "دکتری تخصصی":
            min_score = 115
        else:
            min_score = 95

        article_score = 0

        for article in articles:
            index = article.get("index", "")
            impact_factor = article.get("impact_factor") or 0

            if index in ["ISI / Web of Science", "ISI + Scopus"]:
                base_score = 25
                if impact_factor and impact_factor > 3:
                    base_score += min(int(impact_factor), 25)
                article_score += base_score
                progress["completed_items"].append(f"مقاله ISI: {article.get('title', '')[:50]}")

            elif index in ["Scopus", "PubMed", "Medline"]:
                article_score += 15
                progress["completed_items"].append(f"مقاله Scopus/PubMed: {article.get('title', '')[:50]}")

            else:
                article_score += 10
                progress["completed_items"].append(f"مقاله: {article.get('title', '')[:50]}")

        article_score = min(article_score, 50)
        score += article_score
        score_details["مقالات"] = article_score

        progress["impact_analysis"]["مقالات"] = {
            "score": article_score,
            "max_possible": 50,
            "impact_percent": min(int((article_score / 50) * 100), 100),
            "description": "مقالات ISI/Scopus بیشترین اثر را دارند.",
        }

        if current_degree == "دکتری تخصصی":
            thesis_score = 10
            score += thesis_score
            score_details["پایان‌نامه"] = thesis_score
            progress["completed_items"].append("پایان‌نامه تخصصی")

        presentation_score = 0

        for pres in presentations:
            level = pres.get("level", "")
            result = pres.get("result", "")

            if level == "بین‌المللی":
                presentation_score += 3
                progress["completed_items"].append(f"ارائه بین‌المللی: {pres.get('title', '')[:40]}")
            else:
                presentation_score += 1
                progress["completed_items"].append(f"ارائه داخلی: {pres.get('title', '')[:40]}")

            if result == "برگزیده / جایزه":
                presentation_score += 2
                progress["completed_items"].append("مقاله یا ارائه برگزیده در کنگره")

        presentation_score = min(presentation_score, 15)
        score += presentation_score
        score_details["ارائه‌ها"] = presentation_score

        progress["impact_analysis"]["ارائه‌ها"] = {
            "score": presentation_score,
            "max_possible": 15,
            "impact_percent": min(int((presentation_score / 15) * 100), 100),
            "description": "ارائه در کنگره‌های بین‌المللی اثر بیشتری دارد.",
        }

        proposal_count = profile.get("proposal_count") or 0
        research_score = min(proposal_count * 5, 15)
        score += research_score
        score_details["طرح‌های تحقیقاتی"] = research_score

        if proposal_count:
            progress["completed_items"].append(f"{proposal_count} طرح تحقیقاتی")

        extracurricular = profile.get("extracurricular", "")

        if extracurricular:
            committee_score = 10
            score += committee_score
            score_details["کمیته تحقیقات"] = committee_score
            progress["completed_items"].append("فعالیت در کمیته یا انجمن علمی")

        progress["overall_percent"] = min(int((score / min_score) * 100), 100)
        progress["score_breakdown"] = score_details
        progress["score_breakdown"]["total_score"] = score
        progress["score_breakdown"]["min_score"] = min_score
        progress["score_breakdown"]["degree"] = current_degree
        progress["score_breakdown"]["stage"] = current_stage
        progress["score_breakdown"]["remaining_to_goal"] = max(0, min_score - score)

        if article_score == 0:
            progress["missing_items"].append("انتشار مقاله علمی")
        if presentation_score == 0:
            progress["missing_items"].append("ارائه در کنگره")
        if proposal_count == 0:
            progress["missing_items"].append("همکاری در طرح تحقیقاتی")

    elif goal in ["۴۰ امتیازی", "40 امتیازی"]:
        score = 0
        score_details = {}

        edu_score = 0
        gpa = 0

        for edu in educations:
            if edu.get("gpa"):
                gpa = edu.get("gpa")
                break

        if gpa >= 18:
            edu_score += 10
            progress["completed_items"].append(f"معدل برتر: {gpa}")
        elif gpa >= 17:
            edu_score += 8
            progress["completed_items"].append(f"معدل خوب: {gpa}")
        elif gpa >= 16:
            edu_score += 5
            progress["completed_items"].append(f"معدل قابل قبول: {gpa}")

        edu_score = min(edu_score, 20)
        score += edu_score
        score_details["آموزشی"] = edu_score

        article_score = 0

        for article in articles:
            index = article.get("index", "")
            author_rank = article.get("author_rank") or 99

            if index in ["ISI / Web of Science", "ISI + Scopus", "PubMed", "Scopus"]:
                if author_rank == 1:
                    article_score += 7
                else:
                    article_score += 4
                progress["completed_items"].append(f"مقاله معتبر: {article.get('title', '')[:40]}")
            else:
                article_score += 2
                progress["completed_items"].append(f"مقاله: {article.get('title', '')[:40]}")

        article_score = min(article_score, 15)

        pres_score = 0

        for pres in presentations:
            if pres.get("level") == "بین‌المللی":
                pres_score += 2
            else:
                pres_score += 1.5
            progress["completed_items"].append(f"ارائه علمی: {pres.get('title', '')[:40]}")

        pres_score = min(pres_score, 5)

        proposal_count = profile.get("proposal_count") or 0
        proposal_score = min(proposal_count * 3, 5)

        research_score = min(article_score + pres_score + proposal_score, 20)
        score += research_score

        score_details["مقالات"] = article_score
        score_details["ارائه‌ها"] = pres_score
        score_details["طرح‌ها"] = proposal_score
        score_details["پژوهشی"] = research_score

        social_score = 0
        extracurricular = profile.get("extracurricular", "")

        if extracurricular:
            social_score += 3
            progress["completed_items"].append(f"فعالیت فردی/اجتماعی: {extracurricular[:50]}")

        social_score = min(social_score, 10)
        score += social_score
        score_details["فردی-اجتماعی-فرهنگی"] = social_score

        min_score = 40

        progress["overall_percent"] = min(int((score / min_score) * 100), 100)
        progress["score_breakdown"] = score_details
        progress["score_breakdown"]["total_score"] = score
        progress["score_breakdown"]["min_score"] = min_score
        progress["score_breakdown"]["remaining"] = max(0, min_score - score)

        progress["impact_analysis"] = {
            "آموزشی": {
                "score": edu_score,
                "max_possible": 20,
                "impact_percent": min(int((edu_score / 20) * 100), 100),
                "description": "معدل و فعالیت‌های آموزشی اثر مهمی دارند.",
            },
            "پژوهشی": {
                "score": research_score,
                "max_possible": 20,
                "impact_percent": min(int((research_score / 20) * 100), 100),
                "description": "مقاله، طرح تحقیقاتی و ارائه علمی بیشترین اثر را دارند.",
            },
            "فردی-اجتماعی-فرهنگی": {
                "score": social_score,
                "max_possible": 10,
                "impact_percent": min(int((social_score / 10) * 100), 100),
                "description": "فعالیت‌های اجتماعی و داوطلبانه امتیاز تکمیلی ایجاد می‌کنند.",
            },
        }

        if article_score == 0:
            progress["missing_items"].append("انتشار مقاله علمی")
        if pres_score == 0:
            progress["missing_items"].append("ارائه در کنگره")
        if proposal_count == 0:
            progress["missing_items"].append("همکاری در طرح تحقیقاتی")
        if not extracurricular:
            progress["missing_items"].append("فعالیت فردی، اجتماعی یا داوطلبانه")

    elif goal in ["هیات علمی", "هیأت علمی"]:
        score = 0

        has_phd = any(edu.get("degree") == "دکتری تخصصی" for edu in educations)

        if has_phd:
            score += 20
            progress["completed_items"].append("دارای دکتری تخصصی")
        else:
            progress["missing_items"].append("اتمام دوره تخصصی یا دکتری تخصصی")

        isi_articles = [
            a for a in articles
            if a.get("index") in ["ISI / Web of Science", "Scopus", "ISI + Scopus"]
        ]

        if len(isi_articles) >= 3:
            score += 30
            progress["completed_items"].append(f"{len(isi_articles)} مقاله ISI/Scopus")
        elif isi_articles:
            score += 15
            progress["completed_items"].append(f"{len(isi_articles)} مقاله ISI/Scopus")
            progress["missing_items"].append("افزایش تعداد مقالات معتبر تا حداقل ۳ مقاله")
        else:
            progress["missing_items"].append("انتشار مقاله ISI/Scopus")

        proposal_count = profile.get("proposal_count") or 0

        if proposal_count:
            score += 20
            progress["completed_items"].append(f"{proposal_count} پروپوزال یا طرح تحقیقاتی")
        else:
            progress["missing_items"].append("نوشتن پروپوزال تحقیقاتی")

        if profile_data.get("executive_records"):
            score += 15
            progress["completed_items"].append("سوابق اجرایی دانشگاهی")
        else:
            progress["missing_items"].append("کسب سوابق اجرایی دانشگاهی")

        if profile.get("writing_skills"):
            score += 15
            progress["completed_items"].append("مهارت نگارش مقاله/پروپوزال")
        else:
            progress["missing_items"].append("تقویت مهارت نگارش علمی")

        progress["overall_percent"] = min(score, 100)
        progress["score_breakdown"]["score"] = score

    elif goal == "ریسرچ پوزیشن / فلوشیپ خارج":
        score = 0

        english_level = profile.get("english_level", "")

        if english_level in ["B2", "C1", "C2"]:
            score += 25
            progress["completed_items"].append(f"سطح زبان مناسب: {english_level}")
        elif english_level in ["A2", "B1"]:
            score += 10
            progress["completed_items"].append(f"سطح زبان نیازمند تقویت: {english_level}")
            progress["missing_items"].append("افزایش سطح زبان تا B2 یا بالاتر")
        else:
            progress["missing_items"].append("تقویت زبان انگلیسی")

        article_count = len(articles)

        if article_count >= 2:
            score += 25
            progress["completed_items"].append(f"{article_count} مقاله منتشرشده")
        elif article_count == 1:
            score += 15
            progress["completed_items"].append("۱ مقاله منتشرشده")
            progress["missing_items"].append("انتشار حداقل یک مقاله دیگر")
        else:
            progress["missing_items"].append("نوشتن و انتشار مقاله")

        if profile_data.get("executive_records") or courses:
            score += 20
            progress["completed_items"].append("سوابق تحقیقاتی یا آموزشی مرتبط")
        else:
            progress["missing_items"].append("کسب سوابق تحقیقاتی")

        if presentations:
            score += 15
            progress["completed_items"].append(f"{len(presentations)} ارائه علمی")
        else:
            progress["missing_items"].append("ارائه در کنفرانس")

        proposal_count = profile.get("proposal_count") or 0

        if proposal_count:
            score += 15
            progress["completed_items"].append("دارای پروپوزال یا طرح تحقیقاتی")
        else:
            progress["missing_items"].append("نوشتن پروپوزال تحقیقاتی")

        progress["overall_percent"] = min(score, 100)
        progress["score_breakdown"]["score"] = score

    else:
        # حالت عمومی
        score = 0

        if articles:
            score += 25
            progress["completed_items"].append("دارای مقاله علمی")
        else:
            progress["missing_items"].append("نوشتن مقاله علمی")

        if presentations:
            score += 15
            progress["completed_items"].append("دارای ارائه علمی")
        else:
            progress["missing_items"].append("ارائه در همایش یا کنگره")

        if courses:
            score += 20
            progress["completed_items"].append("دارای دوره آموزشی")
        else:
            progress["missing_items"].append("گذراندن دوره‌های آموزشی کلیدی")

        if profile.get("software_skills"):
            score += 20
            progress["completed_items"].append("دارای مهارت نرم‌افزاری")
        else:
            progress["missing_items"].append("یادگیری نرم‌افزارهای پژوهشی")

        if profile.get("english_level"):
            score += 20
            progress["completed_items"].append("دارای سطح زبان ثبت‌شده")
        else:
            progress["missing_items"].append("تقویت زبان انگلیسی")

        progress["overall_percent"] = min(score, 100)
        progress["score_breakdown"]["score"] = score

    return progress


# ═══════════════════════════════════════════════════════════════
# دریافت فعالیت‌های موجود برای اجبار مدل به استفاده از دیتابیس
# ═══════════════════════════════════════════════════════════════

def _get_available_activities_for_prompt() -> list:
    """
    لیست فعالیت‌های فعال موجود در دیتابیس.
    مدل باید فقط از همین عنوان‌ها استفاده کند تا StageActivity بدون مشکل ذخیره شود.
    """

    activities = Activity.objects.filter(is_active=True).order_by("category", "title")

    return [
        {
            "title": activity.title,
            "category": activity.category,
            "field": activity.field,
            "duration_days": activity.duration_days,
            "difficulty_level": activity.difficulty_level,
            "resume_output": activity.resume_output,
            "prerequisites": activity.prerequisites,
            "resources": activity.resources,
        }
        for activity in activities
    ]


# ═══════════════════════════════════════════════════════════════
# تولید نقشه راه خام توسط مدل
# ═══════════════════════════════════════════════════════════════

def generate_roadmap(profile_data: dict, target_goal: str = None) -> dict:
    """
    تولید نقشه راه شخصی‌سازی‌شده با AI.
    خروجی این تابع ساختار تحلیلی دارد و بعداً به ساختار مدل‌های Django تبدیل می‌شود.
    """

    profile_json = json.dumps(profile_data, ensure_ascii=False, indent=2)

    goal_prompt = ""
    if target_goal:
        goal_prompt = _load_goal_prompt(target_goal)

    goal_for_progress = target_goal or profile_data.get("profile", {}).get("goal", "")
    progress = _calculate_progress(profile_data, goal_for_progress)
    progress_json = json.dumps(progress, ensure_ascii=False, indent=2)

    available_activities = _get_available_activities_for_prompt()
    available_activities_json = json.dumps(available_activities, ensure_ascii=False, indent=2)

    system_prompt = """
تو یک مشاور حرفه‌ای ارشد برای دانشجویان و متخصصان علوم پزشکی هستی.

وظیفه تو:
بر اساس پروفایل کاربر، هدف نهایی، تحلیل کمی، فایل راهنمای هدف و فقط با استفاده از فعالیت‌های موجود در دیتابیس، یک نقشه راه شخصی‌سازی‌شده تولید کن.

قوانین بسیار مهم:
1. فقط JSON خالص برگردان.
2. هیچ توضیحی خارج از JSON ننویس.
3. عنوان فعالیت‌ها در sub_tasks باید دقیقاً برابر با یکی از title های available_activities باشد.
4. اگر فعالیت مناسبی در لیست نبود، نزدیک‌ترین فعالیت موجود را انتخاب کن.
5. از ساختن عنوان فعالیت جدید خودداری کن.
6. مراحل باید واقع‌بینانه، ترتیبی و قابل اجرا باشند.
7. تعداد مراحل بین 4 تا 8 مرحله باشد.
8. هر مرحله بین 2 تا 5 فعالیت داشته باشد.
"""

    output_schema = """
ساختار خروجی JSON دقیقاً به این شکل باشد:
{
  "roadmap": {
    "title": "عنوان نقشه راه",
    "description": "توضیحات کلی",
    "goal": "هدف نهایی",
    "steps": [
      {
        "order": 1,
        "title": "عنوان مرحله",
        "description": "توضیحات مرحله",
        "objectives": "اهداف مرحله",
        "priority": "critical/high/medium/low",
        "estimated_duration": "مدت زمان تخمینی",
        "status": "completed/available/in_progress",
        "impact_score": 1,
        "sub_tasks": [
          {
            "title": "دقیقاً یکی از title های available_activities",
            "is_done": false,
            "notes": "توضیح کوتاه درباره چرایی انجام این فعالیت"
          }
        ],
        "resources": [
          {
            "title": "عنوان منبع",
            "resource_type": "کتاب/دوره/مقاله/وب‌سایت",
            "url": "",
            "description": "توضیح"
          }
        ]
      }
    ]
  },
  "quantitative_analysis": {
    "overall_percent": 0,
    "total_score": 0,
    "min_score": 0,
    "remaining_score": 0,
    "sections": {
      "نام_بخش": {
        "current_score": 0,
        "max_score": 0,
        "percent_of_total": 0,
        "impact_level": "high/medium/low",
        "recommendations": ["پیشنهاد ۱", "پیشنهاد ۲"]
      }
    }
  }
}
"""

    user_prompt = f"""
اطلاعات پروفایل کاربر:
{profile_json}

هدف:
{target_goal or "بر اساس پروفایل تعیین شود"}

فایل راهنمای هدف:
{goal_prompt}

تحلیل کمی فعلی:
{progress_json}

لیست فعالیت‌های مجاز موجود در دیتابیس:
{available_activities_json}

دستور:
بر اساس اطلاعات بالا، نقشه راه را بساز.
تأکید می‌کنم title هر sub_task باید دقیقاً از لیست فعالیت‌های مجاز باشد.

{output_schema}
"""

    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_prompt.strip()},
    ]

    response_text = _call_gpt_api(messages, max_tokens=6000)
    result = _parse_json_response(response_text)

    result["progress"] = progress

    return result


# ═══════════════════════════════════════════════════════════════
# تبدیل خروجی AI به ساختار مورد انتظار roadmap_generate_ai
# ═══════════════════════════════════════════════════════════════

def _normalize_ai_result_to_django_schema(ai_result: dict, profile_data: dict) -> dict:
    """
    تبدیل خروجی generate_roadmap به ساختاری که view فعلی شما انتظار دارد.
    """

    roadmap = ai_result.get("roadmap", {})
    steps = roadmap.get("steps", [])

    first_name = profile_data.get("profile", {}).get("first_name", "")

    normalized = {
        "title": roadmap.get("title") or f"رودمپ پیشرفت حرفه‌ای برای {first_name}",
        "description": roadmap.get("description") or "این رودمپ با استفاده از هوش مصنوعی و بر اساس پروفایل کاربر طراحی شده است.",
        "status": "فعال",
        "stages": [],
        "ai_progress": ai_result.get("progress", {}),
        "quantitative_analysis": ai_result.get("quantitative_analysis", {}),
    }

    valid_activity_titles = set(
        Activity.objects.filter(is_active=True).values_list("title", flat=True)
    )

    for index, step in enumerate(steps, start=1):
        stage_activities = []

        for task in step.get("sub_tasks", []):
            title = task.get("title", "").strip()

            # فقط فعالیت‌هایی ذخیره شوند که واقعاً در دیتابیس هستند
            if title and title in valid_activity_titles:
                stage_activities.append({
                    "title": title,
                    "notes": task.get("notes", "") or step.get("description", ""),
                })

        # اگر مرحله هیچ فعالیت معتبر نداشت، ذخیره نشود
        if not stage_activities:
            continue

        normalized["stages"].append({
            "title": step.get("title") or f"مرحله {index}",
            "description": step.get("description", ""),
            "objectives": step.get("objectives", "") or step.get("description", ""),
            "order": step.get("order") or index,
            "activities": stage_activities,
        })

    return normalized


# ═══════════════════════════════════════════════════════════════
# تابع اصلی مورد استفاده در views.py
# ═══════════════════════════════════════════════════════════════


def generate_ai_roadmap(profile) -> dict:
    """
    تولید رودمپ با AI.
    اگر خطایی رخ دهد یا خروجی معتبر نباشد، Exception بالا می‌رود
    و هیچ roadmap پیش‌فرضی ساخته نمی‌شود.
    """

    profile_data = _collect_profile_data(profile)

    target_goal = (
        profile_data.get("profile", {}).get("goal")
        or profile_data.get("profile", {}).get("specialty")
        or None
    )

    ai_result = generate_roadmap(profile_data=profile_data, target_goal=target_goal)
    normalized = _normalize_ai_result_to_django_schema(ai_result, profile_data)

    if not normalized.get("stages"):

        raise ValueError("خروجی AI معتبر نیست: هیچ مرحله قابل ذخیره‌ای تولید نشد.")

    return normalized



