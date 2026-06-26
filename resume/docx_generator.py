# resume/docx_generator.py

"""
Resume PDF Generator — 4 professional templates using ReportLab.
Supports RTL (Persian/Farsi) text via bidi + arabic_reshaper.
"""
import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER, TA_JUSTIFY

# ── Font registration ──────────────────────────────────────────────────────────
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')

def _register_fonts():
    """Register Persian-capable fonts. Falls back gracefully."""
    fonts_registered = False
    try:
        regular = os.path.join(FONT_DIR, 'Vazirmatn-Regular.ttf')
        bold = os.path.join(FONT_DIR, 'Vazirmatn-Bold.ttf')
        if os.path.exists(regular) and os.path.exists(bold):
            pdfmetrics.registerFont(TTFont('Vazir', regular))
            pdfmetrics.registerFont(TTFont('Vazir-Bold', bold))
            fonts_registered = True
    except Exception:
        pass

    if not fonts_registered:
        # Use built-in Helvetica as fallback (no Persian support but avoids crash)
        return 'Helvetica', 'Helvetica-Bold'
    return 'Vazir', 'Vazir-Bold'


FONT_REGULAR, FONT_BOLD = _register_fonts()


def _rtl(text: str) -> str:
    """Apply RTL reshaping if libraries are available."""
    if not text:
        return ''
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except ImportError:
        return str(text)


# ── Colour palettes per template ──────────────────────────────────────────────
PALETTES = {
    'classic': {
        'primary': colors.HexColor('#1a3a5c'),
        'secondary': colors.HexColor('#2e6da4'),
        'accent': colors.HexColor('#e8f0f7'),
        'text': colors.HexColor('#222222'),
        'light': colors.HexColor('#f5f8fb'),
        'hr': colors.HexColor('#2e6da4'),
    },
    'modern': {
        'primary': colors.HexColor('#1d2d44'),
        'secondary': colors.HexColor('#c1121f'),
        'accent': colors.HexColor('#f0f4f8'),
        'text': colors.HexColor('#1d2d44'),
        'light': colors.HexColor('#fafafa'),
        'hr': colors.HexColor('#c1121f'),
    },
    'academic': {
        'primary': colors.HexColor('#2d6a4f'),
        'secondary': colors.HexColor('#40916c'),
        'accent': colors.HexColor('#d8f3dc'),
        'text': colors.HexColor('#1b4332'),
        'light': colors.HexColor('#f0faf4'),
        'hr': colors.HexColor('#40916c'),
    },
    'minimal': {
        'primary': colors.HexColor('#222222'),
        'secondary': colors.HexColor('#555555'),
        'accent': colors.HexColor('#f0f0f0'),
        'text': colors.HexColor('#333333'),
        'light': colors.HexColor('#fafafa'),
        'hr': colors.HexColor('#aaaaaa'),
    },
}


# ── Style factory ─────────────────────────────────────────────────────────────
def _styles(palette):
    p = palette
    return {
        'name': ParagraphStyle('name', fontName=FONT_BOLD, fontSize=22,
                               textColor=p['primary'], alignment=TA_RIGHT,
                               spaceAfter=2),
        'subtitle': ParagraphStyle('subtitle', fontName=FONT_REGULAR, fontSize=10,
                                   textColor=p['secondary'], alignment=TA_RIGHT,
                                   spaceAfter=8),
        'contact': ParagraphStyle('contact', fontName=FONT_REGULAR, fontSize=8.5,
                                  textColor=p['secondary'], alignment=TA_RIGHT,
                                  spaceAfter=4),
        'section': ParagraphStyle('section', fontName=FONT_BOLD, fontSize=11,
                                  textColor=p['primary'], alignment=TA_RIGHT,
                                  spaceBefore=10, spaceAfter=4),
        'body': ParagraphStyle('body', fontName=FONT_REGULAR, fontSize=9,
                               textColor=p['text'], alignment=TA_RIGHT,
                               spaceAfter=3, leading=14),
        'body_bold': ParagraphStyle('body_bold', fontName=FONT_BOLD, fontSize=9,
                                    textColor=p['text'], alignment=TA_RIGHT,
                                    spaceAfter=2),
        'summary': ParagraphStyle('summary', fontName=FONT_REGULAR, fontSize=9,
                                  textColor=p['text'], alignment=TA_JUSTIFY,
                                  spaceAfter=6, leading=15),
        'tag': ParagraphStyle('tag', fontName=FONT_REGULAR, fontSize=8,
                              textColor=p['secondary'], alignment=TA_RIGHT),
    }


# ── Helper builders ───────────────────────────────────────────────────────────
def _hr(palette, width=None):
    return HRFlowable(
        width=width or '100%', thickness=1,
        color=palette['hr'], spaceAfter=4, spaceBefore=2
    )


