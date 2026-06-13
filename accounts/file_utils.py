def extract_text_from_file(file) -> str:
    """استخراج متن از فایل آپلودشده (txt, pdf, docx)"""
    name = file.name.lower()

    if name.endswith('.txt'):
        return file.read().decode('utf-8', errors='ignore')

    if name.endswith('.pdf'):
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or '')
            return '\n'.join(text_parts)
        except ImportError:
            raise ImportError("برای پردازش PDF لطفاً پکیج pdfplumber را نصب کنید: pip install pdfplumber")

    if name.endswith('.docx'):
        try:
            import docx
            doc = docx.Document(file)
            return '\n'.join(p.text for p in doc.paragraphs)
        except ImportError:
            raise ImportError("برای پردازش DOCX لطفاً پکیج python-docx را نصب کنید: pip install python-docx")

    raise ValueError(f"فرمت فایل پشتیبانی نمی‌شود: {file.name}")
