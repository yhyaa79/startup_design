# roadmap/services/ai_roadmap.py

import json
import os
import re
import requests

from django.conf import settings
from roadmap.models import Activity
from roadmap.services.profile_data import _collect_profile_data


TIMEOUT = 120


def _call_gpt_api(messages: list, max_tokens: int = 4000) -> str:
    if not settings.GAPGPT_API_KEY:
        raise ValueError(
            "API Key تنظیم نشده است. "
            "لطفاً GAPGPT_API_KEY را در settings یا env تنظیم کنید."
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GAPGPT_API_KEY}",
    }

    payload = {
        "model": settings.GAPGPT_MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.25,
    }

    try:
        response = requests.post(
            f"{settings.GAPGPT_API_BASE}/chat/completions",
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
    text = response_text.strip()

    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        text = json_match.group(1)

    code_match = re.search(r'```\s*([\s\S]*?)\s*```', text)
    if code_match:
        text = code_match.group(1)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"خطا در پارس JSON: {str(e)}\n\nمتن دریافتی:\n{text}")


def _load_goal_prompt(goal: str) -> str:
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


def _calculate_progress(profile_data: dict, goal: str) -> dict:
    """
    محاسبه درصد پیشرفت کاربر بر اساس اطلاعات پروفایل و هدف.
    (بدون تغییر نسبت به نسخه قبلی)
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
            "score": article_score, "max_possible": 50,
            "impact_percent": min(int((article_score / 50) * 100), 100),
            "description": "مقالات ISI/Scopus بیشترین اثر را دارند.",
        }

        if current_degree == "دکتری تخصصی":
            score += 10
            score_details["پایان‌نامه"] = 10
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
            "score": presentation_score, "max_possible": 15,
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
            score += 10
            score_details["کمیته تحقیقات"] = 10
            progress["completed_items"].append("فعالیت در کمیته یا انجمن علمی")

        progress["overall_percent"] = min(int((score / min_score) * 100), 100)
        progress["score_breakdown"] = score_details
        progress["score_breakdown"].update({
            "total_score": score, "min_score": min_score,
            "degree": current_degree, "stage": current_stage,
            "remaining_to_goal": max(0, min_score - score),
        })

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
                article_score += 7 if author_rank == 1 else 4
                progress["completed_items"].append(f"مقاله معتبر: {article.get('title', '')[:40]}")
            else:
                article_score += 2
                progress["completed_items"].append(f"مقاله: {article.get('title', '')[:40]}")

        article_score = min(article_score, 15)

        pres_score = 0
        for pres in presentations:
            pres_score += 2 if pres.get("level") == "بین‌المللی" else 1.5
            progress["completed_items"].append(f"ارائه علمی: {pres.get('title', '')[:40]}")
        pres_score = min(pres_score, 5)

        proposal_count = profile.get("proposal_count") or 0
        proposal_score = min(proposal_count * 3, 5)
        research_score = min(article_score + pres_score + proposal_score, 20)
        score += research_score

        score_details.update({
            "مقالات": article_score, "ارائه‌ها": pres_score,
            "طرح‌ها": proposal_score, "پژوهشی": research_score,
        })

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
        progress["score_breakdown"].update({
            "total_score": score, "min_score": min_score,
            "remaining": max(0, min_score - score),
        })
        progress["impact_analysis"] = {
            "آموزشی": {"score": edu_score, "max_possible": 20,
                       "impact_percent": min(int((edu_score / 20) * 100), 100),
                       "description": "معدل و فعالیت‌های آموزشی اثر مهمی دارند."},
            "پژوهشی": {"score": research_score, "max_possible": 20,
                       "impact_percent": min(int((research_score / 20) * 100), 100),
                       "description": "مقاله، طرح تحقیقاتی و ارائه علمی بیشترین اثر را دارند."},
            "فردی-اجتماعی-فرهنگی": {"score": social_score, "max_possible": 10,
                                     "impact_percent": min(int((social_score / 10) * 100), 100),
                                     "description": "فعالیت‌های اجتماعی و داوطلبانه امتیاز تکمیلی ایجاد می‌کنند."},
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

        isi_articles = [a for a in articles if a.get("index") in ["ISI / Web of Science", "Scopus", "ISI + Scopus"]]
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


def _get_available_activities_for_prompt() -> list:
    """
    لیست فعالیت‌های فعال موجود در دیتابیس برای ارائه به AI به عنوان نمونه.
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