def _section_header(title: str, st, palette):
    return KeepTogether([
        Paragraph(_rtl(title), st['section']),
        _hr(palette),
    ])


def _row(label: str, value: str, st):
    """Two-column label/value row — right-aligned."""
    if not value:
        return None
    data = [[Paragraph(_rtl(str(value)), st['body']),
             Paragraph(_rtl(str(label)), st['body_bold'])]]
    tbl = Table(data, colWidths=['75%', '25%'])
    tbl.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return tbl


def _chip_row(items: list, st, palette):
    """Comma-separated chips for skills / languages."""
    if not items:
        return None
    text = '  |  '.join([_rtl(i) for i in items if i])
    return Paragraph(text, st['tag'])


# ── Section builders ──────────────────────────────────────────────────────────
def _build_header(profile, resume, st, palette, story, page_width):
    """Name, title, contacts — varies slightly by template."""
    tmpl = resume.template

    name_text = _rtl(f'{profile.first_name} {profile.last_name}')
    story.append(Paragraph(name_text, st['name']))

    sub_parts = []
    if profile.job_title:
        sub_parts.append(_rtl(profile.job_title))
    if profile.specialty:
        sub_parts.append(_rtl(profile.specialty))
    if sub_parts:
        story.append(Paragraph('  ·  '.join(sub_parts), st['subtitle']))

    # Contact line
    contacts = []
    if profile.phone:
        contacts.append(profile.phone)
    if profile.email:
        contacts.append(profile.email)
    if profile.city:
        contacts.append(_rtl(profile.city))
    if profile.orcid:
        contacts.append(f'ORCID: {profile.orcid}')
    if contacts:
        story.append(Paragraph('  |  '.join(contacts), st['contact']))

    story.append(_hr(palette))


def _build_summary(profile, resume, st, palette, story):
    if resume.ai_enhanced and resume.ai_summary:
        story.append(_section_header('خلاصه حرفه‌ای', st, palette))
        story.append(Paragraph(_rtl(resume.ai_summary), st['summary']))
    elif profile.goal_notes:
        story.append(_section_header('خلاصه حرفه‌ای', st, palette))
        story.append(Paragraph(_rtl(profile.goal_notes), st['summary']))


def _build_education(profile, st, palette, story):
    educations = profile.educations.all()
    if not educations:
        return
    story.append(_section_header('سوابق تحصیلی', st, palette))
    for edu in educations:
        parts = []
        if edu.degree:
            parts.append(_rtl(edu.degree))
        if edu.field:
            parts.append(_rtl(edu.field))
        title = ' — '.join(parts)
        story.append(Paragraph(title, st['body_bold']))

        details = []
        if edu.university:
            details.append(_rtl(edu.university))
        if edu.uni_type:
            details.append(_rtl(edu.uni_type))
        if edu.start_date or edu.end_date:
            details.append(f"{edu.start_date or ''} تا {edu.end_date or 'اکنون'}")
        if edu.gpa:
            details.append(f"معدل: {edu.gpa}")
        if edu.stage:
            details.append(_rtl(f"مرحله: {edu.stage}"))
        if details:
            story.append(Paragraph('  |  '.join(details), st['body']))
        story.append(Spacer(1, 3))


def _build_articles(profile, st, palette, story):
    articles = profile.articles.all()
    if not articles:
        return
    story.append(_section_header('مقالات پژوهشی', st, palette))
    for i, art in enumerate(articles, 1):
        title = _rtl(art.title) if art.title else f'مقاله {i}'
        story.append(Paragraph(f'{i}. {title}', st['body_bold']))
        meta = []
        if art.journal:
            meta.append(_rtl(art.journal))
        if art.quartile:
            meta.append(art.quartile)
        if art.impact_factor:
            meta.append(f'IF: {art.impact_factor}')
        if art.year:
            meta.append(str(art.year))
        if art.author_rank and art.total_authors:
            meta.append(f'نویسنده {art.author_rank} از {art.total_authors}')
        if art.index:
            meta.append(_rtl(art.index))
        if meta:
            story.append(Paragraph('  |  '.join(meta), st['body']))
        story.append(Spacer(1, 2))


def _build_presentations(profile, st, palette, story):
    items = profile.presentations.all()
    if not items:
        return
    story.append(_section_header('ارائه در کنگره', st, palette))
    for i, p in enumerate(items, 1):
        title = _rtl(p.title) if p.title else f'ارائه {i}'
        story.append(Paragraph(f'{i}. {title}', st['body_bold']))
        meta = []
        if p.event:
            meta.append(_rtl(p.event))
        if p.level:
            meta.append(_rtl(p.level))
        if p.result:
            meta.append(_rtl(p.result))
        if meta:
            story.append(Paragraph('  |  '.join(meta), st['body']))
        story.append(Spacer(1, 2))


