# accounts/ai_utils.py

import json
import re
import time
import logging
import requests
from django.conf import settings
from .models import Profile

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# تنظیمات
# ═══════════════════════════════════════════════════════════════

DEFAULT_TIMEOUT = getattr(settings, "GAPGPT_TIMEOUT", 60)   # read timeout
CONNECT_TIMEOUT = 10                                          # connect timeout
MAX_RETRIES = 2                                                # تلاش مجدد برای خطاهای شبکه/۵xx روی هر مدل

# مدل اصلی و مدل قوی‌تر (fallback) برای زمانی که خروجی مدل اول نامعتبر/ناقص باشد.
# GAPGPT_MODEL_NAME_2 را در settings.py تعریف کنید؛ اگر تعریف نشود همان مدل اول استفاده می‌شود.
MODEL_PRIMARY = settings.GAPGPT_MODEL_NAME
MODEL_FALLBACK = getattr(settings, "GAPGPT_MODEL_NAME_2", None) or MODEL_PRIMARY


class AIExtractionError(Exception):
    """
    خطای مربوط به استخراج اطلاعات توسط هوش مصنوعی.
    پیام این exception مستقیماً قابل نمایش به کاربر است (فارسی و قابل‌فهم).
    """
    pass


REQUIRED_PROFILE_FIELDS = ["first_name", "last_name", "gender", "goal"]

LIST_FIELDS = [
    "social_profiles", "educations", "articles",
    "presentations", "executive_records", "training_courses",
]


# ═══════════════════════════════════════════════════════════════
# تابع کمکی برای ارتباط با API
# ═══════════════════════════════════════════════════════════════

def _call_gpt_api(messages: list, model: str, max_tokens: int = 4000) -> str:
    """
    فراخوانی GapGPT Chat Completion API با retry و مدیریت خطا.
    در صورت هر گونه خطا، AIExtractionError با پیام قابل‌نمایش به کاربر صادر می‌شود.
    """
    if not getattr(settings, "GAPGPT_API_KEY", None) or settings.GAPGPT_API_KEY == "YOUR_API_KEY_HERE":
        logger.error("GAPGPT_API_KEY is not configured.")
        raise AIExtractionError("کلید API سرویس هوش مصنوعی تنظیم نشده است.")

    url = f"{settings.GAPGPT_API_BASE}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GAPGPT_API_KEY}",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
        # اجبار مدل به خروجی خالص JSON (اگر مدل پشتیبانی نکند، خودکار حذف و دوباره تلاش می‌شود)
        "response_format": {"type": "json_object"},
    }

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Calling GPT API model=%s (attempt %s/%s)", model, attempt, MAX_RETRIES)
            start_time = time.monotonic()

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=(CONNECT_TIMEOUT, DEFAULT_TIMEOUT),
            )

            elapsed = time.monotonic() - start_time
            logger.info("GPT API (%s) responded in %.2fs -> status %s", model, elapsed, response.status_code)

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]

            # اگر مدل پارامتر response_format را پشتیبانی نکند (خطای ۴۰۰ رایج)، بدون آن دوباره تلاش کن
            if response.status_code == 400 and "response_format" in payload:
                logger.warning("response_format may not be supported by model=%s; retrying without it.", model)
                payload.pop("response_format", None)
                continue

            # خطاهای موقت سرویس → retry با backoff
            if response.status_code in (429, 502, 503, 504):
                logger.warning("Upstream error %s on attempt %s (model=%s)", response.status_code, attempt, model)
                last_error = AIExtractionError(
                    "سرویس هوش مصنوعی موقتاً در دسترس نیست یا شلوغ است. لطفاً چند دقیقه بعد دوباره تلاش کنید."
                )
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt)
                    continue
                raise last_error

            # سایر خطاهای HTTP
            logger.error("HTTP error %s from GPT API (%s): %s", response.status_code, model, response.text[:500])
            raise AIExtractionError(f"خطای سرویس هوش مصنوعی (کد {response.status_code}).")

        except requests.exceptions.ReadTimeout:
            logger.warning("Read timeout on attempt %s (model=%s)", attempt, model)
            last_error = AIExtractionError("سرویس هوش مصنوعی دیر پاسخ داد. لطفاً دوباره تلاش کنید.")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue
            raise last_error

        except requests.exceptions.ConnectionError:
            logger.exception("Connection error while calling GPT API (model=%s).", model)
            raise AIExtractionError("خطا در اتصال به سرویس هوش مصنوعی. اتصال اینترنت سرور را بررسی کنید.")

        except (KeyError, IndexError, json.JSONDecodeError):
            logger.exception("Invalid API response structure (model=%s).", model)
            raise AIExtractionError("پاسخ دریافتی از سرویس هوش مصنوعی نامعتبر است.")

        except AIExtractionError:
            raise

        except Exception:
            logger.exception("Unexpected error in _call_gpt_api (model=%s).", model)
            raise AIExtractionError("خطای غیرمنتظره در ارتباط با سرویس هوش مصنوعی.")

    if last_error:
        raise last_error
    raise AIExtractionError("خطای نامشخص در ارتباط با سرویس هوش مصنوعی.")