def generate_roadmap(profile_data: dict, target_goal: str = None) -> dict:
    """
    تولید نقشه راه شخصی‌سازی‌شده با AI.
    AI می‌تواند از فعالیت‌های موجود استفاده کند یا فعالیت‌های جدید بسازد.
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

    category_choices = ['پژوهشی', 'بالینی', 'آموزشی', 'نرم‌افزاری', 'زبان', 'شبکه‌سازی', 'توسعه‌شخصی', 'سایر']
    field_choices = ['پزشکی', 'دندان‌پزشکی', 'داروسازی', 'پرستاری', 'فیزیوتراپی', 'سایر', 'عمومی']
    difficulty_choices = ['آسان', 'متوسط', 'سخت']
    resume_target_choices = ['article', 'presentation', 'training_course', 'executive_record', 'skill']

    # ─── اطلاعات ساختار پروفایل برای راهنمایی AI ───
    profile_schema_hint = """
ساختار مدل‌های پروفایل که هنگام تکمیل فعالیت در دیتابیس ذخیره می‌شوند:

training_courses: {title, category(پژوهشی|بالینی|آموزشی|نرم‌افزاری|زبان|سایر), status(تکمیل‌شده), organizer, date("{today}"), certificate(دارد|ندارد), skills_gained}
presentations:    {title, event, level(بین‌المللی|ملی|قطبی|دانشگاهی), result(برگزیده / جایزه|ارائه عادی)}
articles:         {title, journal, year(عدد جلالی مثل 1403), author_rank(عدد), index(ISI / Web of Science|Scopus|PubMed|ISI + Scopus|سایر)}
executive_records:{title, start_date("{today}"), end_date("")}
""".strip()

    system_prompt = f"""
تو یک مشاور حرفه‌ای ارشد برای دانشجویان و متخصصان علوم پزشکی ایران هستی.
هدف تو ساختن یک نقشه راه دقیق، شخصی و قابل اجرا برای رسیدن کاربر به هدف حرفه‌ای‌اش است.

═══ قوانین خروجی ═══
1. فقط JSON خالص برگردان. هیچ توضیح، مقدمه یا متنی خارج از JSON ننویس.
2. تمام مقادیر رشته‌ای باید غیر خالی باشند مگر آنکه در schema مشخص شده باشد.

═══ قوانین طراحی نقشه راه ═══
3. نقشه راه باید کاملاً بر اساس وضعیت فعلی کاربر طراحی شود:
   - نقاط قوت موجود را شناسایی و بر آن‌ها بنا کن.
   - شکاف‌های حیاتی (missing_items) را در اولویت قرار بده.
   - مراحل را از آسان به سخت و از پایه به تخصصی مرتب کن.
4. هر مرحله باید یک هدف مشخص و قابل سنجش داشته باشد.
5. تعداد مراحل: بین ۴ تا ۸ مرحله.
6. تعداد فعالیت هر مرحله: بین ۲ تا ۵ فعالیت.

═══ قوانین انتخاب فعالیت ═══
7. ابتدا از existing_activities فعالیت‌هایی انتخاب کن که:
   - suitable_goals آن‌ها شامل هدف کاربر می‌شود، یا suitable_goals خالی است.
   - با وضعیت فعلی کاربر و مرحله جاری تناسب دارد.
   → این فعالیت‌ها را با is_new: false برگردان.
8. اگر فعالیت مناسبی در existing_activities نبود یا نیاز به فعالیت تخصصی‌تر داشتی:
   → فعالیت جدید با is_new: true و تمام فیلدهای activity_data بساز.
9. ترکیب هوشمندانه‌ای از هر دو نوع داشته باش.

═══ قوانین profile_template برای فعالیت‌های جدید ═══
{profile_schema_hint}

