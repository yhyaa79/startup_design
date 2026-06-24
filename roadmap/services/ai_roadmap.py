# roadmap/services/ai_roadmap.py 
"""
تولید رودمپ حرفه‌ای با AI برای دانشجویان علوم پزشکی ایران.

تغییرات کلیدی نسبت به نسخه قبل:
- prompt سه‌لایه‌ای (system / goal_context / user)
- تحلیل شکاف دقیق‌تر با اولویت‌بندی HIGH/MEDIUM/LOW
- هر مرحله دارای milestone، معیار تکمیل و ریسک‌ها
- هر فعالیت دارای impact_score، difficulty_rating و نشانگر نوع
- نرمالایزر هوشمندتر با fallback چندسطحی
"""

import json
import os
import re
import requests
from datetime import date

from django.conf import settings
from roadmap.models import Activity
from roadmap.services.profile_data import _collect_profile_data


TIMEOUT = 120


# ══════════════════════════════════════════════════════════════════
#  لایه ارتباط با API
# ══════════════════════════════════════════════════════════════════

def _call_gpt_api(messages: list, max_tokens: int = 6000) -> str:
    if not settings.GAPGPT_API_KEY:
        raise ValueError("GAPGPT_API_KEY تنظیم نشده است.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GAPGPT_API_KEY}",
    }
    payload = {
        "model": settings.GAPGPT_MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,  # کمتر از قبل → خروجی منظم‌تر
    }

    try:
        response = requests.post(
            f"{settings.GAPGPT_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.ConnectionError:
        raise ConnectionError("خطا در اتصال به API.")
    except requests.exceptions.Timeout:
        raise TimeoutError("زمان پاسخ API به پایان رسید.")
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else ""
        text = e.response.text if e.response else ""
        raise ValueError(f"خطای HTTP {code}: {text}")
    except (KeyError, IndexError) as e:
        raise ValueError(f"ساختار پاسخ API نامعتبر: {e}")


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    for pattern in [r'```json\s*([\s\S]*?)\s*```', r'```\s*([\s\S]*?)\s*```']:
        m = re.search(pattern, text)
        if m:
            text = m.group(1).strip()
            break
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"خطا در پارس JSON: {e}\n\nمتن:\n{text[:500]}")


# ══════════════════════════════════════════════════════════════════
#  بارگذاری prompt تخصصی هدف
# ══════════════════════════════════════════════════════════════════

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
    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "prompts", filename
    )
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


# ══════════════════════════════════════════════════════════════════
#  تحلیل شکاف پیشرفته
# ══════════════════════════════════════════════════════════════════

