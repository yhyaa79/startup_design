# roadmap/ai_roadmap.py 

import json
import re
import requests
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# تنظیمات API - GapGPT
# ═══════════════════════════════════════════════════════════════

GAPGPT_API_URL = settings.GAPGPT_API_BASE
GAPGPT_API_KEY = settings.GAPGPT_API_KEY

TIMEOUT = 120  # ثانیه
# نگاشت کلید هدف (مطابق GOAL_CHOICES مدل Roadmap) به برچسب فارسی جهت استفاده در پرامپت
GOAL_LABELS = {
    "estedad_darakhshan": "استعداد درخشان",
    "40_emtiaz": "۴۰ امتیازی",
    "heyat_elmi": "هیات علمی",
    "research_position": "ریسرچ پوزیشن / فلوشیپ خارج",
    "general": "بهبود عمومی",
}

if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


# ═══════════════════════════════════════════════════════════════
# تابع کمکی برای ارتباط با API
# ═══════════════════════════════════════════════════════════════
'''
def _call_gpt_api(messages: list, max_tokens: int = 4000) -> str:
    """
    نسخه تست - بدون فراخوانی واقعی API
    """
    sample_response = {
        "title": "نقشه راه استعداد درخشان - قلب و عروق",
        "description": "نقشه راه شخصی‌سازی‌شده برای کسب امتیاز استعداد درخشان",
        "stages": [
            {
                "order": 1,
                "title": "تقویت پایه پژوهشی",
                "description": "ایجاد زیرساخت لازم برای فعالیت‌های پژوهشی آینده",
                "objectives": "یادگیری روش‌شناسی تحقیق و آمار پیشرفته",
                "phase_type": "foundation",
                "priority": "high",
                "duration_days": 60,
                "milestone": "تسلط بر روش تحقیق پایه",
                "success_criteria": ["گذراندن دوره متدولوژی", "آشنایی با نرم‌افزار آماری"],
                "risks": ["کمبود زمان به دلیل کارآموزی"],
                "recommended_resources": ["دوره روش تحقیق دانشگاه", "کتاب Epidemiology Basics"],
                "activities": [
                    {
                        "title": "دوره متدولوژی تحقیق",
                        "description": "گذراندن دوره آنلاین روش تحقیق بالینی",
                        "category": "course",
                        "duration_days": 30,
                        "impact_score": 6,
                        "difficulty_rating": "medium",
                        "resume_output": "گواهی دوره متدولوژی تحقیق بالینی"
                    },
                    {
                        "title": "یادگیری SPSS پیشرفته",
                        "description": "تسلط بر تحلیل‌های آماری پیشرفته",
                        "category": "course",
                        "duration_days": 30,
                        "impact_score": 5,
                        "difficulty_rating": "medium",
                        "resume_output": "مهارت تحلیل آماری پیشرفته"
                    }
                ]
            },
            {
                "order": 2,
                "title": "تولید و انتشار مقاله",
                "description": "نگارش و ارسال مقاله به ژورنال‌های معتبر",
                "objectives": "انتشار حداقل یک مقاله ISI/Scopus",
                "phase_type": "development",
                "priority": "high",
                "duration_days": 90,
                "milestone": "ارسال مقاله به ژورنال",
                "success_criteria": ["نگارش مقاله کامل", "ارسال به ژورنال معتبر"],
                "risks": ["ریجکت شدن مقاله", "طولانی شدن فرآیند داوری"],
                "recommended_resources": ["راهنمای نگارش مقاله ISI", "مشاوره با استاد راهنما"],
                "activities": [
                    {
                        "title": "جمع‌آوری داده‌های پژوهشی",
                        "description": "جمع‌آوری و تحلیل داده‌های بیماران نارسایی قلبی",
                        "category": "research",
                        "duration_days": 45,
                        "impact_score": 8,
                        "difficulty_rating": "hard",
                        "resume_output": "پروژه پژوهشی نارسایی قلبی"
                    },
                    {
                        "title": "نگارش و ارسال مقاله",
                        "description": "نگارش مقاله بر اساس یافته‌ها و ارسال به ژورنال Scopus",
                        "category": "research",
                        "duration_days": 45,
                        "impact_score": 9,
                        "difficulty_rating": "hard",
                        "resume_output": "مقاله در حال داوری در ژورنال Scopus"
                    }
                ]
            }
        ],
        "quantitative_analysis": {
            "overall_percent": 45,
            "total_score": 45,
            "min_score": 95,
            "remaining_score": 50,
            "sections": {
                "مقالات": {
                    "current_score": 15,
                    "max_score": 50,
                    "percent_of_total": 30,
                    "impact_level": "high",
                    "recommendations": ["انتشار مقاله ISI با امپکت بالاتر"]
                },
                "ارائه‌ها": {
                    "current_score": 5,
                    "max_score": 15,
                    "percent_of_total": 33,
                    "impact_level": "medium",
                    "recommendations": ["شرکت در کنگره‌های بین‌المللی بیشتر"]
                }
            }
        }
    }

    logger.info("پاسخ تستی (mock) برگردانده شد.")
    return json.dumps(sample_response, ensure_ascii=False)

'''