مقدار date در training_courses و start_date در executive_records باید دقیقاً "{{"{{today}}"}}": باشد (رشته literal، بدون تغییر).
resume_target = "skill" → profile_template باید null باشد.
""".strip()

    output_schema = f"""
═══ ساختار JSON خروجی ═══
{{
  "roadmap": {{
    "title": "عنوان نقشه راه متناسب با هدف و تخصص کاربر",
    "description": "خلاصه‌ای از وضعیت فعلی کاربر و مسیر پیش رو (۲-۳ جمله)",
    "goal": "هدف نهایی",
    "steps": [
      {{
        "order": 1,
        "title": "عنوان مرحله - باید گویا و انگیزه‌بخش باشد",
        "description": "توضیح اینکه این مرحله چه چیزی را می‌سازد و چرا مهم است",
        "objectives": "اهداف مشخص و قابل سنجش این مرحله",
        "priority": "critical",
        "estimated_duration": "مثال: ۶ هفته",
        "status": "available",
        "impact_score": 9,
        "sub_tasks": [
          {{
            "is_new": false,
            "title": "عنوان دقیقاً مطابق existing_activities",
            "notes": "چرا این فعالیت در این مرحله ضروری است"
          }},
          {{
            "is_new": true,
            "title": "عنوان توصیفی و منحصر به فرد برای فعالیت جدید",
            "notes": "چرا این فعالیت در این مرحله ضروری است",
            "activity_data": {{
              "description": "توضیح کامل فعالیت و نحوه انجام آن",
              "category": "یکی از: {category_choices}",
              "field": "یکی از: {field_choices}",
              "duration_days": 30,
              "difficulty_level": "یکی از: {difficulty_choices}",
              "resume_output": "چه چیزی در رزومه اضافه می‌شود",
              "prerequisites": "پیش‌نیازهای لازم یا خالی",
              "resources": "منابع، سایت‌ها یا کتاب‌های پیشنهادی",
              "resume_target": "یکی از: {resume_target_choices}",
              "profile_template": {{
                "model": "training_courses",
                "data": {{
                  "title": "عنوان برای ذخیره در پروفایل",
                  "category": "پژوهشی",
                  "status": "تکمیل‌شده",
                  "organizer": "Roadmap",
                  "date": "{{today}}",
                  "certificate": "دارد",
                  "skills_gained": "مهارت‌های کسب‌شده"
                }}
              }}
            }}
          }}
        ],
        "resources": [
          {{
            "title": "عنوان منبع",
            "resource_type": "کتاب/دوره/مقاله/وب‌سایت",
            "url": "",
            "description": "چرا این منبع مفید است"
          }}
        ]
      }}
    ]
  }},
  "quantitative_analysis": {{
    "overall_percent": 0,
    "total_score": 0,
    "min_score": 0,
    "remaining_score": 0,
    "sections": {{
      "نام_بخش": {{
        "current_score": 0,
        "max_score": 0,
        "percent_of_total": 0,
        "impact_level": "high/medium/low",
        "recommendations": ["اقدام اول", "اقدام دوم"]
      }}
    }}
  }}
}}
""".strip()

    user_prompt = f"""
═══ پروفایل کاربر ═══
{profile_json}

═══ هدف نهایی ═══
{target_goal or "بر اساس فیلد goal در پروفایل تعیین شود"}

═══ راهنمای تخصصی هدف ═══
{goal_prompt if goal_prompt else "راهنمای خاصی موجود نیست - از اطلاعات پروفایل استفاده کن"}

═══ تحلیل کمی وضعیت فعلی ═══
{progress_json}

═══ فعالیت‌های موجود در دیتابیس (existing_activities) ═══
{available_activities_json}

═══ دستور ═══
با توجه به تمام اطلاعات بالا:

۱. وضعیت فعلی کاربر را ارزیابی کن (completed_items چیست، missing_items چیست).
۲. یک نقشه راه مرحله‌به‌مرحله طراحی کن که شکاف‌های موجود را پر کند.
۳. برای هر مرحله، فعالیت‌هایی انتخاب یا بساز که بیشترین تأثیر را بر رسیدن به هدف دارند.
۴. مطمئن شو profile_template هر فعالیت جدید با ساختار صحیح مدل متناظر تطبیق دارد.

