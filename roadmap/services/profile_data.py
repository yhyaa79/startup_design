# roadmap/services/profile_data.py

"""
جمع‌آوری داده‌های پروفایل
"""

from accounts.models import Profile


def _safe_date(value):
    """تبدیل تاریخ به string"""
    if not value:
        return ""
    return str(value)


def collect_profile_data(profile: Profile) -> dict:
    """جمع‌آوری داده‌های پروفایل"""
    
    return {
        "profile": {
            "first_name": profile.first_name or "",
            "last_name": profile.last_name or "",
            "gender": profile.gender or "",
            "job_title": profile.job_title or "",
            "email": profile.email or "",
            "english_level": profile.english_level or "",
            "lang_cert": profile.lang_cert or "",
            "software_skills": profile.software_skills or "",
            "writing_skills": profile.writing_skills or "",
            "clinical_exp": profile.clinical_exp or "",
            "extracurricular": profile.extracurricular or "",
            "goal": profile.goal or "",
            "specialty": profile.specialty or "",
            "proposal_count": profile.proposal_count or 0,
        },
        
        "educations": [
            {
                "field": edu.field or "",
                "degree": edu.degree or "",
                "university": edu.university or "",
                "start_date": _safe_date(edu.start_date),
                "end_date": _safe_date(edu.end_date),
                "gpa": float(edu.gpa) if edu.gpa else None,
                "current_term": edu.current_term or 0,
                "remaining_terms": edu.remaining_terms or 0,
            }
            for edu in profile.educations.all()
        ],
        
        "articles": [
            {
                "title": article.title or "",
                "journal": article.journal or "",
                "impact_factor": float(article.impact_factor) if article.impact_factor else None,
                "year": article.year,
                "author_rank": article.author_rank,
                "index": article.index or "",
            }
            for article in profile.articles.all()
        ],
        
        "presentations": [
            {
                "title": pres.title or "",
                "event": pres.event or "",
                "level": pres.level or "",
                "result": pres.result or "",
            }
            for pres in profile.presentations.all()
        ],
        
        "training_courses": [
            {
                "title": course.title or "",
                "category": course.category or "",
                "organizer": course.organizer or "",
                "date": _safe_date(course.date),
            }
            for course in profile.training_courses.all()
        ],
        
        "executive_records": [
            {
                "title": rec.title or "",
                "start_date": _safe_date(rec.start_date),
                "end_date": _safe_date(rec.end_date),
            }
            for rec in profile.executive_records.all()
        ],
    }