def _call_gpt_api(messages: list, max_tokens: int = 4000) -> str:
    """
    فراخوانی واقعی API با تضمین خروجی JSON معتبر

    gpt-4o-mini
    gemini-2.5-flash-lite
    gpt-4.1-mini
    gpt-4.1
    """
    headers = {
        "Authorization": f"Bearer {GAPGPT_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gemini-2.5-flash-lite",
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


# ═══════════════════════════════════════════════════════════════
# تابع اصلی: تولید نقشه راه
# ═══════════════════════════════════════════════════════════════

def _load_goal_prompt(goal: str) -> str:
    """
    بارگذاری فایل placeholder مربوط به هدف کاربر.
    
    Args:
        goal: هدف کاربر (استعداد درخشان، ۴۰ امتیازی، هیات علمی، ریسرچ پوزیشن / فلوشیپ خارج)
    
    Returns:
        محتوای فایل placeholder یا رشته خالی در صورت عدم وجود
    """
    import os
    
    goal_map = {
        "استعداد درخشان": "estedad_darakhshan.md",
        "۴۰ امتیازی": "40_emtiaz.md",
        "هیات علمی": "heyat_elmi.md",
        "ریسرچ پوزیشن / فلوشیپ خارج": "research_position.md",
    }
    
    filename = goal_map.get(goal)
    if not filename:
        return ""
    
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "roadmap", "prompts", filename)
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _calculate_progress(profile_data: dict, goal: str) -> dict:
    """
    محاسبه درصد پیشرفت کاربر بر اساس رزومه و هدف.
    goal باید یکی از کلیدهای GOAL_CHOICES مدل Roadmap باشد
    (estedad_darakhshan, 40_emtiaz, heyat_elmi, research_position, general)
    """
    progress = {
        "overall_percent": 0,
        "completed_items": [],
        "missing_items": [],
        "score_breakdown": {},
        "impact_analysis": {}
    }

    profile = profile_data.get("profile", {})
    educations = profile_data.get("educations", [])
    articles = profile_data.get("articles", [])
    presentations = profile_data.get("presentations", [])
    courses = profile_data.get("training_courses", [])

    if goal == "estedad_darakhshan":
        # محاسبه امتیاز بر اساس دستورالعمل استعداد درخشان
        score = 0
        score_details = {}

        current_degree = ""
        current_stage = ""
        for edu in educations:
            degree = edu.get("degree", "")
            stage = edu.get("stage", "")
            if degree:
                current_degree = degree
            if stage:
                current_stage = stage

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
            impact_factor = article.get("impact_factor", 0)

            if index in ["ISI / Web of Science", "ISI + Scopus"]:
                base_score = 25
                if impact_factor and impact_factor > 3:
                    base_score += min(int(impact_factor), 25)
                article_score += base_score
                progress["completed_items"].append(f"مقاله ISI: {article.get('title', '')[:50]}...")
            elif index in ["Scopus", "PubMed", "Medline"]:
                article_score += 15
                progress["completed_items"].append(f"مقاله Scopus/PubMed: {article.get('title', '')[:50]}...")
            else:
                article_score += 10
                progress["completed_items"].append(f"مقاله: {article.get('title', '')[:50]}...")

        article_score = min(article_score, 50)
        score += article_score
        score_details["مقالات"] = article_score
        progress["impact_analysis"]["مقالات"] = {
            "score": article_score,
            "max_possible": 50,
            "impact_percent": min(int((article_score / 50) * 100), 100),
            "description": "مقالات ISI/Scopus بیشترین تاثیر را در استعداد درخشان دارند"
        }

        if current_degree == "دکتری تخصصی":
            thesis_score = 10
            score += thesis_score
            score_details["پایان‌نامه"] = thesis_score
            progress["completed_items"].append("پایان‌نامه تخصصی")
            progress["impact_analysis"]["پایان‌نامه"] = {
                "score": thesis_score,
                "max_possible": 10,
                "impact_percent": 100,
                "description": "پایان‌نامه تخصصی الزامی است"
            }

        presentation_score = 0
        for pres in presentations:
            level = pres.get("level", "")
            result = pres.get("result", "")

            if level == "بین‌المللی":
                presentation_score += 3
                progress["completed_items"].append(f"ارائه بین‌المللی: {pres.get('title', '')[:40]}...")
            else:
                presentation_score += 1
                progress["completed_items"].append(f"ارائه داخلی: {pres.get('title', '')[:40]}...")

            if result == "برگزیده / جایزه":
                presentation_score += 2
                progress["completed_items"].append("🏆 مقاله برتر در کنگره")

        presentation_score = min(presentation_score, 15)
        score += presentation_score
        score_details["ارائه‌ها"] = presentation_score
        progress["impact_analysis"]["ارائه‌ها"] = {
            "score": presentation_score,
            "max_possible": 15,
            "impact_percent": min(int((presentation_score / 15) * 100), 100),
            "description": "ارائه در کنگره‌های بین‌المللی امتیاز بیشتری دارد"
        }

        exec_records = profile_data.get("executive_records", [])
        proposal_count = profile.get("proposal_count") or 0
        research_score = min(proposal_count * 5, 15)
        score += research_score
        score_details["طرح‌های تحقیقاتی"] = research_score
        if proposal_count:
            progress["completed_items"].append(f"{proposal_count} طرح تحقیقاتی")
            progress["impact_analysis"]["طرح‌های تحقیقاتی"] = {
                "score": research_score,
                "max_possible": 15,
                "impact_percent": min(int((research_score / 15) * 100), 100),
                "description": "هر طرح تحقیقاتی ۵ امتیاز دارد"
            }

        extracurricular = profile.get("extracurricular", "")
        if extracurricular:
            committee_score = 10
            score += committee_score
            score_details["کمیته تحقیقات"] = committee_score
            progress["completed_items"].append("فعالیت در کمیته تحقیقات دانشجویی")
            progress["impact_analysis"]["کمیته تحقیقات"] = {
                "score": committee_score,
                "max_possible": 10,
                "impact_percent": 100,
                "description": "فعالیت در کمیته تحقیقات دانشجویی ۱۰ امتیاز دارد"
            }

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

    elif goal == "40_emtiaz":
        score = 0
        score_details = {}

        edu_score = 0
        gpa = 0
        for edu in educations:
            if edu.get("gpa"):
                gpa = edu.get("gpa", 0)
                break
        if gpa >= 18:
            edu_score += 10
            progress["completed_items"].append(f"معدل برتر: {gpa}")
        elif gpa >= 17:
            edu_score += 8
            progress["completed_items"].append(f"معدل خوب: {gpa}")
        elif gpa >= 16:
            edu_score += 5
            progress["completed_items"].append(f"معدل: {gpa}")

        olympic_award = profile.get("olympic_award", "")
        if olympic_award == "طلا":
            edu_score += 10
            progress["completed_items"].append("🥇 مدال طلا المپیاد علمی")
        elif olympic_award == "نقره":
            edu_score += 7
            progress["completed_items"].append("🥈 مدال نقره المپیاد علمی")
        elif olympic_award == "برنز":
            edu_score += 5
            progress["completed_items"].append("🥉 مدال برنز المپیاد علمی")

        edu_score = min(edu_score, 20)
        score += edu_score
        score_details["آموزشی"] = edu_score
        progress["impact_analysis"]["آموزشی"] = {
            "score": edu_score,
            "max_possible": 20,
            "impact_percent": min(int((edu_score / 20) * 100), 100),
            "description": "معدل بالا و المپیاد علمی تا ۲۰ امتیاز دارند"
        }

        article_score = 0
        for article in articles:
            index = article.get("index", "")
            author_rank = article.get("author_rank", 99)

            if index in ["ISI / Web of Science", "ISI + Scopus", "PubMed", "Scopus"]:
                if author_rank == 1:
                    article_score += 7
                    progress["completed_items"].append(f"مقاله ISI/Scopus (نویسنده اول): {article.get('title', '')[:40]}...")
                else:
                    article_score += 4
                    progress["completed_items"].append(f"مقاله ISI/Scopus (همکار): {article.get('title', '')[:40]}...")
            else:
                article_score += 2
                progress["completed_items"].append(f"مقاله: {article.get('title', '')[:40]}...")

        article_score = min(article_score, 15)
        research_score = article_score
        score_details["مقالات"] = article_score
        progress["impact_analysis"]["مقالات"] = {
            "score": article_score,
            "max_possible": 15,
            "impact_percent": min(int((article_score / 15) * 100), 100),
            "description": "مقالات ISI/Scopus با نویسنده اول ۷ امتیاز دارند"
        }

        pres_score = 0
        for pres in presentations:
            level = pres.get("level", "")
            if level == "بین‌المللی":
                pres_score += 2
                progress["completed_items"].append(f"سخنرانی بین‌المللی: {pres.get('title', '')[:40]}...")
            else:
                pres_score += 1.5
                progress["completed_items"].append(f"سخنرانی داخلی: {pres.get('title', '')[:40]}...")

        pres_score = min(pres_score, 5)
        research_score += pres_score
        score_details["ارائه‌ها"] = pres_score
        progress["impact_analysis"]["ارائه‌ها"] = {
            "score": pres_score,
            "max_possible": 5,
            "impact_percent": min(int((pres_score / 5) * 100), 100),
            "description": "سخنرانی بین‌المللی ۲ امتیاز، داخلی ۱.۵ امتیاز"
        }

        proposal_count = profile.get("proposal_count") or 0
        proposal_score = min(proposal_count * 3, 5)
        research_score += proposal_score
        score_details["طرح‌ها"] = proposal_score
        if proposal_count:
            progress["completed_items"].append(f"{proposal_count} طرح تحقیقاتی")
            progress["impact_analysis"]["طرح‌ها"] = {
                "score": proposal_score,
                "max_possible": 5,
                "impact_percent": min(int((proposal_score / 5) * 100), 100),
                "description": "هر طرح تحقیقاتی ۳ امتیاز دارد"
            }

        book_count = profile.get("book_count", 0)
        book_score = min(book_count * 3, 5)
        research_score += book_score
        score_details["کتاب"] = book_score
        if book_count:
            progress["completed_items"].append(f"{book_count} کتاب تألیفی/ترجمه")
            progress["impact_analysis"]["کتاب"] = {
                "score": book_score,
                "max_possible": 5,
                "impact_percent": min(int((book_score / 5) * 100), 100),
                "description": "هر کتاب تألیفی/ترجمه ۳ امتیاز دارد"
            }

        invention = profile.get("invention", "")
        if invention:
            research_score += 7
            score_details["اختراع"] = 7
            progress["completed_items"].append("✅ ثبت اختراع/اکتشاف")
            progress["impact_analysis"]["اختراع"] = {
                "score": 7,
                "max_possible": 7,
                "impact_percent": 100,
                "description": "ثبت اختراع ۷ امتیاز دارد"
            }

        research_score = min(research_score, 20)
        score += research_score
        score_details["پژوهشی"] = research_score
        progress["impact_analysis"]["پژوهشی"] = {
            "score": research_score,
            "max_possible": 20,
            "impact_percent": min(int((research_score / 20) * 100), 100),
            "description": "فعالیت‌های پژوهشی تا ۲۰ امتیاز دارند"
        }

        social_score = 0
        festival_award = profile.get("festival_award", "")
        if festival_award == "اول کشوری":
            social_score += 5
            progress["completed_items"].append("🏆 رتبه اول کشوری جشنواره")
        elif festival_award == "دوم کشوری":
            social_score += 3
            progress["completed_items"].append("🥈 رتبه دوم کشوری جشنواره")
        elif festival_award == "سوم کشوری":
            social_score += 2
            progress["completed_items"].append("🥉 رتبه سوم کشوری جشنواره")

        extracurricular = profile.get("extracurricular", "")
        if extracurricular:
            social_score += 3
            progress["completed_items"].append(f"عضویت فعال: {extracurricular[:50]}")

        volunteer = profile.get("volunteer", "")
        if volunteer:
            social_score += 3
            progress["completed_items"].append(f"فعالیت داوطلبانه: {volunteer[:50]}")

        ethics_award = profile.get("ethics_award", "")
        if ethics_award:
            social_score += 3
            progress["completed_items"].append("⭐ دانشجوی نمونه اخلاق حرفه‌ای")

        social_score = min(social_score, 10)
        score += social_score
        score_details["فردی-اجتماعی-فرهنگی"] = social_score
        progress["impact_analysis"]["فردی-اجتماعی-فرهنگی"] = {
            "score": social_score,
            "max_possible": 10,
            "impact_percent": min(int((social_score / 10) * 100), 100),
            "description": "فعالیت‌های فردی-اجتماعی تا ۱۰ امتیاز دارند"
        }

        min_score = 40
        progress["overall_percent"] = min(int((score / min_score) * 100), 100)
        progress["score_breakdown"] = score_details
        progress["score_breakdown"]["total_score"] = score
        progress["score_breakdown"]["min_score"] = min_score
        progress["score_breakdown"]["remaining"] = max(0, min_score - score)

        if article_score == 0:
            progress["missing_items"].append("انتشار مقاله علمی (تا ۱۵ امتیاز)")
        if pres_score == 0:
            progress["missing_items"].append("ارائه در کنگره (تا ۵ امتیاز)")
        if proposal_count == 0:
            progress["missing_items"].append("همکاری در طرح تحقیقاتی (تا ۵ امتیاز)")
        if not extracurricular:
            progress["missing_items"].append("عضویت فعال در شوراهای دانشجویی (تا ۴ امتیاز)")
        if not volunteer:
            progress["missing_items"].append("فعالیت داوطلبانه (تا ۴ امتیاز)")

    elif goal == "heyat_elmi":
        score = 0

        for edu in educations:
            if edu.get("degree") == "دکتری تخصصی":
                score += 20
                progress["completed_items"].append("دارای دکتری تخصصی")
                progress["impact_analysis"]["دکتری تخصصی"] = {
                    "score": 20, "max_possible": 20, "impact_percent": 100,
                    "description": "دکتری تخصصی الزامی است"
                }
                break
        else:
            progress["missing_items"].append("اتمام دوره تخصصی")
            progress["impact_analysis"]["دکتری تخصصی"] = {
                "score": 0, "max_possible": 20, "impact_percent": 0,
                "description": "دکتری تخصصی الزامی است"
            }

        isi_articles = [a for a in articles if a.get("index") in ["ISI / Web of Science", "Scopus", "ISI + Scopus"]]
        if len(isi_articles) >= 3:
            score += 30
            progress["completed_items"].append(f"{len(isi_articles)} مقاله ISI/Scopus")
            progress["impact_analysis"]["مقالات ISI/Scopus"] = {
                "score": 30, "max_possible": 30, "impact_percent": 100,
                "description": "۳ مقاله ISI/Scopus کافی است"
            }
        elif isi_articles:
            score += 15
            progress["completed_items"].append(f"{len(isi_articles)} مقاله ISI/Scopus")
            progress["impact_analysis"]["مقالات ISI/Scopus"] = {
                "score": 15, "max_possible": 30, "impact_percent": 50,
                "description": "حداقل ۳ مقاله ISI/Scopus نیاز است"
            }
        else:
            progress["missing_items"].append("انتشار مقاله ISI/Scopus")
            progress["impact_analysis"]["مقالات ISI/Scopus"] = {
                "score": 0, "max_possible": 30, "impact_percent": 0,
                "description": "حداقل ۳ مقاله ISI/Scopus نیاز است"
            }

        proposal_count = profile.get("proposal_count") or 0
        if proposal_count:
            score += 20
            progress["completed_items"].append(f"{proposal_count} پروپوزال")
            progress["impact_analysis"]["پروپوزال"] = {
                "score": 20, "max_possible": 20, "impact_percent": 100,
                "description": "داشتن پروپوزال تحقیقاتی الزامی است"
            }
        else:
            progress["missing_items"].append("نوشتن پروپوزال تحقیقاتی")
            progress["impact_analysis"]["پروپوزال"] = {
                "score": 0, "max_possible": 20, "impact_percent": 0,
                "description": "داشتن پروپوزال تحقیقاتی الزامی است"
            }

        exec_records = profile_data.get("executive_records", [])
        if exec_records:
            score += 15
            progress["completed_items"].append("سوابق اجرایی دانشگاهی")
            progress["impact_analysis"]["سوابق اجرایی"] = {
                "score": 15, "max_possible": 15, "impact_percent": 100,
                "description": "سوابق اجرایی دانشگاهی مهم است"
            }
        else:
            progress["missing_items"].append("کسب سوابق اجرایی دانشگاهی")
            progress["impact_analysis"]["سوابق اجرایی"] = {
                "score": 0, "max_possible": 15, "impact_percent": 0,
                "description": "سوابق اجرایی دانشگاهی مهم است"
            }

        writing_skills = profile.get("writing_skills", "")
        if writing_skills:
            score += 15
            progress["completed_items"].append("مهارت نگارش مقاله/پروپوزال")
            progress["impact_analysis"]["مهارت نگارش"] = {
                "score": 15, "max_possible": 15, "impact_percent": 100,
                "description": "مهارت نگارش مقاله/پروپوزال ضروری است"
            }
        else:
            progress["missing_items"].append("تقویت مهارت نگارش")
            progress["impact_analysis"]["مهارت نگارش"] = {
                "score": 0, "max_possible": 15, "impact_percent": 0,
                "description": "مهارت نگارش مقاله/پروپوزال ضروری است"
            }

        progress["overall_percent"] = min(score, 100)
        progress["score_breakdown"]["score"] = score

    elif goal == "research_position":
        score = 0

        english_level = profile.get("english_level", "")
        if english_level in ["B2", "C1", "C2"]:
            score += 25
            progress["completed_items"].append(f"زبان انگلیسی: {english_level}")
            progress["impact_analysis"]["زبان انگلیسی"] = {
                "score": 25, "max_possible": 25, "impact_percent": 100,
                "description": "زبان انگلیسی B2 یا بالاتر الزامی است"
            }
        elif english_level in ["A2", "B1"]:
            score += 10
            progress["completed_items"].append(f"زبان انگلیسی: {english_level} (نیاز به تقویت)")
            progress["impact_analysis"]["زبان انگلیسی"] = {
                "score": 10, "max_possible": 25, "impact_percent": 40,
                "description": "زبان انگلیسی نیاز به تقویت دارد"
            }
        else:
            progress["missing_items"].append("تقویت زبان انگلیسی")
            progress["impact_analysis"]["زبان انگلیسی"] = {
                "score": 0, "max_possible": 25, "impact_percent": 0,
                "description": "زبان انگلیسی B2 یا بالاتر الزامی است"
            }

        article_count = len(articles)
        if article_count >= 2:
            score += 25
            progress["completed_items"].append(f"{article_count} مقاله منتشر شده")
            progress["impact_analysis"]["مقالات"] = {
                "score": 25, "max_possible": 25, "impact_percent": 100,
                "description": "حداقل ۲ مقاله نیاز است"
            }
        elif article_count == 1:
            score += 15
            progress["completed_items"].append("۱ مقاله منتشر شده")
            progress["impact_analysis"]["مقالات"] = {
                "score": 15, "max_possible": 25, "impact_percent": 60,
                "description": "حداقل ۲ مقاله نیاز است"
            }
        else:
            progress["missing_items"].append("نوشتن و انتشار مقاله")
            progress["impact_analysis"]["مقالات"] = {
                "score": 0, "max_possible": 25, "impact_percent": 0,
                "description": "حداقل ۲ مقاله نیاز است"
            }

        if profile_data.get("executive_records") or courses:
            score += 20
            progress["completed_items"].append("سوابق تحقیقاتی")
            progress["impact_analysis"]["سوابق تحقیقاتی"] = {
                "score": 20, "max_possible": 20, "impact_percent": 100,
                "description": "سوابق تحقیقاتی مهم است"
            }
        else:
            progress["missing_items"].append("کسب سوابق تحقیقاتی")
            progress["impact_analysis"]["سوابق تحقیقاتی"] = {
                "score": 0, "max_possible": 20, "impact_percent": 0,
                "description": "سوابق تحقیقاتی مهم است"
            }

        if presentations:
            score += 15
            progress["completed_items"].append(f"{len(presentations)} ارائه علمی")
            progress["impact_analysis"]["ارائه‌ها"] = {
                "score": 15, "max_possible": 15, "impact_percent": 100,
                "description": "ارائه در کنفرانس مهم است"
            }
        else:
            progress["missing_items"].append("ارائه در کنفرانس")
            progress["impact_analysis"]["ارائه‌ها"] = {
                "score": 0, "max_possible": 15, "impact_percent": 0,
                "description": "ارائه در کنفرانس مهم است"
            }

        proposal_count = profile.get("proposal_count") or 0
        if proposal_count:
            score += 15
            progress["completed_items"].append("دارای پروپوزال تحقیقاتی")
            progress["impact_analysis"]["پروپوزال"] = {
                "score": 15, "max_possible": 15, "impact_percent": 100,
                "description": "داشتن پروپوزال تحقیقاتی مهم است"
            }
        else:
            progress["missing_items"].append("نوشتن پروپوزال")
            progress["impact_analysis"]["پروپوزال"] = {
                "score": 0, "max_possible": 15, "impact_percent": 0,
                "description": "داشتن پروپوزال تحقیقاتی مهم است"
            }

        progress["overall_percent"] = min(score, 100)
        progress["score_breakdown"]["score"] = score

    else:
        # goal == "general" یا هر مقدار ناشناخته دیگر
        logger.info(f"هدف '{goal}' فاقد قاعده امتیازدهی اختصاصی است؛ مقادیر پیش‌فرض برگردانده می‌شود.")

    return progress



