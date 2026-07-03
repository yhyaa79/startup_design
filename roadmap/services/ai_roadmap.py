# roadmap/services/ai_roadmap.py 
"""
سرویس تولید رودمپ حرفه‌ای با AI
"""

import json
import logging
import re
import time

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 120
MAX_RETRIES = 2


def _call_gpt_api(messages: list, max_tokens: int = 12000, model: str = None) -> str:
    """فراخوانی API GPT"""
    print(f"messages::::{messages}")
    if not settings.GAPGPT_API_KEY:
        raise ValueError("GAPGPT_API_KEY تنظیم نشده است.")

    url = f"{settings.GAPGPT_API_BASE}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GAPGPT_API_KEY}",
    }

    payload = {
        "model": model or settings.GAPGPT_MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Calling GPT API (attempt %s/%s) model=%s", attempt, MAX_RETRIES, payload["model"])
            start = time.monotonic()

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )

            elapsed = time.monotonic() - start
            logger.info("GPT API responded in %.2f seconds", elapsed)

            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.ReadTimeout:
            logger.warning("Read timeout on attempt %s", attempt)
            if attempt == MAX_RETRIES:
                logger.exception("Final timeout failure.")
                raise TimeoutError("زمان پاسخ API به پایان رسید.")
            time.sleep(1.5)

        except requests.exceptions.ConnectionError:
            logger.exception("Connection error while calling GPT API.")
            raise ConnectionError("خطا در اتصال به API.")

        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response else ""
            text = e.response.text if e.response else ""
            logger.exception("HTTP error from API: %s", code)
            raise ValueError(f"خطای HTTP {code}: {text}")

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.exception("Invalid API response structure.")
            raise ValueError(f"ساختار پاسخ API نامعتبر: {e}")

        except Exception:
            logger.exception("Unexpected error in _call_gpt_api.")
            raise


def _parse_json_response(text: str) -> dict:
    """استخراج JSON از پاسخ"""
    text = text.strip()

    # الگوهای مختلف برای استخراج JSON
    patterns = [
        r"```json\s*([\s\S]*?)\s*```",
        r"```\s*([\s\S]*?)\s*```",
        r"(\{[\s\S]*\})",  # هر JSON معتبر
    ]
    
    extracted_json = None
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            extracted_json = m.group(1).strip()
            break
    
    if not extracted_json:
        extracted_json = text

    # تلاش برای تصحیح JSON ناقص
    try:
        return json.loads(extracted_json)
    except json.JSONDecodeError:
        # اگر JSON ناقص است، سعی کنید آن را تکمیل کنید
        if extracted_json.count('{') > extracted_json.count('}'):
            extracted_json += '}' * (extracted_json.count('{') - extracted_json.count('}'))
        
        try:
            return json.loads(extracted_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Attempted text: {extracted_json[:1000]}")
            raise ValueError(f"خطا در پارس JSON: {e}\n\nمتن:\n{extracted_json[:500]}")




def generate_roadmap(profile_data: dict, goal: str, duration_days: int) -> dict:
    """تولید رودمپ حرفه‌ای با AI"""
    logger.info("Generating roadmap | goal=%s | duration=%s", goal, duration_days)

    gap_analysis = _calculate_gap_analysis(profile_data, goal)
    system_prompt = _build_system_prompt(goal)
    goal_context = _build_goal_context(goal, duration_days, gap_analysis)
    user_prompt = _build_user_prompt(profile_data, gap_analysis, duration_days)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{goal_context}\n\n{user_prompt}"},
    ]

    max_attempts = 3
    for attempt in range(max_attempts):
        model = settings.GAPGPT_MODEL_NAME if attempt == 0 else settings.GAPGPT_MODEL_NAME_2
        try:
            logger.info("Roadmap attempt %s/%s using model=%s", attempt + 1, max_attempts, model)
            response = _call_gpt_api(messages, max_tokens=12000, model=model)
            roadmap_data = _parse_json_response(response)
            logger.info("Roadmap generated successfully on attempt %s.", attempt + 1)
            return roadmap_data
        except ValueError as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                raise
            time.sleep(2)




