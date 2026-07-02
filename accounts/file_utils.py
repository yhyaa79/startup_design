# accounts/file_utils.py

import logging

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = 15


class FileExtractionError(Exception):
    """
    خطا در استخراج متن از فایل آپلودشده.
    پیام این exception مستقیماً قابل نمایش به کاربر است (فارسی و قابل‌فهم).
    """
    pass


def extract_text_from_file(file) -> str:
    """
    استخراج متن از فایل آپلودشده (txt, pdf, docx, doc, rtf).

    در صورت هر گونه مشکل — فایل خراب، فرمت پشتیبانی‌نشده، فایل خالی،
    یا نبود متن قابل استخراج (مثلاً فایل کاملاً اسکن/تصویری) —
    یک FileExtractionError با پیام مناسب برای نمایش به کاربر صادر می‌شود.
    """
    if not file:
        raise FileExtractionError("فایلی ارسال نشده است.")

    name = (file.name or "").lower()

    if file.size == 0:
        raise FileExtractionError("فایل ارسالی خالی است.")

    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise FileExtractionError(f"حجم فایل بیشتر از {MAX_FILE_SIZE_MB} مگابایت مجاز است.")

    try:
        if name.endswith(".txt"):
            text = _extract_txt(file)
        elif name.endswith(".pdf"):
            text = _extract_pdf(file)
        elif name.endswith(".docx"):
            text = _extract_docx(file)
        elif name.endswith(".doc"):
            text = _extract_doc(file)
        elif name.endswith(".rtf"):
            text = _extract_rtf(file)
        else:
            raise FileExtractionError(
                f"فرمت فایل «{file.name}» پشتیبانی نمی‌شود. "
                "لطفاً فایل را با فرمت txt، pdf، docx یا doc آپلود کنید."
            )
    except FileExtractionError:
        raise
    except Exception:
        # هر خطای پیش‌بینی‌نشده دیگری (فایل خراب، encoding عجیب و ...)
        logger.exception("خطای غیرمنتظره هنگام استخراج متن از فایل: %s", file.name)
        raise FileExtractionError(
            "فایل ارسالی قابل باز شدن نیست یا خراب است. لطفاً فایل دیگری امتحان کنید."
        )

    text = (text or "").strip()
    if not text:
        raise FileExtractionError(
            "متنی در فایل ارسالی پیدا نشد. اگر فایل شما اسکن‌شده یا تصویری است، "
            "لطفاً نسخه متنی/قابل‌کپی آن را آپلود کنید یا متن را مستقیم در کادر بالا وارد کنید."
        )

    return text


def _extract_txt(file) -> str:
    raw = file.read()
    for encoding in ("utf-8", "utf-8-sig", "cp1256", "windows-1252"):
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    # آخرین راه‌حل: کاراکترهای ناسازگار را نادیده بگیر
    return raw.decode("utf-8", errors="ignore")


def _extract_pdf(file) -> str:
    try:
        import pdfplumber
    except ImportError:
        raise FileExtractionError(
            "پردازش فایل PDF در سرور فعال نیست. لطفاً با پشتیبانی تماس بگیرید "
            "(نیاز به نصب pdfplumber: pip install pdfplumber)."
        )

    text_parts = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                try:
                    page_text = page.extract_text() or ""
                except Exception:
                    # اگر یک صفحه مشکل داشت، بقیه صفحات را از دست ندهیم
                    page_text = ""
                text_parts.append(page_text)
    except Exception as e:
        logger.exception("خطا در باز کردن فایل PDF: %s", file.name)
        raise FileExtractionError(
            "فایل PDF قابل باز شدن نیست، خراب است یا رمزگذاری‌شده است."
        ) from e

    text = "\n".join(text_parts).strip()

    # اگر PDF کاملاً اسکن‌شده/تصویری بود و متنی استخراج نشد، تلاش برای OCR (اختیاری)
    if not text:
        text = _try_ocr_pdf(file)

    return text


def _try_ocr_pdf(file) -> str:
    """
    تلاش برای OCR روی PDF اسکن‌شده، فقط در صورتی که pdf2image و pytesseract
    روی سرور نصب باشند. در غیر این صورت رشته خالی برمی‌گرداند و کاربر پیام
    استاندارد «متنی پیدا نشد» را می‌بیند.

    برای فعال‌سازی این قابلیت روی سرور باید نصب شود:
        pip install pdf2image pytesseract
        apt-get install poppler-utils tesseract-ocr tesseract-ocr-fas
    """
    try:
        import pytesseract
        from pdf2image import convert_from_bytes
    except ImportError:
        return ""

    try:
        file.seek(0)
        images = convert_from_bytes(file.read())
        text_parts = [pytesseract.image_to_string(img, lang="fas+eng") for img in images]
        return "\n".join(text_parts).strip()
    except Exception:
        logger.exception("خطا در OCR فایل PDF: %s", file.name)
        return ""


def _extract_docx(file) -> str:
    try:
        import docx
    except ImportError:
        raise FileExtractionError(
            "پردازش فایل DOCX در سرور فعال نیست. لطفاً با پشتیبانی تماس بگیرید "
            "(نیاز به نصب python-docx: pip install python-docx)."
        )

    try:
        doc = docx.Document(file)
    except Exception as e:
        logger.exception("خطا در باز کردن فایل DOCX: %s", file.name)
        raise FileExtractionError(
            "فایل Word (.docx) قابل باز شدن نیست یا خراب است."
        ) from e

    parts = [p.text for p in doc.paragraphs if p.text]

    # استخراج متن جدول‌ها هم (رزومه‌ها معمولاً بخشی از اطلاعات را در جدول می‌گذارند)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text:
                    parts.append(cell.text)

    return "\n".join(parts)


def _extract_doc(file) -> str:
    """
    استخراج متن از فایل‌های doc قدیمی (فرمت باینری Word 97-2003).
    این فرمت پیچیده‌تر از docx است و نیاز به کتابخانه‌ی جداگانه (مثل textract) دارد.
    """
    try:
        import textract
    except ImportError:
        raise FileExtractionError(
            "فایل‌های doc (نسخه قدیمی Word) در حال حاضر پشتیبانی نمی‌شوند. "
            "لطفاً فایل را با فرمت docx یا pdf ذخیره و دوباره آپلود کنید."
        )

    try:
        raw_bytes = file.read()
        text_bytes = textract.process(raw_bytes, extension="doc")
        return text_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.exception("خطا در باز کردن فایل doc: %s", file.name)
        raise FileExtractionError(
            "فایل doc قابل باز شدن نیست یا خراب است. لطفاً فرمت docx یا pdf را امتحان کنید."
        ) from e


def _extract_rtf(file) -> str:
    try:
        from striprtf.striprtf import rtf_to_text
    except ImportError:
        raise FileExtractionError(
            "پردازش فایل RTF در سرور فعال نیست. لطفاً فایل را با فرمت txt یا docx ذخیره کنید "
            "(نیاز به نصب striprtf: pip install striprtf)."
        )

    try:
        raw = file.read().decode("utf-8", errors="ignore")
        return rtf_to_text(raw)
    except Exception as e:
        logger.exception("خطا در باز کردن فایل RTF: %s", file.name)
        raise FileExtractionError("فایل RTF قابل باز شدن نیست یا خراب است.") from e