def _parse_json_response(response_text: str) -> dict:
    """
    استخراج و پارس کردن JSON از پاسخ متنی مدل.
    مدل ممکن است JSON را داخل ```json ... ``` قرار دهد یا متن اضافی
    قبل/بعد از آن بیاورد؛ این تابع این موارد را مدیریت می‌کند.
    """
    if not response_text or not response_text.strip():
        logger.error("پاسخ خالی از API دریافت شد.")
        raise ValueError("پاسخ خالی از مدل دریافت شد.")

    text = response_text.strip()

    fence_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"خطا در پارس JSON پاسخ مدل: {e}\nمتن دریافتی (خلاصه):\n{response_text[:2000]}")
        raise ValueError(f"پاسخ مدل به فرمت JSON معتبر نبود: {str(e)}")
    


def _normalize_roadmap_data(data: dict, duration_days: int) -> dict:
    """
    اطمینان از وجود تمام فیلدهای موردنیاز مدل‌های Roadmap/Stage/Activity
    و اصلاح مقادیر نامعتبر (enum ها) برای جلوگیری از خطا هنگام ذخیره در دیتابیس.
    """
    if not isinstance(data, dict):
        logger.error("پاسخ مدل یک دیکشنری معتبر نیست.")
        raise ValueError("ساختار پاسخ مدل نامعتبر است.")

    normalized = {
        "title": data.get("title") or "رودمپ بدون عنوان",
        "description": data.get("description") or "",
        "stages": [],
        "quantitative_analysis": data.get("quantitative_analysis", {}) or {},
    }

    valid_phase_types = {"foundation", "development", "optimization", "execution"}
    valid_priorities = {"low", "medium", "high"}
    valid_categories = {"course", "event", "project", "research"}
    valid_difficulties = {"easy", "medium", "hard"}

    stages = data.get("stages") or []
    if not stages:
        logger.warning("مدل هیچ مرحله‌ای (stages) برنگرداند.")

    for i, stage in enumerate(stages, start=1):
        if not isinstance(stage, dict):
            logger.warning(f"مرحله شماره {i} فرمت نامعتبر دارد و نادیده گرفته شد.")
            continue

        phase_type = stage.get("phase_type")
        if phase_type not in valid_phase_types:
            phase_type = "development"

        priority = stage.get("priority")
        if priority not in valid_priorities:
            priority = "medium"

        try:
            stage_duration = max(1, int(stage.get("duration_days") or 30))
        except (TypeError, ValueError):
            stage_duration = 30

        activities = []
        for activity in (stage.get("activities") or []):
            if not isinstance(activity, dict):
                continue

            category = activity.get("category")
            if category not in valid_categories:
                category = "course"

            difficulty_rating = activity.get("difficulty_rating")
            if difficulty_rating not in valid_difficulties:
                difficulty_rating = "medium"

            try:
                impact_score = int(activity.get("impact_score", 5))
            except (TypeError, ValueError):
                impact_score = 5
            impact_score = min(max(impact_score, 1), 10)

            try:
                activity_duration = max(1, int(activity.get("duration_days") or 7))
            except (TypeError, ValueError):
                activity_duration = 7

            activities.append({
                "title": activity.get("title") or "فعالیت بدون عنوان",
                "description": activity.get("description") or "",
                "category": category,
                "duration_days": activity_duration,
                "impact_score": impact_score,
                "difficulty_rating": difficulty_rating,
                "resume_output": activity.get("resume_output") or "",
            })

        if not activities:
            logger.warning(f"مرحله '{stage.get('title', i)}' هیچ فعالیتی نداشت.")

        normalized["stages"].append({
            "order": stage.get("order") or i,
            "title": stage.get("title") or f"مرحله {i}",
            "description": stage.get("description") or "",
            "objectives": stage.get("objectives") or "",
            "phase_type": phase_type,
            "priority": priority,
            "duration_days": stage_duration,
            "milestone": stage.get("milestone") or "",
            "success_criteria": stage.get("success_criteria") or [],
            "risks": stage.get("risks") or [],
            "recommended_resources": stage.get("recommended_resources") or [],
            "activities": activities,
        })

    normalized["stages"].sort(key=lambda s: s["order"])
    for idx, stage in enumerate(normalized["stages"], start=1):
        stage["order"] = idx

    total_stage_days = sum(s["duration_days"] for s in normalized["stages"])
    if total_stage_days and total_stage_days > duration_days:
        logger.warning(
            f"مجموع مدت زمان مراحل ({total_stage_days} روز) بیشتر از duration_days "
            f"درخواستی ({duration_days} روز) است."
        )

    return normalized