def _build_system_prompt(goal: str) -> str:
    """ساخت system prompt"""
    
    return f"""شما یک متخصص برنامه‌ریزی آموزشی برای دانشجویان علوم پزشکی ایران هستید.

        وظیفه شما تولید نقشه راه (Roadmap) حرفه‌ای و دقیق برای رسیدن به هدف: {goal}

        قوانین زمان‌بندی:
        1. مدت زمان هر مرحله باید ثابت و منطقی باشد.
        2. مجموع duration_days فعالیت‌ها باید دقیقاً برابر duration_days مرحله باشد.
        3. اگر total duration کمتر شد، تعداد فعالیت‌ها را کاهش بده، نه مدت زمان هر فعالیت را.
        4. فعالیت‌های مهم‌تر را حفظ کن و فعالیت‌های کم‌اثر را حذف یا ادغام کن.
        5. برای هر مرحله 3 تا 5 فعالیت تولید کن، اما اگر زمان کم است حداقل 2 فعالیت بسیار مؤثر تولید کن.
        6. مدت هر فعالیت باید واقع‌گرایانه باشد و از 2 روز کمتر و از 10 روز بیشتر نشود، مگر در فعالیت‌های پژوهشی بلندمدت.
        7. از اسم کاربر توی توضیحات یا هیچ متنی استفاده نکن.

        فقط JSON معتبر برگردان.
        هیچ توضیحی خارج از JSON ننویس.
        از markdown code fence مثل 
        ```json استفاده نکن.
        """



def _build_goal_context(goal: str, duration_days: int, gap_analysis: dict) -> str:
    """ساخت goal context"""
    
    goal_map = {
        'estedad_darakhshan': '''
هدف: استعداد درخشان
- حداقل امتیاز بر اساس مقطع تحصیلی
- تاکید بر مقالات ISI/Scopus
- ارائه در کنگره‌های معتبر
- طرح‌های تحقیقاتی مصوب
- فعالیت‌های فوق‌برنامه
        ''',
        '40_emtiaz': '''
هدف: ۴۰ امتیازی
- معدل بالا (17+)
- مقالات ISI معتبر
- ارائه‌های علمی
- سوابق اجرایی
- فعالیت‌های اجتماعی
        ''',
        'heyat_elmi': '''
هدف: هیات علمی
- دکتری تخصصی الزامی
- حداقل 3 مقاله ISI
- تجربه PI/Co-I در طرح‌های مصوب
- سوابق اجرایی دانشگاهی
- مهارت‌های نگارش و تحقیق
        ''',
        'research_position': '''
هدف: ریسرچ پوزیشن / فلوشیپ خارج
- سطح زبان B2+ الزامی
- مقالات بین‌المللی معتبر
- ارائه‌های بین‌المللی
- Research Statement حرفه‌ای
- شبکه‌سازی بین‌المللی
        ''',
    }
    
    context = goal_map.get(goal, '')
    
    current_score = gap_analysis.get('score', {})
    critical_gaps = gap_analysis.get('critical_gaps', [])
    
    context += f"\n\nوضعیت فعلی:\n"
    context += f"- امتیاز فعلی: {current_score.get('current', 0)}\n"
    context += f"- کمبودهای حیاتی: {', '.join(critical_gaps[:3])}\n"
    context += f"- مدت زمان دسترسی: {duration_days} روز\n"
    
    return context


def _build_user_prompt(profile_data: dict, gap_analysis: dict, duration_days: int) -> str:
    """ساخت user prompt"""
    
    profile = profile_data.get('profile', {})
    educations = profile_data.get('educations', [])
    articles = profile_data.get('articles', [])
    
    current_edu = educations[0] if educations else {}
    
    prompt = f"""
داده‌های کاربر:
- نام: {profile.get('first_name', '')} {profile.get('last_name', '')}
- مقطع: {current_edu.get('degree', 'نامشخص')}
- دانشگاه: {current_edu.get('university', 'نامشخص')}
- معدل: {current_edu.get('gpa', 'نامشخص')}
- تعداد مقالات: {len(articles)}
- سطح زبان انگلیسی: {profile.get('english_level', 'نامشخص')}

کمبودهای شناسایی‌شده:
- حیاتی: {', '.join(gap_analysis.get('critical_gaps', []))}
- مهم: {', '.join(gap_analysis.get('important_gaps', []))}

لطفاً نقشه راه جامعی برای {duration_days} روز آینده ایجاد کنید که:
1. کمبودهای حیاتی را رفع کند
2. اولویت‌ها را رعایت کند
3. زمان‌بندی واقع‌گرایانه داشته باشد

خروجی JSON:
{{
    "title": "عنوان رودمپ",
    "description": "توضیحات کلی",
    "stages": [
        {{
            "order": 1,
            "title": "عنوان مرحله",
            "description": "توضیحات",
            "objectives": "اهداف",
            "phase_type": "foundation|development|optimization|execution",
            "priority": "low|medium|high",
            "duration_days": 30,
            "milestone": "معیار تکمیل",
            "success_criteria": ["معیار 1", "معیار 2"],
            "risks": ["ریسک 1", "ریسک 2"],
            "recommended_resources": [
                {{"title": "عنوان", "type": "وب‌سایت|نرم‌افزار|کتاب", "description": "توضیح"}}
            ],
            "activities": [
                {{
                    "title": "عنوان فعالیت",
                    "category": "course|event|project|research",
                    "duration_days": 7,
                    "description": "توضیح",
                    "impact_score": 8,
                    "difficulty_rating": "easy|medium|hard",
                    "resume_output": "خروجی رزومه"
                }}
            ]
        }}
    ]
}}
"""
    
    return prompt