def _calculate_gap_analysis(profile_data: dict, goal: str) -> dict:
    """
    تحلیل جامع شکاف بین وضعیت فعلی و هدف.
    خروجی برای AI ارسال می‌شود تا رودمپ را شخصی‌سازی کند.
    """
    profile = profile_data.get("profile", {})
    educations = profile_data.get("educations", [])
    articles = profile_data.get("articles", [])
    presentations = profile_data.get("presentations", [])
    courses = profile_data.get("training_courses", [])
    exec_records = profile_data.get("executive_records", [])

    # —— اطلاعات تحصیلی ——
    current_edu = {}
    for edu in educations:
        if edu.get("degree"):
            current_edu = edu
            break

    degree = current_edu.get("degree", "نامشخص")
    gpa = float(current_edu.get("gpa") or 0)
    current_term = current_edu.get("current_term") or 0
    remaining_terms = current_edu.get("remaining_terms") or 0
    university = current_edu.get("university", "")

    # —— مقالات ——
    isi_articles = [a for a in articles if a.get("index") in
                    ["ISI / Web of Science", "ISI + Scopus", "Scopus", "PubMed"]]
    first_author_articles = [a for a in isi_articles if (a.get("author_rank") or 99) == 1]
    article_journals = [a.get("journal", "") for a in articles if a.get("journal")]

    # —— زبان ——
    english_level = profile.get("english_level", "")
    lang_cert = profile.get("lang_cert", "")
    has_strong_english = english_level in ["B2", "C1", "C2"]
    has_lang_cert = bool(lang_cert and lang_cert.strip())

    # —— مهارت‌ها ——
    software_skills = profile.get("software_skills", "")
    clinical_exp = profile.get("clinical_exp", "")
    writing_skills = profile.get("writing_skills", "")

    # —— سوابق اجرایی ——
    proposal_count = int(profile.get("proposal_count") or 0)

    # —— ساخت گزارش تحلیلی ——
    analysis = {
        "current_status": {
            "degree": degree,
            "university": university,
            "gpa": gpa,
            "current_term": current_term,
            "remaining_terms": remaining_terms,
            "total_articles": len(articles),
            "isi_articles": len(isi_articles),
            "first_author_articles": len(first_author_articles),
            "presentations_count": len(presentations),
            "courses_count": len(courses),
            "exec_records_count": len(exec_records),
            "proposal_count": proposal_count,
            "english_level": english_level,
            "has_lang_cert": has_lang_cert,
            "lang_cert": lang_cert,
            "has_software_skills": bool(software_skills),
            "has_clinical_exp": bool(clinical_exp),
            "has_writing_skills": bool(writing_skills),
            "extracurricular": bool(profile.get("extracurricular")),
        },
        "strengths": [],
        "critical_gaps": [],      # باید حتماً رفع شوند
        "important_gaps": [],     # اثر زیاد دارند
        "optional_gaps": [],      # تکمیلی هستند
        "priority_actions": [],   # ۳ اقدام فوری
        "score": {},
        "goal_specific": {},
    }

    # —— تحلیل بر اساس هدف ——
    if goal == "استعداد درخشان":
        _analyze_estedad(analysis, profile, articles, isi_articles, presentations,
                         proposal_count, degree, gpa)

    elif goal in ["۴۰ امتیازی", "40 امتیازی"]:
        _analyze_40emtiaz(analysis, profile, articles, isi_articles, presentations,
                          proposal_count, gpa, exec_records, courses)

    elif goal in ["هیات علمی", "هیأت علمی"]:
        _analyze_heyat_elmi(analysis, profile, articles, isi_articles, presentations,
                            proposal_count, degree, exec_records, writing_skills)

    elif goal == "ریسرچ پوزیشن / فلوشیپ خارج":
        _analyze_research_position(analysis, profile, articles, presentations,
                                   proposal_count, english_level, has_lang_cert,
                                   exec_records, courses)

    else:
        _analyze_general(analysis, profile, articles, presentations, courses, software_skills)

    return analysis


def _analyze_estedad(analysis, profile, articles, isi_articles, presentations,
                     proposal_count, degree, gpa):
    # حداقل امتیاز بر اساس مقطع
    min_score_map = {
        "کارشناسی": 55, "دکتری عمومی": 95, "کارشناسی ارشد": 95, "دکتری تخصصی": 115
    }
    min_score = min_score_map.get(degree, 95)

    score = 0
    # مقالات
    for a in articles:
        idx = a.get("index", "")
        if idx in ["ISI / Web of Science", "ISI + Scopus"]:
            score += 25 + min(int(float(a.get("impact_factor") or 0)), 25)
        elif idx in ["Scopus", "PubMed", "Medline"]:
            score += 15
        else:
            score += 10
    score = min(score, 50)

    # پایان‌نامه
    if degree == "دکتری تخصصی":
        score += 10

    # ارائه
    pres_score = 0
    for p in presentations:
        pres_score += 3 if p.get("level") == "بین‌المللی" else 1
        if p.get("result") == "برگزیده / جایزه":
            pres_score += 2
    score += min(pres_score, 15)

    # طرح تحقیقاتی
    score += min(proposal_count * 5, 15)

    # فعالیت فوق‌برنامه
    if profile.get("extracurricular"):
        score += 10

    remaining = max(0, min_score - score)
    percent = min(int(score / min_score * 100), 100)

    analysis["score"] = {
        "current": score,
        "minimum_required": min_score,
        "remaining": remaining,
        "percent": percent,
        "degree": degree,
    }

    if score >= min_score:
        analysis["strengths"].append(f"امتیاز کافی برای استعداد درخشان ({score}/{min_score})")
    else:
        analysis["critical_gaps"].append(
            f"کمبود {remaining} امتیاز از {min_score} امتیاز لازم برای {degree}"
        )

    if len(isi_articles) == 0:
        analysis["critical_gaps"].append("هیچ مقاله ISI/Scopus ندارید — حداقل یک مقاله ISI الزامی است")
        analysis["priority_actions"].append("همکاری در پروژه تحقیقاتی برای انتشار مقاله ISI")
    elif len(isi_articles) < 2:
        analysis["important_gaps"].append("داشتن حداقل ۲ مقاله ISI امتیاز قابل توجهی می‌دهد")

    if not presentations:
        analysis["important_gaps"].append("ارائه در کنگره ملی یا بین‌المللی امتیاز می‌دهد")
        analysis["priority_actions"].append("ثبت‌نام و ارائه در یک کنگره علمی")

    if proposal_count == 0:
        analysis["important_gaps"].append("همکاری در طرح تحقیقاتی (مصوب) امتیاز مستقیم دارد")

    if not profile.get("extracurricular"):
        analysis["optional_gaps"].append("عضویت در کمیته تحقیقات دانشجویی یا انجمن علمی")

    analysis["goal_specific"] = {
        "min_score_for_degree": min_score,
        "score_breakdown": {
            "articles": min(sum(25 for a in isi_articles), 50),
            "presentations": min(pres_score, 15),
            "research_projects": min(proposal_count * 5, 15),
        },
        "note": "امتیازات استعداد درخشان طبق آیین‌نامه وزارت بهداشت محاسبه شده"
    }