def _build_executive(profile, st, palette, story):
    items = profile.executive_records.all()
    if not items:
        return
    story.append(_section_header('سوابق اجرایی', st, palette))
    for item in items:
        story.append(Paragraph(_rtl(item.title), st['body_bold']))
        if item.start_date or item.end_date:
            story.append(Paragraph(
                f"{item.start_date or ''} تا {item.end_date or 'اکنون'}", st['body']
            ))
        story.append(Spacer(1, 2))


def _build_training(profile, st, palette, story):
    items = profile.training_courses.all()
    if not items:
        return
    story.append(_section_header('دوره‌های آموزشی', st, palette))
    for item in items:
        story.append(Paragraph(_rtl(item.title), st['body_bold']))
        meta = []
        if item.category:
            meta.append(_rtl(item.category))
        if item.organizer:
            meta.append(_rtl(item.organizer))
        if item.date:
            meta.append(item.date)
        if item.certificate:
            meta.append(_rtl(f'گواهی: {item.certificate}'))
        if meta:
            story.append(Paragraph('  |  '.join(meta), st['body']))
        story.append(Spacer(1, 2))


def _build_clinical(profile, st, palette, story):
    if not (profile.clinical_exp or profile.clinical_certs or profile.procedures):
        return
    story.append(_section_header('سوابق بالینی', st, palette))
    if profile.clinical_exp:
        story.append(Paragraph(_rtl('سوابق کار بالینی:'), st['body_bold']))
        story.append(Paragraph(_rtl(profile.clinical_exp), st['body']))
    if profile.clinical_certs:
        story.append(Paragraph(_rtl('گواهینامه‌های مهارتی:'), st['body_bold']))
        story.append(Paragraph(_rtl(profile.clinical_certs), st['body']))
    if profile.procedures:
        story.append(Paragraph(_rtl('مهارت‌های پروسیجرال:'), st['body_bold']))
        story.append(Paragraph(_rtl(profile.procedures), st['body']))


def _build_languages(profile, st, palette, story):
    has_lang = profile.native_lang or profile.english_level or profile.lang_cert or profile.other_langs
    if not has_lang:
        return
    story.append(_section_header('زبان‌ها', st, palette))
    if profile.native_lang:
        story.append(_row('زبان مادری', profile.native_lang, st))
    if profile.english_level:
        cert_txt = f"{profile.english_level}" + (f"  ({profile.lang_cert})" if profile.lang_cert else '')
        story.append(_row('انگلیسی', cert_txt, st))
    if profile.other_langs:
        story.append(_row('سایر زبان‌ها', profile.other_langs, st))


def _build_skills(profile, st, palette, story):
    if not (profile.software_skills or profile.writing_skills):
        return
    story.append(_section_header('مهارت‌ها', st, palette))
    if profile.software_skills:
        story.append(Paragraph(_rtl('مهارت‌های نرم‌افزاری:'), st['body_bold']))
        story.append(Paragraph(_rtl(profile.software_skills), st['body']))
    if profile.writing_skills:
        story.append(Paragraph(_rtl('مهارت‌های نگارشی:'), st['body_bold']))
        story.append(Paragraph(_rtl(profile.writing_skills), st['body']))


def _build_extracurricular(profile, st, palette, story):
    if not profile.extracurricular:
        return
    story.append(_section_header('فعالیت‌های فوق برنامه', st, palette))
    story.append(Paragraph(_rtl(profile.extracurricular), st['body']))


# ── Main generator ────────────────────────────────────────────────────────────
def generate_docx(profile, resume) -> bytes:
    """
    Build a PDF resume and return its bytes.
    template choices: classic | modern | academic | minimal
    """
    buf = io.BytesIO()
    palette = PALETTES.get(resume.template, PALETTES['classic'])
    st = _styles(palette)

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    page_width = A4[0] - 3.6 * cm
    story = []

    _build_header(profile, resume, st, palette, story, page_width)
    _build_summary(profile, resume, st, palette, story)

    if resume.include_education:
        _build_education(profile, st, palette, story)
    if resume.include_articles:
        _build_articles(profile, st, palette, story)
    if resume.include_presentations:
        _build_presentations(profile, st, palette, story)
    if resume.include_executive:
        _build_executive(profile, st, palette, story)
    if resume.include_training:
        _build_training(profile, st, palette, story)
    if resume.include_clinical:
        _build_clinical(profile, st, palette, story)
    if resume.include_languages:
        _build_languages(profile, st, palette, story)
    if resume.include_skills:
        _build_skills(profile, st, palette, story)
    if resume.include_extracurricular:
        _build_extracurricular(profile, st, palette, story)

    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(FONT_REGULAR, 7)
        canvas.setFillColor(palette['secondary'])
        canvas.drawRightString(
            A4[0] - 1.8 * cm,
            0.8 * cm,
            f'صفحه {doc.page}'
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()