def _calculate_gap_analysis(profile_data: dict, goal: str) -> dict:
    """تحلیل شکاف"""
    
    profile = profile_data.get('profile', {})
    educations = profile_data.get('educations', [])
    articles = profile_data.get('articles', [])
    presentations = profile_data.get('presentations', [])
    courses = profile_data.get('training_courses', [])
    
    current_edu = educations[0] if educations else {}
    
    isi_articles = [
        a for a in articles 
        if a.get('index') in ['ISI / Web of Science', 'ISI + Scopus', 'Scopus', 'PubMed']
    ]
    
    analysis = {
        'current_status': {
            'degree': current_edu.get('degree', 'نامشخص'),
            'gpa': current_edu.get('gpa', 0),
            'total_articles': len(articles),
            'isi_articles': len(isi_articles),
            'presentations': len(presentations),
            'courses': len(courses),
            'english_level': profile.get('english_level', ''),
        },
        'strengths': [],
        'critical_gaps': [],
        'important_gaps': [],
        'score': {},
    }
    
    # تحلیل بر اساس هدف
    if goal == 'estedad_darakhshan':
        _analyze_estedad(analysis, profile, articles, isi_articles, presentations)
    elif goal == '40_emtiaz':
        _analyze_40emtiaz(analysis, profile, articles, isi_articles, current_edu)
    elif goal == 'heyat_elmi':
        _analyze_heyat_elmi(analysis, profile, articles, isi_articles, current_edu)
    elif goal == 'research_position':
        _analyze_research_position(analysis, profile, articles, isi_articles)
    
    return analysis


def _analyze_estedad(analysis, profile, articles, isi_articles, presentations):
    """تحلیل برای استعداد درخشان"""
    
    if len(isi_articles) == 0:
        analysis['critical_gaps'].append('هیچ مقاله ISI ندارید')
    elif len(isi_articles) < 2:
        analysis['important_gaps'].append('نیاز به حداقل 2 مقاله ISI')
    else:
        analysis['strengths'].append(f'{len(isi_articles)} مقاله ISI')
    
    if not presentations:
        analysis['important_gaps'].append('ارائه در کنگره ملی یا بین‌المللی')
    else:
        analysis['strengths'].append(f'{len(presentations)} ارائه')


def _analyze_40emtiaz(analysis, profile, articles, isi_articles, current_edu):
    """تحلیل برای 40 امتیازی"""
    
    gpa = float(current_edu.get('gpa') or 0)
    
    if gpa < 16:
        analysis['critical_gaps'].append(f'معدل {gpa} پایین است')
    elif gpa < 17:
        analysis['important_gaps'].append('بالا بردن معدل به 17+')
    else:
        analysis['strengths'].append(f'معدل خوب: {gpa}')
    
    if len(isi_articles) == 0:
        analysis['critical_gaps'].append('انتشار مقاله ISI')
    else:
        analysis['strengths'].append(f'{len(isi_articles)} مقاله ISI')


def _analyze_heyat_elmi(analysis, profile, articles, isi_articles, current_edu):
    """تحلیل برای هیات علمی"""
    
    degree = current_edu.get('degree', '')
    
    if degree != 'دکتری تخصصی':
        analysis['critical_gaps'].append('دکتری تخصصی الزامی است')
    else:
        analysis['strengths'].append('دکتری تخصصی دارید')
    
    if len(isi_articles) < 3:
        analysis['critical_gaps'].append(f'نیاز به {3 - len(isi_articles)} مقاله ISI بیشتر')
    else:
        analysis['strengths'].append(f'{len(isi_articles)} مقاله ISI')


def _analyze_research_position(analysis, profile, articles, isi_articles):
    """تحلیل برای ریسرچ پوزیشن"""
    
    english_level = profile.get('english_level', '')
    
    if not english_level or english_level in ['A1', 'A2']:
        analysis['critical_gaps'].append('سطح زبان انگلیسی بسیار پایین')
    elif english_level in ['B1']:
        analysis['important_gaps'].append('ارتقاء سطح زبان به B2+')
    else:
        analysis['strengths'].append(f'سطح زبان {english_level}')
    
    if len(isi_articles) == 0:
        analysis['critical_gaps'].append('نیاز به مقاله بین‌المللی')
    else:
        analysis['strengths'].append(f'{len(isi_articles)} مقاله بین‌المللی')
