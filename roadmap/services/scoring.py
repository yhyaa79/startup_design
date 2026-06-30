"""
سیستم امتیازدهی
"""

from datetime import date


def calculate_roadmap_score(roadmap, profile_data: dict) -> dict:
    """محاسبه امتیاز رودمپ"""
    
    goal = roadmap.goal
    score_breakdown = {}
    total_score = 0
    
    if goal == 'estedad_darakhshan':
        score_breakdown = _score_estedad(profile_data)
    elif goal == '40_emtiaz':
        score_breakdown = _score_40emtiaz(profile_data)
    elif goal == 'heyat_elmi':
        score_breakdown = _score_heyat_elmi(profile_data)
    elif goal == 'research_position':
        score_breakdown = _score_research_position(profile_data)
    
    total_score = sum(v.get('score', 0) for v in score_breakdown.values())
    
    return {
        'total_score': total_score,
        'breakdown': score_breakdown,
    }


def _score_estedad(profile_data: dict) -> dict:
    """امتیازدهی استعداد درخشان"""
    
    articles = profile_data.get('articles', [])
    presentations = profile_data.get('presentations', [])
    
    isi_articles = [
        a for a in articles 
        if a.get('index') in ['ISI / Web of Science', 'ISI + Scopus', 'Scopus']
    ]
    
    return {
        'articles': {
            'score': min(len(isi_articles) * 10, 50),
            'detail': f'{len(isi_articles)} مقاله ISI'
        },
        'presentations': {
            'score': min(len(presentations) * 5, 20),
            'detail': f'{len(presentations)} ارائه'
        },
    }


def _score_40emtiaz(profile_data: dict) -> dict:
    """امتیازدهی 40 امتیازی"""
    
    educations = profile_data.get('educations', [])
    articles = profile_data.get('articles', [])
    
    gpa = float(educations[0].get('gpa') or 0) if educations else 0
    
    isi_articles = [
        a for a in articles 
        if a.get('index') in ['ISI / Web of Science', 'ISI + Scopus', 'Scopus']
    ]
    
    edu_score = 10 if gpa >= 18 else (8 if gpa >= 17 else (5 if gpa >= 16 else 0))
    
    return {
        'educational': {
            'score': edu_score,
            'detail': f'معدل: {gpa}'
        },
        'research': {
            'score': min(len(isi_articles) * 7, 20),
            'detail': f'{len(isi_articles)} مقاله ISI'
        },
    }


def _score_heyat_elmi(profile_data: dict) -> dict:
    """امتیازدهی هیات علمی"""
    
    educations = profile_data.get('educations', [])
    articles = profile_data.get('articles', [])
    
    degree = educations[0].get('degree', '') if educations else ''
    
    isi_articles = [
        a for a in articles 
        if a.get('index') in ['ISI / Web of Science', 'ISI + Scopus', 'Scopus']
    ]
    
    phd_score = 30 if degree == 'دکتری تخصصی' else 0
    
    return {
        'degree': {
            'score': phd_score,
            'detail': f'مقطع: {degree}'
        },
        'research': {
            'score': min(len(isi_articles) * 10, 40),
            'detail': f'{len(isi_articles)} مقاله ISI'
        },
    }


def _score_research_position(profile_data: dict) -> dict:
    """امتیازدهی ریسرچ پوزیشن"""
    
    profile = profile_data.get('profile', {})
    articles = profile_data.get('articles', [])
    
    english_level = profile.get('english_level', '')
    lang_cert = profile.get('lang_cert', '')
    
    intl_articles = [
        a for a in articles 
        if a.get('index') in ['ISI / Web of Science', 'ISI + Scopus', 'Scopus']
    ]
    
    lang_score = 20 if english_level in ['B2', 'C1', 'C2'] else (10 if english_level == 'B1' else 0)
    cert_score = 10 if lang_cert else 0
    
    return {
        'language': {
            'score': lang_score + cert_score,
            'detail': f'زبان: {english_level}, مدرک: {"دارد" if lang_cert else "ندارد"}'
        },
        'research': {
            'score': min(len(intl_articles) * 15, 50),
            'detail': f'{len(intl_articles)} مقاله بین‌المللی'
        },
    }