def _analyze_40emtiaz(analysis, profile, articles, isi_articles, presentations,
                      proposal_count, gpa, exec_records, courses):
    score = 0

    # آموزشی (max 20)
    if gpa >= 18:
        edu_score = 10
    elif gpa >= 17:
        edu_score = 8
    elif gpa >= 16:
        edu_score = 5
    else:
        edu_score = 0
    score += edu_score

    # پژوهشی (max 20)
    article_score = sum(7 if (a.get("author_rank") or 99) == 1 else 4
                        for a in isi_articles)
    article_score = min(article_score, 15)
    pres_score = min(sum(2 if p.get("level") == "بین‌المللی" else 1.5
                         for p in presentations), 5)
    research_score = min(article_score + pres_score + min(proposal_count * 3, 5), 20)
    score += research_score

    # فردی-اجتماعی (max 10)
    social_score = 0
    if profile.get("extracurricular"):
        social_score += 3
    if exec_records:
        social_score += 4
    social_score = min(social_score, 10)
    score += social_score

    remaining = max(0, 40 - score)
    analysis["score"] = {
        "current": score,
        "minimum_required": 40,
        "remaining": remaining,
        "percent": min(int(score / 40 * 100), 100),
        "breakdown": {
            "educational": edu_score,
            "research": research_score,
            "social": social_score,
        }
    }

    if gpa < 16:
        analysis["critical_gaps"].append(f"معدل {gpa} پایین است — تمرکز بر ارتقاء معدل ضروری است")
    elif gpa < 17:
        analysis["important_gaps"].append(f"بالا بردن معدل از {gpa} به بالای ۱۷ اثر زیادی دارد")

    if article_score == 0:
        analysis["critical_gaps"].append("انتشار مقاله معتبر برای بخش پژوهشی الزامی است")
        analysis["priority_actions"].append("شروع همکاری در پروژه پژوهشی برای انتشار مقاله")
    
    if not exec_records:
        analysis["important_gaps"].append("سوابق اجرایی در بخش فردی-اجتماعی ۴ امتیاز می‌دهد")
    
    if remaining > 0:
        analysis["priority_actions"].append(f"برای رسیدن به ۴۰ امتیاز، {remaining} امتیاز دیگر لازم است")

    analysis["goal_specific"] = {
        "max_scores": {"educational": 20, "research": 20, "social": 10},
        "current_scores": {"educational": edu_score, "research": research_score, "social": social_score},
        "note": "امتیازات بر اساس آیین‌نامه ارزیابی ۴۰ امتیازی وزارت بهداشت"
    }


