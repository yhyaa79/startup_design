# roadmap/services/profile_data.py

from accounts.models import Profile


def _safe_date(value):
    if not value:
        return ""
    return str(value)


def _collect_profile_data(profile: Profile) -> dict:
    """
    جمع‌آوری داده‌های پروفایل به صورت دیکشنری برای ارسال به AI.
    """

    return {
        "profile": {
            "first_name": profile.first_name or "",
            "last_name": profile.last_name or "",
            "gender": profile.gender or "",
            "marital_status": profile.marital_status or "",
            "military_status": profile.military_status or "",
            "job_title": profile.job_title or "",
            "birth_date": _safe_date(profile.birth_date),
            "country": profile.country or "",
            "city": profile.city or "",
            "phone": profile.phone or "",
            "email": profile.email or "",
            "website": profile.website or "",
            "national_id": profile.national_id or "",
            "orcid": profile.orcid or "",
            "proposal_count": profile.proposal_count or 0,
            "proposal_status": profile.proposal_status or "",
            "software_skills": profile.software_skills or "",
            "writing_skills": profile.writing_skills or "",
            "clinical_certs": profile.clinical_certs or "",
            "clinical_exp": profile.clinical_exp or "",
            "procedures": profile.procedures or "",
            "native_lang": profile.native_lang or "",
            "english_level": profile.english_level or "",
            "lang_cert": profile.lang_cert or "",
            "other_langs": profile.other_langs or "",
            "extracurricular": profile.extracurricular or "",
            "goal": profile.goal or "",
            "specialty": profile.specialty or "",
            "goal_notes": profile.goal_notes or "",
            "service_plan": profile.service_plan or "",
        },

        "social_profiles": [
            {
                "social_type": sp.social_type or "",
                "url": sp.url or "",
            }
            for sp in profile.social_profiles.all()
        ],

        "educations": [
            {
                "field": edu.field or "",
                "degree": edu.degree or "",
                "university": edu.university or "",
                "uni_type": edu.uni_type or "",
                "start_date": _safe_date(edu.start_date),
                "end_date": _safe_date(edu.end_date),
                "stage": edu.stage or "",
                "current_term": edu.current_term or 0,
                "remaining_terms": edu.remaining_terms or 0,
                "gpa": float(edu.gpa) if edu.gpa else None,
            }
            for edu in profile.educations.all()
        ],

        "articles": [
            {
                "title": article.title or "",
                "journal": article.journal or "",
                "impact_factor": float(article.impact_factor) if article.impact_factor else None,
                "quartile": article.quartile or "",
                "year": article.year,
                "author_rank": article.author_rank,
                "total_authors": article.total_authors,
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

        "executive_records": [
            {
                "title": rec.title or "",
                "start_date": _safe_date(rec.start_date),
                "end_date": _safe_date(rec.end_date),
            }
            for rec in profile.executive_records.all()
        ],

        "training_courses": [
            {
                "title": course.title or "",
                "category": course.category or "",
                "status": course.status or "",
                "organizer": course.organizer or "",
                "date": _safe_date(course.date),
                "certificate": course.certificate or "",
                "skills_gained": course.skills_gained or "",
            }
            for course in profile.training_courses.all()
        ],
    }