# ═══════════════════════════════════════════════════════════════
# Parse و اعتبارسنجی خروجی JSON
# ═══════════════════════════════════════════════════════════════

def _parse_json_response(response_text: str) -> dict:
    """
    استخراج و parse کردن JSON از پاسخ مدل، حتی اگر مدل متن اضافه دور آن
    گذاشته باشد یا داخل بلوک کد markdown برگردانده باشد.
    """
    text = (response_text or "").strip()
    if not text:
        raise AIExtractionError("پاسخ خالی از سرویس هوش مصنوعی دریافت شد.")

    # حذف بلوک‌های کد ```json ... ``` یا ``` ... ```
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if code_block:
        text = code_block.group(1).strip()

    # تلاش مستقیم
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # فقط بخش بین اولین { و آخرین } را نگه دار (برای حذف توضیحات اضافه مدل)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # حذف کاماهای اضافه قبل از } یا ] که باعث خطای رایج JSON می‌شود
            fixed = re.sub(r",\s*([}\]])", r"\1", candidate)
            try:
                return json.loads(fixed)
            except json.JSONDecodeError as e:
                logger.warning("Could not parse JSON from AI response: %s", text[:300])
                raise AIExtractionError("پاسخ مدل هوش مصنوعی به فرمت JSON معتبر نبود.") from e

    logger.warning("No JSON object found in AI response: %s", text[:300])
    raise AIExtractionError("پاسخ مدل هوش مصنوعی به فرمت JSON معتبر نبود.")


def _validate_extracted_data(data) -> None:
    """
    بررسی می‌کند خروجی مدل حداقل ساختار موردنیاز را دارد.
    اگر معتبر نبود، AIExtractionError صادر می‌شود تا caller با مدل قوی‌تر دوباره تلاش کند.
    """
    if not isinstance(data, dict):
        raise AIExtractionError("ساختار خروجی هوش مصنوعی نامعتبر است.")

    profile = data.get("profile")
    if not isinstance(profile, dict):
        raise AIExtractionError("بخش «profile» در خروجی هوش مصنوعی یافت نشد.")

    missing = [f for f in REQUIRED_PROFILE_FIELDS if not str(profile.get(f, "")).strip()]
    if missing:
        raise AIExtractionError(
            "برخی اطلاعات ضروری (نام، نام‌خانوادگی، جنسیت یا هدف) در متن یافت نشد."
        )

    for key in LIST_FIELDS:
        if key in data and data[key] is not None and not isinstance(data[key], list):
            raise AIExtractionError(f"بخش «{key}» در خروجی هوش مصنوعی باید لیست باشد.")


# ═══════════════════════════════════════════════════════════════
# ساخت پرامپت‌ها
# ═══════════════════════════════════════════════════════════════