def _analyze_heyat_elmi(analysis, profile, articles, isi_articles, presentations,
                        proposal_count, degree, exec_records, writing_skills):
    has_phd = degree == "دکتری تخصصی"

    if not has_phd:
        analysis["critical_gaps"].append("دکتری تخصصی یا فوق‌تخصص برای هیات علمی الزامی است")
        analysis["priority_actions"].append("برنامه‌ریزی برای ورود به دوره تخصصی/PhD")

    if len(isi_articles) < 3:
        gap = 3 - len(isi_articles)
        analysis["critical_gaps"].append(f"نیاز به {gap} مقاله ISI/Scopus بیشتر (حداقل ۳ مقاله لازم است)")
        analysis["priority_actions"].append("افزایش تعداد مقالات ISI به حداقل ۳ عنوان")
    else:
        analysis["strengths"].append(f"{len(isi_articles)} مقاله ISI/Scopus")

    if proposal_count == 0:
        analysis["critical_gaps"].append("تجربه PI یا Co-I در طرح تحقیقاتی مصوب الزامی است")
    
    if not exec_records:
        analysis["important_gaps"].append("سوابق اجرایی دانشگاهی در ارزیابی هیات علمی مهم است")

    if not writing_skills:
        analysis["important_gaps"].append("تقویت مهارت نگارش علمی (proposal + مقاله)")

    # H-index تقریبی
    h_index = min(len(isi_articles), 3)  # تخمین ساده
    analysis["score"] = {
        "has_phd": has_phd,
        "isi_articles": len(isi_articles),
        "min_isi_required": 3,
        "estimated_h_index": h_index,
        "exec_records": len(exec_records),
        "proposal_count": proposal_count,
    }

    analysis["goal_specific"] = {
        "phd_required": True,
        "min_isi_articles": 3,
        "needs_grant_experience": True,
        "note": "الزامات بر اساس آیین‌نامه استخدام هیات علمی وزارت بهداشت"
    }


def _analyze_research_position(analysis, profile, articles, presentations,
                               proposal_count, english_level, has_lang_cert,
                               exec_records, courses):
    # زبان
    if not english_level or english_level in ["A1", "A2"]:
        analysis["critical_gaps"].append("سطح زبان انگلیسی بسیار پایین است — B2 حداقل مورد نیاز")
        analysis["priority_actions"].append("شروع فوری دوره زبان انگلیسی تخصصی")
    elif english_level == "B1":
        analysis["important_gaps"].append("ارتقاء سطح زبان از B1 به B2/C1 ضروری است")
    else:
        analysis["strengths"].append(f"سطح زبان {english_level} مناسب")

    if not has_lang_cert:
        analysis["important_gaps"].append("مدرک رسمی IELTS یا TOEFL برای اپلای الزامی است")
        analysis["priority_actions"].append("آماده‌سازی و شرکت در آزمون IELTS Academic")

    # مقالات بین‌المللی
    intl_articles = [a for a in articles if a.get("index") in
                     ["ISI / Web of Science", "ISI + Scopus", "Scopus", "PubMed"]]
    if not intl_articles:
        analysis["critical_gaps"].append("نیاز به حداقل یک مقاله در ژورنال بین‌المللی معتبر")
    elif len(intl_articles) < 2:
        analysis["important_gaps"].append("داشتن ۲+ مقاله بین‌المللی پرونده را قوی‌تر می‌کند")
    else:
        analysis["strengths"].append(f"{len(intl_articles)} مقاله بین‌المللی")

    # ارائه بین‌المللی
    intl_pres = [p for p in presentations if p.get("level") == "بین‌المللی"]
    if not intl_pres:
        analysis["important_gaps"].append("ارائه در کنفرانس بین‌المللی برای research position مهم است")
    else:
        analysis["strengths"].append(f"{len(intl_pres)} ارائه بین‌المللی")

    # Research statement / SOP
    analysis["critical_gaps"].append("نیاز به نوشتن Research Statement / SOP حرفه‌ای")
    analysis["priority_actions"].append("تهیه Research Statement و CV انگلیسی")

    if not exec_records and not courses:
        analysis["important_gaps"].append("سوابق تحقیقاتی یا آموزشی مستند")

    analysis["score"] = {
        "english_level": english_level,
        "has_lang_cert": has_lang_cert,
        "intl_articles": len(intl_articles),
        "intl_presentations": len(intl_pres),
        "proposal_count": proposal_count,
    }

    analysis["goal_specific"] = {
        "need_sop": True,
        "need_english_cv": True,
        "target_ielts": "6.5-7.0",
        "recommended_databases": ["PubMed", "Scopus", "ResearchGate"],
        "note": "الزامات بر اساس استانداردهای پوزیشن‌های تحقیقاتی اروپا و آمریکا"
    }