{output_schema}
""".strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response_text = _call_gpt_api(messages, max_tokens=6000)
    result = _parse_json_response(response_text)
    result["progress"] = progress

    return result


def _get_or_create_activity(task: dict) -> Activity | None:
    title = task.get("title", "").strip()
    if not title:
        return None

    is_new = task.get("is_new", False)

    if not is_new:
        activity = Activity.objects.filter(title=title, is_active=True).first()
        if activity:
            return activity
        activity = Activity.objects.filter(title__icontains=title[:20], is_active=True).first()
        return activity

    activity_data = task.get("activity_data", {})
    if not activity_data:
        return None

    valid_categories = ['پژوهشی', 'بالینی', 'آموزشی', 'نرم‌افزاری', 'زبان', 'شبکه‌سازی', 'توسعه‌شخصی', 'سایر']
    valid_fields = ['پزشکی', 'دندان‌پزشکی', 'داروسازی', 'پرستاری', 'فیزیوتراپی', 'سایر', 'عمومی']
    valid_difficulties = ['آسان', 'متوسط', 'سخت']
    valid_resume_targets = ['article', 'presentation', 'training_course', 'executive_record', 'skill']

    category = activity_data.get("category", "سایر")
    if category not in valid_categories:
        category = "سایر"

    field = activity_data.get("field", "عمومی")
    if field not in valid_fields:
        field = "عمومی"

    difficulty = activity_data.get("difficulty_level", "متوسط")
    if difficulty not in valid_difficulties:
        difficulty = "متوسط"

    resume_target = activity_data.get("resume_target", "skill")
    if resume_target not in valid_resume_targets:
        resume_target = "skill"

    duration_days = activity_data.get("duration_days", 30)
    try:
        duration_days = max(1, min(int(duration_days), 365))
    except (TypeError, ValueError):
        duration_days = 30

    profile_template = activity_data.get("profile_template")
    if resume_target == "skill":
        profile_template = None

    # ← مهم: مطمئن شو {today} به صورت literal در JSON ذخیره می‌شه
    # profile_activity_sync.py موقع اجرا آن را جایگزین می‌کند
    # پس نباید اینجا جایگزین کنیم

    activity, _ = Activity.objects.update_or_create(
        title=title,
        defaults={
            "description": (activity_data.get("description", "") or f"فعالیت {title}")[:500],
            "category": category,
            "field": field,
            "duration_days": duration_days,
            "difficulty_level": difficulty,
            "resume_output": activity_data.get("resume_output", title),
            "prerequisites": activity_data.get("prerequisites", ""),
            "resources": activity_data.get("resources", ""),
            "resume_target": resume_target,
            "profile_template": profile_template,
            "suitable_goals": [],  # فعالیت‌های AI-generated بدون suitable_goals ذخیره می‌شن
            "is_active": True,
        }
    )

    return activity


def _normalize_ai_result_to_django_schema(ai_result: dict, profile_data: dict) -> dict:
    """
    تبدیل خروجی generate_roadmap به ساختاری که view انتظار دارد.
    فعالیت‌های جدید AI در دیتابیس ذخیره می‌شوند.
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

    for index, step in enumerate(steps, start=1):
        stage_activities = []

        for task in step.get("sub_tasks", []):
            # پیدا کردن یا ساختن فعالیت
            activity = _get_or_create_activity(task)

            if activity:
                stage_activities.append({
                    "title": activity.title,
                    "notes": task.get("notes", "") or step.get("description", ""),
                })

        # اگر مرحله هیچ فعالیتی نداشت، ذخیره نشود
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


def generate_ai_roadmap(profile) -> dict:
    """
    تولید رودمپ با AI.
    فعالیت‌های جدید AI به صورت خودکار در دیتابیس ذخیره می‌شوند.
    اگر خطایی رخ دهد یا خروجی معتبر نباشد، Exception بالا می‌رود.
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