def _build_messages(text: str) -> list:
    system_prompt = """تو یک دستیار هوشمند برای استخراج اطلاعات از متن‌های فارسی هستی.
وظیفه‌ات این است که متن زیر را بخوانی و اطلاعات موجود در آن را به صورت ساختاریافته استخراج کنی.

قوانین مهم:
1. فقط اطلاعاتی را استخراج کن که صراحتاً در متن ذکر شده‌اند.
2. اگر اطلاعاتی وجود ندارد، آن فیلد را خالی ("") یا null بگذار.
3. تاریخ‌ها را به صورت جلالی بنویس (مثال: ۱۴۰۲/۰۳/۱۵).
4. اعداد را به صورت انگلیسی بنویس (مثال: 1402 نه ۱۴۰۲).
5. فقط و فقط یک شیء JSON خالص برگردان، بدون هیچ توضیح اضافی، بدون بلوک کد markdown.
6. حتماً کلیدهای "profile"، "social_profiles"، "educations"، "articles"، "presentations"،
   "executive_records" و "training_courses" را در خروجی بگنجان (لیست‌های خالی [] اگر موردی نبود).
7. فیلدهای الزامی profile عبارت‌اند از: first_name، last_name، gender، goal — این‌ها را
   حتماً از روی بهترین برداشت خودت از متن پر کن و خالی نگذار."""

    user_prompt = f"""لطفاً اطلاعات زیر را از متن استخراج کن و فقط یک شیء JSON با دقیقاً این ساختار برگردان:

متن ورودی:
{text}

ساختار خروجی مورد انتظار:
{{
  "profile": {{
    "first_name": "نام",
    "last_name": "نام خانوادگی",
    "gender": "مرد یا زن",
    "marital_status": "مجرد یا متأهل یا خالی",
    "military_status": "معاف یا طرح پزشکی یا سرباز یا پایان خدمت یا خالی",
    "job_title": "عنوان شغلی",
    "birth_date": "تاریخ تولد جلالی",
    "country": "کشور",
    "city": "شهر",
    "phone": "شماره تلفن",
    "email": "ایمیل",
    "website": "وب‌سایت",
    "national_id": "کد ملی",
    "orcid": "شناسه ORCID",
    "proposal_count": عدد یا null,
    "proposal_status": "همه در جریان یا همه خاتمه‌یافته یا ترکیبی یا خالی",
    "software_skills": "مهارت‌های نرم‌افزاری",
    "writing_skills": "مهارت‌های نگارشی",
    "clinical_certs": "گواهینامه‌های بالینی",
    "clinical_exp": "سوابق بالینی",
    "procedures": "مهارت‌های پروسیجرال",
    "native_lang": "زبان مادری",
    "english_level": "A1 یا A2 یا B1 یا B2 یا C1 یا C2 یا خالی",
    "lang_cert": "مدرک زبان",
    "other_langs": "سایر زبان‌ها",
    "extracurricular": "فعالیت‌های فوق برنامه",
    "goal": "استعداد درخشان یا ۴۰ امتیازی یا هیات علمی یا ریسرچ پوزیشن / فلوشیپ خارج",
    "specialty": "حوزه تخصصی",
    "goal_notes": "توضیحات اهداف",
    "service_plan": "مشمول نیستم یا در حال گذراندن یا پایان یافته یا خالی"
  }},
  "social_profiles": [
    {{"social_type": "LinkedIn یا GitHub یا Google Scholar یا ResearchGate یا Dribbble یا Twitter / X یا Instagram یا سایر", "url": "لینک"}}
  ],
  "educations": [
    {{"field": "پزشکی یا دندان‌پزشکی یا داروسازی یا پرستاری یا فیزیوتراپی یا سایر", "degree": "کارشناسی یا کارشناسی ارشد یا دکتری عمومی یا دکتری تخصصی", "university": "نام دانشگاه", "uni_type": "تیپ ۱ یا تیپ ۲ یا تیپ ۳ یا خالی", "start_date": "تاریخ شروع جلالی", "end_date": "تاریخ پایان جلالی", "stage": "علوم پایه یا فیزیوپات یا استاژری یا اینترنی یا فارغ‌التحصیل یا خالی", "current_term": عدد یا null, "remaining_terms": عدد یا null, "gpa": عدد یا null}}
  ],
  "articles": [
    {{"title": "عنوان مقاله", "journal": "نام ژورنال", "impact_factor": عدد یا null, "quartile": "Q1 یا Q2 یا Q3 یا Q4 یا خالی", "year": عدد یا null, "author_rank": عدد یا null, "total_authors": عدد یا null, "index": "ISI / Web of Science یا Scopus یا PubMed یا ISI + Scopus یا سایر یا خالی"}}
  ],
  "presentations": [
    {{"title": "عنوان ارائه", "event": "نام رویداد", "level": "بین‌المللی یا ملی یا قطبی یا دانشگاهی یا خالی", "result": "برگزیده / جایزه یا ارائه عادی یا خالی"}}
  ],
  "executive_records": [
    {{"title": "عنوان سمت", "start_date": "تاریخ شروع جلالی", "end_date": "تاریخ پایان جلالی"}}
  ],
  "training_courses": [
    {{"title": "عنوان دوره", "category": "پژوهشی یا بالینی یا آموزشی یا نرم‌افزاری یا زبان یا سایر یا خالی", "status": "تکمیل‌شده یا در حال گذراندن یا ناتمام یا خالی", "organizer": "برگزارکننده", "date": "تاریخ جلالی", "certificate": "دارد یا ندارد یا خالی", "skills_gained": "مهارت‌های کسب‌شده"}}
  ]
}}"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


# ═══════════════════════════════════════════════════════════════
# تابع اصلی: استخراج پروفایل از متن (با retry روی مدل قوی‌تر)
# ═══════════════════════════════════════════════════════════════

def extract_profile_from_text(text: str) -> dict:
    """
    استخراج داده‌های ساختاریافته پروفایل از متن خام فارسی با استفاده از LLM.

    ابتدا با مدل اصلی (GAPGPT_MODEL_NAME) تلاش می‌شود. اگر پاسخ:
      - قابل parse به JSON نبود، یا
      - ساختار/فیلدهای ضروری‌اش ناقص بود،
    آنگاه یک‌بار دیگر با مدل قوی‌تر (GAPGPT_MODEL_NAME_2) تلاش می‌شود.

    اگر هر دو تلاش شکست بخورد، AIExtractionError با پیام قابل‌نمایش به کاربر صادر می‌شود.
    """
    if not text or not text.strip():
        raise AIExtractionError("متنی برای استخراج وجود ندارد.")

    messages = _build_messages(text)

    models_to_try = [MODEL_PRIMARY]
    if MODEL_FALLBACK and MODEL_FALLBACK != MODEL_PRIMARY:
        models_to_try.append(MODEL_FALLBACK)

    last_error = None
    for model in models_to_try:
        try:
            response_text = _call_gpt_api(messages, model=model, max_tokens=4000)
            result = _parse_json_response(response_text)
            _validate_extracted_data(result)
            return result
        except AIExtractionError as e:
            logger.warning("Extraction attempt failed with model=%s: %s", model, e)
            last_error = e
            continue

    raise last_error or AIExtractionError("استخراج اطلاعات با هوش مصنوعی ناموفق بود.")


# ═══════════════════════════════════════════════════════════════
# پاکسازی داده قبل از ذخیره در دیتابیس
# ═══════════════════════════════════════════════════════════════

def _sanitize_profile_data(data: dict) -> dict:
    """
    تبدیل مقادیر خروجی AI به مقادیر امن و سازگار با مدل Profile:
    - None بر اساس نوع فیلد به '' یا None تبدیل می‌شود.
    - فیلدهای ناشناخته (که در مدل وجود ندارند) حذف می‌شوند تا خطای غیرمنتظره ندهند.
    - مقادیر list/dict که مدل انتظارش را ندارد به رشته JSON تبدیل می‌شوند.
    """
    numeric_null_fields = {"proposal_count"}

    valid_fields = {f.name for f in Profile._meta.get_fields() if hasattr(f, "attname")}

    cleaned = {}
    for key, value in data.items():
        if key not in valid_fields:
            logger.debug("Ignoring unknown profile field from AI output: %s", key)
            continue

        if value is None:
            cleaned[key] = None if key in numeric_null_fields else ""
        elif isinstance(value, (list, dict)):
            cleaned[key] = json.dumps(value, ensure_ascii=False)
        else:
            cleaned[key] = value

    return cleaned