def _analyze_general(analysis, profile, articles, presentations, courses, software_skills):
    score = 0
    if articles:
        score += 25
        analysis["strengths"].append(f"{len(articles)} مقاله")
    else:
        analysis["important_gaps"].append("انتشار مقاله علمی")

    if presentations:
        score += 15
        analysis["strengths"].append(f"{len(presentations)} ارائه علمی")
    else:
        analysis["important_gaps"].append("ارائه در کنگره")

    if courses:
        score += 20
        analysis["strengths"].append(f"{len(courses)} دوره آموزشی")
    else:
        analysis["important_gaps"].append("گذراندن دوره‌های آموزشی کلیدی")

    if software_skills:
        score += 20
        analysis["strengths"].append("مهارت‌های نرم‌افزاری")
    else:
        analysis["important_gaps"].append("یادگیری نرم‌افزارهای پژوهشی مثل SPSS/R/STATA")

    if profile.get("english_level"):
        score += 20
        analysis["strengths"].append("سطح زبان ثبت‌شده")
    else:
        analysis["important_gaps"].append("ثبت و ارتقاء سطح زبان انگلیسی")

    analysis["score"] = {"percent": min(score, 100)}


# ══════════════════════════════════════════════════════════════════
#  لیست فعالیت‌های موجود
# ══════════════════════════════════════════════════════════════════

def _get_available_activities() -> list:
    activities = Activity.objects.filter(is_active=True).order_by("category", "title")
    return [
        {
            "title": a.title,
            "category": a.category,
            "field": a.field,
            "duration_days": a.duration_days,
            "difficulty_level": a.difficulty_level,
            "resume_output": a.resume_output,
            "resume_target": a.resume_target,
            "suitable_goals": a.suitable_goals or [],
            "prerequisites": a.prerequisites or "",
        }
        for a in activities
    ]


# ══════════════════════════════════════════════════════════════════
#  prompt اصلی — سه‌لایه‌ای
# ══════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
تو یک مشاور ارشد حرفه‌ای برای دانشجویان و متخصصان علوم پزشکی ایران هستی.
تخصص تو طراحی نقشه راه (رودمپ) دقیق، قابل اجرا و شخصی‌سازی‌شده برای رسیدن به اهداف آکادمیک است.

══ اصول طراحی رودمپ ══
۱. شخصی‌سازی کامل: رودمپ باید دقیقاً متناسب با وضعیت، هدف و شکاف‌های آن کاربر خاص باشد.
۲. اولویت‌بندی هوشمند: critical_gaps را در مراحل اول قرار بده، optional_gaps را در مراحل آخر.
۳. توالی منطقی: هر مرحله باید زمینه مرحله بعد را فراهم کند.
۴. قابل سنجش بودن: هر مرحله باید معیار مشخصی برای «تکمیل» داشته باشد.
۵. واقع‌بینی: زمان‌بندی باید با بار تحصیلی و وضعیت کاربر سازگار باشد.