def generate_roadmap(profile_data: dict, goal: str, duration_days: int, goal_details: str = "") -> dict:
    """
    تولید نقشه راه شخصی‌سازی شده بر اساس داده‌های پروفایل و اهداف کاربر.

    Args:
        profile_data: داده‌های پروفایل (خروجی collect_profile_data)
        goal: کلید هدف کاربر مطابق GOAL_CHOICES مدل Roadmap
        duration_days: مدت زمان کل رودمپ به روز (از UI انتخاب می‌شود)
        goal_details: جزئیات اضافی هدف که کاربر در UI وارد کرده است

    Returns:
        دیکشنری سازگار با مدل‌های Roadmap/Stage/Activity:
        {
            "title": "...", "description": "...",
            "stages": [{...}], "quantitative_analysis": {...}, "progress": {...}
        }
    """
    logger.info(f"شروع تولید رودمپ | goal={goal} | duration_days={duration_days}")

    profile_json = json.dumps(profile_data, ensure_ascii=False, indent=2)
    goal_label = GOAL_LABELS.get(goal, goal)
    goal_prompt = _load_goal_prompt(goal)

    try:
        progress = _calculate_progress(profile_data, goal)
    except Exception:
        logger.exception("خطا در محاسبه درصد پیشرفت کاربر.")
        progress = {
            "overall_percent": 0, "completed_items": [], "missing_items": [],
            "score_breakdown": {}, "impact_analysis": {},
        }

    progress_json = json.dumps(progress, ensure_ascii=False, indent=2)

    system_prompt = """
    تو مشاور ارشد رزومه و مسیر شغلی/پژوهشی علوم پزشکی برای دانشجویان و پزشکان ایرانی هستی. برای اهدافی مثل «استعداد درخشان»، «۴۰ امتیازی»، «هیات علمی» یا «ریسرچ پوزیشن خارج از کشور» نقشه راه دقیق و شخصی‌سازی‌شده طراحی می‌کنی.

    # قانون تعداد مراحل و فعالیت‌ها (اکید و غیرقابل‌تخطی)
    بر اساس duration_days کل رودمپ، دقیقاً از این جدول پیروی کن (خارج شدن از بازه = خطا):

    | duration_days | تعداد stages | تعداد کل activities |
    |---|---|---|
    | ≤ 30 | 2-3 | 2-8 |
    | 31-90 | 3-4 | 7-13 |
    | 91-180 | 4-5 | 10-15 |
    | 181-365 | 5-6 | 13-22 |
    | > 365 | 6-8 | 20-35 |

    قبل از تولید خروجی، duration_days ورودی را در جدول پیدا کن و عدد stages/activities را از همان بازه انتخاب کن؛ سپس مجموع duration_days مراحل را چک کن که از کل duration_days بیشتر نشود (حداکثر ۵٪ کمتر مجاز است، هرگز بیشتر). مجموع duration_days فعالیت‌های هر مرحله هم نباید از duration_days همان مرحله بیشتر شود.

    # خروجی
    فقط یک JSON معتبر و کامل مطابق output_schema برگردان؛ بدون هیچ متن، توضیح یا فنس مارک‌داون. اولین کاراکتر `{` و آخرین `}` باشد. هیچ کلیدی حذف یا اضافه نشود.
    مقادیر enum فقط از این گزینه‌ها:
    - phase_type: foundation | development | optimization | execution
    - priority: low | medium | high
    - category: course | event | project | research
    - difficulty_rating: easy | medium | hard
    - impact_level: high | medium | low
    success_criteria، risks، recommended_resources همیشه آرایه رشته‌ای‌اند. impact_score عدد صحیح ۱ تا ۱۰.

    # قوانین محتوا
    1. title دقیقاً به فرم «نقشه راه {duration_days} روزه برای {هدف مشخص کاربر}» باشد.
    2. description کل رودمپ: ۵-۷ جمله مشخص درباره‌ی موقعیت فعلی کاربر (بر اساس profile/progress)، مسیر رودمپ و هدف نهایی — نه کلی‌گویی.
    3. در هر stage: description، objectives، milestone و success_criteria باید کامل، مشخص و قابل‌سنجش باشند؛ نه کوتاه یا کلیشه‌ای.
    4. اولویت مراحل بر اساس ضعیف‌ترین بخش‌های progress (کمترین current_score/percent_of_total، بیشترین impact_level) تعیین شود؛ ابتدا مهم‌ترین کمبودها.
    5. goal_details کاربر باید مستقیماً در عنوان/توضیح فعالیت‌ها (موضوع مقاله، حوزه تخصصی، کنگره و...) منعکس شود؛ از عناوین کلیشه‌ای و مبهم پرهیز کن.
    6. quantitative_analysis دقیقاً بازتاب عددی progress ورودی باشد (نه اعداد اختراعی)؛ sections شامل بخش‌های کلیدی score_breakdown/impact_analysis با ۱-۲ توصیه عملی برای هرکدام.

    فقط JSON نهایی را برگردان.
    """


    output_schema = """
ساختار دقیق خروجی JSON:
{
  "title": "عنوان نقشه راه",
  "description": "توضیح کلی نقشه راه",
  "stages": [
    {
      "order": 1,
      "title": "عنوان مرحله",
      "description": "توضیحات مرحله",
      "objectives": "اهداف این مرحله",
      "phase_type": "foundation | development | optimization | execution",
      "priority": "low | medium | high",
      "duration_days": 30,
      "milestone": "معیار تکمیل این مرحله",
      "success_criteria": ["معیار ۱", "معیار ۲"],
      "risks": ["ریسک ۱", "ریسک ۲"],
      "recommended_resources": ["منبع ۱", "منبع ۲"],
      "activities": [
        {
          "title": "عنوان فعالیت",
          "description": "توضیح فعالیت",
          "category": "course | event | project | research",
          "duration_days": 7,
          "impact_score": 1,
          "difficulty_rating": "easy | medium | hard",
          "resume_output": "خروجی که به رزومه اضافه می‌شود"
        }
      ]
    }
  ],
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
        "impact_level": "high | medium | low",
        "recommendations": ["پیشنهاد ۱"]
      }
    }
  }
}"""

    user_prompt = f"""اطلاعات پروفایل کاربر:
    {profile_json}

    هدف انتخابی کاربر: {goal_label} (کلید: {goal})
    مدت زمان کل رودمپ: {duration_days} روز
    جزئیات هدف که کاربر وارد کرده: {goal_details or "توضیحی وارد نشده است"}

    {f"فایل راهنمای هدف:{chr(10)}{goal_prompt}" if goal_prompt else ""}

    تحلیل کمی فعلی کاربر (progress):
    {progress_json}

    دستورالعمل نهایی:
    1. طبق قانون «تعیین تعداد مراحل بر اساس duration_days» در system prompt، برای duration_days برابر {duration_days} روز، تعداد مراحل و فعالیت‌های مناسب را انتخاب کن.
    2. مجموع duration_days مراحل نباید از {duration_days} روز بیشتر شود.
    3. اولویت مراحل را بر اساس ضعیف‌ترین بخش‌های progress (بیشترین remaining/کمترین impact_percent) تعیین کن.
    4. جزئیات هدف کاربر ({goal_details or "-"}) را مستقیماً در عنوان/توضیح فعالیت‌ها منعکس کن.
    5. quantitative_analysis را با اعداد سازگار با progress بالا (نه اعداد جدید و بی‌ربط) پر کن.
    6. خروجی را دقیقاً مطابق output_schema زیر و بدون هیچ متن اضافه برگردان.

    {output_schema}"""


    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        response_text = _call_gpt_api(messages, max_tokens=6000)
    except Exception:
        logger.exception("خطا در فراخوانی API تولید رودمپ.")
        raise

    try:
        result = _parse_json_response(response_text)
    except Exception:
        logger.exception("خطا در پارس پاسخ JSON مدل هنگام تولید رودمپ.")
        raise

    try:
        result = _normalize_roadmap_data(result, duration_days)
    except Exception:
        logger.exception("خطا در نرمال‌سازی داده‌های رودمپ.")
        raise

    result["progress"] = progress

    logger.info(f"رودمپ با موفقیت تولید شد | تعداد مراحل: {len(result.get('stages', []))}")
    return result