══ قوانین خروجی ══
- فقط JSON خالص برگردان، بدون هیچ متن اضافه.
- تمام رشته‌ها باید به فارسی و غیر خالی باشند.
- اعداد باید integer یا float باشند نه string.
""".strip()


def _build_goal_context(goal: str, goal_prompt: str) -> str:
    """context تخصصی هدف را می‌سازد"""
    base = f"هدف کاربر: {goal}\n\n"
    if goal_prompt:
        base += f"راهنمای تخصصی هدف:\n{goal_prompt}\n\n"
    return base


# ── تابع کمکی: برچسب فارسی بازه زمانی ──
_TIMEFRAME_LABELS = {
    'under_3_months': 'کمتر از ۳ ماه',
    '3_to_6_months': '۳ تا ۶ ماه',
    '6_to_12_months': '۶ ماه تا ۱ سال',
    '1_to_2_years': '۱ تا ۲ سال',
    'over_2_years': 'بیشتر از ۲ سال',
}


def _build_user_prompt(
    profile_data: dict,
    gap_analysis: dict,
    available_activities: list,
    target_goal: str,
    goal_prompt: str,
    timeframe: str = '',
    timeframe_days: int = 180,
    user_notes: str = '',
) -> str:
    profile_json = json.dumps(profile_data, ensure_ascii=False, indent=2)
    gap_json = json.dumps(gap_analysis, ensure_ascii=False, indent=2)
    activities_json = json.dumps(available_activities, ensure_ascii=False, indent=2)

    goal_context = _build_goal_context(target_goal or "عمومی", goal_prompt)

    valid_categories = ['پژوهشی', 'بالینی', 'آموزشی', 'نرم‌افزاری', 'زبان', 'شبکه‌سازی', 'توسعه‌شخصی', 'سایر']
    valid_fields = ['پزشکی', 'دندان‌پزشکی', 'داروسازی', 'پرستاری', 'فیزیوتراپی', 'سایر', 'عمومی']
    valid_difficulties = ['آسان', 'متوسط', 'سخت']
    valid_resume_targets = ['article', 'presentation', 'training_course', 'executive_record', 'skill']
    valid_priorities = ['critical', 'high', 'medium', 'low']
    valid_phase_types = ['foundation', 'development', 'advancement', 'excellence']

    # ── بخش زمان‌بندی برای inject در پرامپت ──
    timeframe_label = _TIMEFRAME_LABELS.get(timeframe, '')
    timeframe_section = f"""
═══ محدودیت زمانی کاربر ═══
بازه زمانی انتخابی: {timeframe_label or 'مشخص نشده'}
حداکثر روزهای در دسترس: {timeframe_days} روز
قانون اجباری: جمع duration_days تمام فعالیت‌های همه مراحل باید حداکثر {timeframe_days} روز باشد.
فعالیت‌ها را طوری انتخاب و اولویت‌بندی کن که در این بازه زمانی واقعاً قابل انجام باشند.
""".strip()

    notes_section = ""
    if user_notes:
        notes_section = f"""
═══ نکات شخصی کاربر ═══
{user_notes}
این نکات را در طراحی رودمپ مدنظر قرار بده.
""".strip()

    profile_schema = """
═══ ساختار مدل‌های پروفایل (برای profile_template فعالیت‌های جدید) ═══
training_courses → {title, category(پژوهشی|بالینی|آموزشی|نرم‌افزاری|زبان|سایر), status("تکمیل‌شده"), organizer("Roadmap"), date("{today}"), certificate(دارد|ندارد), skills_gained}
presentations    → {title, event, level(بین‌المللی|ملی|قطبی|دانشگاهی), result(برگزیده / جایزه|ارائه عادی)}
articles         → {title, journal, year(عدد مثل 1403), author_rank(عدد), index(ISI / Web of Science|Scopus|PubMed|ISI + Scopus|سایر)}
executive_records→ {title, start_date("{today}"), end_date("")}
نکته: "{today}" را دقیقاً همین‌طور بنویس — runtime جایگزین می‌کند.
resume_target = "skill" → profile_template باید null باشد.
""".strip()

    output_schema = f"""
═══ ساختار JSON خروجی — EXACT FORMAT ═══
{{
  "title": "عنوان رودمپ — باید هدف و تخصص را نشان دهد",
  "description": "خلاصه تحلیلی ۴-۵ جمله‌ای از وضعیت کاربر و مسیر طراحی‌شده",
  "goal": "{target_goal or 'هدف نهایی'}",
  "stages": [
    {{
      "order": 1,
      "title": "عنوان گویا — مثال: پایه‌ریزی مهارت پژوهش",
      "description": "چرا این مرحله اول است و چه چیزی می‌سازد — ۲-۳ جمله",
      "objectives": "چه چیزی باید در پایان این مرحله حاصل شده باشد — دقیق و قابل سنجش",
      "phase_type": "یکی از: {valid_phase_types}",
      "priority": "یکی از: {valid_priorities}",
      "milestone": "معیار تکمیل مرحله — مثال: یک مقاله ارسال‌شده به ژورنال",
      "success_criteria": ["معیار ۱ قابل سنجش", "معیار ۲ قابل سنجش"],
      "risks": ["ریسک احتمالی ۱", "ریسک ۲"],
      "activities": [
        {{
          "is_new": false,
          "title": "عنوان دقیقاً مطابق existing_activities",
          "notes": "چرا این فعالیت در این مرحله؟ چه تأثیری دارد؟",
          "impact_score": 9,
          "priority_in_stage": "critical"
        }}
      ],
      "recommended_resources": []
    }}
  ]
}}
""".strip()

    return f"""
{goal_context}

{timeframe_section}

{notes_section}

═══ پروفایل کاربر ═══
{profile_json}

═══ تحلیل شکاف وضعیت فعلی ═══
{gap_json}

═══ فعالیت‌های موجود در سیستم ═══
{activities_json}

{profile_schema}

═══ دستورالعمل طراحی ═══
۱. از gap_analysis.critical_gaps شروع کن — اینها باید در مراحل اول رفع شوند.
۲. از gap_analysis.strengths استفاده کن — روی آن‌ها بنا کن نه از صفر.
۳. از existing_activities استفاده کن (is_new:false) وقتی با هدف و مرحله تطابق دارد.
۴. فعالیت جدید (is_new:true) فقط وقتی existing_activities کافی نیست.
۵. تعداد مراحل: ۴ تا ۸. هر مرحله: ۲ تا ۵ فعالیت.
۶. impact_score: 1-10 بر اساس تأثیر واقعی روی رسیدن به هدف.
۷. milestone باید یک خروجی ملموس و قابل اثبات باشد.
۸. جمع duration_days فعالیت‌ها نباید از {timeframe_days} روز تجاوز کند — این قانون اجباری است.

{output_schema}
""".strip()



# ══════════════════════════════════════════════════════════════════
#  تولید رودمپ با AI
# ══════════════════════════════════════════════════════════════════

def generate_roadmap_v2(
    profile_data: dict,
    target_goal: str = None,
    timeframe: str = '',
    timeframe_days: int = 180,
    user_notes: str = '',
) -> dict:

    goal = target_goal or profile_data.get("profile", {}).get("goal", "")
    goal_prompt = _load_goal_prompt(goal)
    gap_analysis = _calculate_gap_analysis(profile_data, goal)
    available_activities = _get_available_activities()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": _build_user_prompt(
                profile_data,
                gap_analysis,
                available_activities,
                goal,
                goal_prompt,
                timeframe=timeframe,
                timeframe_days=timeframe_days,
                user_notes=user_notes,
            ),
        },
    ]

    response_text = _call_gpt_api(messages, max_tokens=7000)
    result = _parse_json_response(response_text)
    result["gap_analysis"] = gap_analysis
    return result


# ══════════════════════════════════════════════════════════════════
#  پیدا کردن یا ساختن Activity در دیتابیس
# ══════════════════════════════════════════════════════════════════

VALID_CATEGORIES = {'پژوهشی', 'بالینی', 'آموزشی', 'نرم‌افزاری', 'زبان', 'شبکه‌سازی', 'توسعه‌شخصی', 'سایر'}
VALID_FIELDS = {'پزشکی', 'دندان‌پزشکی', 'داروسازی', 'پرستاری', 'فیزیوتراپی', 'سایر', 'عمومی'}
VALID_DIFFICULTIES = {'آسان', 'متوسط', 'سخت'}
VALID_RESUME_TARGETS = {'article', 'presentation', 'training_course', 'executive_record', 'skill'}


def _get_or_create_activity(task: dict) -> Activity | None:
    title = (task.get("title") or "").strip()
    if not title:
        return None

    is_new = task.get("is_new", False)

    if not is_new:
        # ۱. تطابق دقیق
        activity = Activity.objects.filter(title=title, is_active=True).first()
        if activity:
            return activity
        # ۲. تطابق تقریبی (۲۵ کاراکتر اول)
        activity = Activity.objects.filter(
            title__icontains=title[:25], is_active=True
        ).first()
        return activity

    activity_data = task.get("activity_data") or {}
    if not activity_data:
        # اگر is_new=true ولی activity_data نداشت، یک بار existing را جستجو کن
        return Activity.objects.filter(
            title__icontains=title[:20], is_active=True
        ).first()

    def _clean(value, valid_set, default):
        return value if value in valid_set else default

    category = _clean(activity_data.get("category", ""), VALID_CATEGORIES, "سایر")
    field = _clean(activity_data.get("field", ""), VALID_FIELDS, "عمومی")
    difficulty = _clean(activity_data.get("difficulty_level", ""), VALID_DIFFICULTIES, "متوسط")
    resume_target = _clean(activity_data.get("resume_target", ""), VALID_RESUME_TARGETS, "skill")

    try:
        duration_days = max(1, min(int(activity_data.get("duration_days", 30)), 365))
    except (TypeError, ValueError):
        duration_days = 30

    profile_template = activity_data.get("profile_template")
    if resume_target == "skill":
        profile_template = None

    activity, _ = Activity.objects.update_or_create(
        title=title,
        defaults={
            "description": (activity_data.get("description") or f"فعالیت {title}")[:500],
            "category": category,
            "field": field,
            "duration_days": duration_days,
            "difficulty_level": difficulty,
            "resume_output": activity_data.get("resume_output") or title,
            "prerequisites": activity_data.get("prerequisites") or "",
            "resources": activity_data.get("resources") or "",
            "resume_target": resume_target,
            "profile_template": profile_template,
            "suitable_goals": [],
            "is_active": True,
        },
    )
    return activity


# ══════════════════════════════════════════════════════════════════
#  نرمالایز کردن خروجی AI به ساختار Django
# ══════════════════════════════════════════════════════════════════

def _normalize_to_django_schema(ai_result: dict, profile_data: dict) -> dict:
    """
    تبدیل خروجی AI به ساختار مورد انتظار view.
    فعالیت‌های جدید در دیتابیس ذخیره می‌شوند.
    """
    first_name = profile_data.get("profile", {}).get("first_name", "")

    normalized = {
        "title": ai_result.get("title") or f"رودمپ حرفه‌ای {first_name}",
        "description": ai_result.get("description") or "رودمپ شخصی‌سازی‌شده با هوش مصنوعی",
        "status": "فعال",
        "stages": [],
        "gap_analysis": ai_result.get("gap_analysis", {}),
        "summary": ai_result.get("summary", {}),
    }

    for index, stage_data in enumerate(ai_result.get("stages", []), start=1):
        stage_activities = []

        for task in stage_data.get("activities", []):
            activity = _get_or_create_activity(task)
            if not activity:
                continue

            stage_activities.append({
                "title": activity.title,
                "notes": task.get("notes") or stage_data.get("description", ""),
                "impact_score": task.get("impact_score", 5),
                "priority_in_stage": task.get("priority_in_stage", "medium"),
            })

        if not stage_activities:
            continue

        normalized["stages"].append({
            "title": stage_data.get("title") or f"مرحله {index}",
            "description": stage_data.get("description") or "",
            "objectives": stage_data.get("objectives") or stage_data.get("description") or "",
            "order": stage_data.get("order") or index,
            "phase_type": stage_data.get("phase_type") or "development",
            "priority": stage_data.get("priority") or "medium",
            "milestone": stage_data.get("milestone") or "",
            "success_criteria": stage_data.get("success_criteria") or [],
            "risks": stage_data.get("risks") or [],
            "activities": stage_activities,
            "recommended_resources": stage_data.get("recommended_resources") or [],
        })

    return normalized


# ══════════════════════════════════════════════════════════════════
#  entry point اصلی — جایگزین generate_ai_roadmap
# ══════════════════════════════════════════════════════════════════

def generate_ai_roadmap(
    profile,
    target_goal: str = None,
    timeframe: str = '',
    timeframe_days: int = 180,
    user_notes: str = '',
) -> dict:
    """
    entry point اصلی برای view.
    """
    profile_data = _collect_profile_data(profile)

    goal = target_goal or (
        profile_data.get("profile", {}).get("goal")
        or profile_data.get("profile", {}).get("specialty")
        or None
    )

    ai_result = generate_roadmap_v2(
        profile_data=profile_data,
        target_goal=goal,
        timeframe=timeframe,
        timeframe_days=timeframe_days,
        user_notes=user_notes,
    )
    normalized = _normalize_to_django_schema(ai_result, profile_data)

    if not normalized.get("stages"):
        raise ValueError("خروجی AI معتبر نیست: هیچ مرحله قابل ذخیره‌ای تولید نشد.")

    return normalized
