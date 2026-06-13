# roadmap/management/commands/populate_activities.py

from django.core.management.base import BaseCommand
from roadmap.models import Activity


""" 
هر وار تغییر در این بخش باید کد زیر در ترمینال اجرا بشه
python manage.py populate_activities
"""

class Command(BaseCommand):
    help = 'پر کردن پایگاه داده با فعالیت‌های پیش‌فرض'

    def handle(self, *args, **options):
        activities_data = [
            # پژوهشی - دوره ها
            {
                'title': 'شرکت در کارگاه مقاله‌نویسی علمی',
                'description': 'در این کارگاه با اصول نگارش مقاله علمی، ساختار بخش‌های مختلف مقاله و نکات مهم برای آماده‌سازی متن پژوهشی قابل ارسال به ژورنال آشنا می‌شوید.',
                'category': 'پژوهشی',
                'resume_output': 'تقویت مقاله‌نویسی علمی',
                'duration_days': 90,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "کارگاه مقاله‌نویسی علمی",
                        "category": "پژوهشی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "نگارش مقاله علمی، ساختار مقاله، اصول رفرنس‌دهی"
                    },
                },
            },
            {
                'title': 'شرکت در کارگاه پروپوزال‌نویسی',
                'description': 'این کارگاه به شما کمک می‌کند ایده پژوهشی خود را به یک پروپوزال منظم تبدیل کنید و با نحوه تدوین سوال پژوهش، اهداف، روش اجرا و اهمیت مطالعه آشنا شوید.',
                'category': 'پژوهشی',
                'resume_output': 'یادگیری پروپوزال‌نویسی',
                'duration_days': 90,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "کارگاه پروپوزال‌نویسی",
                        "category": "پژوهشی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "پروپوزال‌نویسی، طراحی سوال پژوهش، تعیین اهداف مطالعه"
                    },
                },
            },
            {
                'title': 'شرکت در دوره جستجوی منابع و سرچ حرفه‌ای',
                'description': 'در این دوره روش‌های جستجوی حرفه‌ای منابع علمی در پایگاه‌هایی مانند PubMed و Scopus آموزش داده می‌شود تا بتوانید منابع معتبر و مرتبط را سریع‌تر پیدا کنید.',
                'category': 'پژوهشی',
                'resume_output': 'مهارت جستجوی منابع',
                'duration_days': 60,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره جستجوی منابع و سرچ حرفه‌ای",
                        "category": "پژوهشی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "جستجوی PubMed و Scopus، طراحی استراتژی سرچ، فیلتر مقالات"
                    },
                },
            },
            {
                'title': 'شرکت در دوره اصول ریویو سیستماتیک',
                'description': 'این دوره مبانی مرور نظام‌مند را آموزش می‌دهد و شما را با مراحل طراحی سوال پژوهش، جستجوی منابع، غربالگری مطالعات و استخراج داده آشنا می‌کند.',
                'category': 'پژوهشی',
                'resume_output': 'آشنایی با ریویو سیستماتیک',
                'duration_days': 120,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره اصول ریویو سیستماتیک",
                        "category": "پژوهشی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "مرور نظام‌مند، غربالگری مطالعات، استخراج داده"
                    },
                },
            },
            {
                'title': 'شرکت در دوره آشنایی با اصول متاآنالیز',
                'description': 'در این دوره با مفاهیم پایه متاآنالیز، ترکیب نتایج مطالعات، تفسیر نمودارهای آماری و ارزیابی ناهمگنی بین مطالعات آشنا می‌شوید.',
                'category': 'پژوهشی',
                'resume_output': 'درک مبانی متاآنالیز',
                'duration_days': 120,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره آشنایی با اصول متاآنالیز",
                        "category": "پژوهشی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "مفاهیم متاآنالیز، تفسیر forest plot، ارزیابی ناهمگنی"
                    },
                },
            },

            # نرم افزاری
            {
                'title': 'شرکت در دوره SPSS',
                'description': 'این دوره برای یادگیری تحلیل آماری با نرم‌افزار SPSS طراحی شده و شامل ورود داده، اجرای آزمون‌های پایه، تحلیل نتایج و تهیه خروجی قابل استفاده در پژوهش است.',
                'category': 'نرم‌افزاری',
                'resume_output': 'یادگیری تحلیل آماری',
                'duration_days': 90,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره SPSS",
                        "category": "نرم‌افزاری",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "تحلیل آماری، آزمون‌های پایه، ترسیم نمودار"
                    },
                },
            },
            {
                'title': 'شرکت در دوره Excel برای پژوهش',
                'description': 'در این دوره با کاربردهای Excel در مدیریت داده‌های پژوهشی، پاک‌سازی اطلاعات، فرمول‌نویسی و آماده‌سازی دیتاست برای تحلیل آشنا می‌شوید.',
                'category': 'نرم‌افزاری',
                'resume_output': 'مدیریت داده پژوهشی',
                'duration_days': 45,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره Excel برای پژوهش",
                        "category": "نرم‌افزاری",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "مدیریت داده، فرمول‌نویسی، آماده‌سازی دیتاست"
                    },
                },
            },
            {
                'title': 'شرکت در دوره EndNote',
                'description': 'این دوره نحوه مدیریت منابع علمی با EndNote را آموزش می‌دهد و به شما کمک می‌کند کتابخانه منابع بسازید، ارجاعات را سازمان‌دهی کنید و رفرنس‌دهی را ساده‌تر انجام دهید.',
                'category': 'نرم‌افزاری',
                'resume_output': 'مدیریت منابع علمی',
                'duration_days': 30,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره EndNote",
                        "category": "نرم‌افزاری",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "مدیریت منابع، رفرنس‌دهی خودکار، ساخت کتابخانه مقالات"
                    },
                },
            },
            {
                'title': 'شرکت در دوره مقدماتی Python برای پژوهش',
                'description': 'در این دوره با مفاهیم ابتدایی برنامه‌نویسی Python و کاربرد آن در پژوهش، از جمله آماده‌سازی داده، تحلیل مقدماتی و کار با کتابخانه pandas آشنا می‌شوید.',
                'category': 'نرم‌افزاری',
                'resume_output': 'برنامه‌نویسی برای پژوهش',
                'duration_days': 120,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره مقدماتی Python برای پژوهش",
                        "category": "نرم‌افزاری",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "تحلیل داده مقدماتی، کار با pandas، آماده‌سازی داده"
                    },
                },
            },

            # آموزشي و زبان
            {
                'title': 'شرکت در دوره فن بیان و ارائه علمی',
                'description': 'این دوره با هدف تقویت مهارت ارائه علمی برگزار می‌شود و شامل اصول سخنرانی، طراحی اسلاید، مدیریت زمان و انتقال موثر مفاهیم به مخاطب است.',
                'category': 'آموزشی',
                'resume_output': 'تقویت ارائه علمی',
                'duration_days': 45,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره فن بیان و ارائه علمی",
                        "category": "آموزشی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "ارائه علمی، طراحی اسلاید، فن بیان"
                    },
                },
            },
            {
                'title': 'شرکت در دوره آموزش رزومه‌نویسی حرفه‌ای',
                'description': 'در این دوره یاد می‌گیرید چگونه سوابق آموزشی، پژوهشی و مهارتی خود را به شکل حرفه‌ای در رزومه تنظیم کنید و دستاوردهای خود را بهتر نمایش دهید.',
                'category': 'آموزشی',
                'resume_output': 'بهبود رزومه حرفه‌ای',
                'duration_days': 30,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره آموزش رزومه‌نویسی حرفه‌ای",
                        "category": "آموزشی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "رزومه‌نویسی، پروفایل‌سازی، معرفی دستاوردها"
                    },
                },
            },
            {
                'title': 'شرکت در دوره زبان انگلیسی پزشکی',
                'description': 'این دوره برای تقویت زبان تخصصی پزشکی طراحی شده و به درک بهتر متون علمی، یادگیری واژگان تخصصی و بهبود مکاتبات علمی کمک می‌کند.',
                'category': 'زبان',
                'resume_output': 'تقویت زبان پزشکی',
                'duration_days': 180,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره زبان انگلیسی پزشکی",
                        "category": "زبان",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "درک متون پزشکی، واژگان تخصصی، مکاتبه علمی"
                    },
                },
            },
            {
                'title': 'شرکت در دوره آمادگی IELTS',
                'description': 'در این دوره مهارت‌های اصلی آزمون IELTS شامل شنیدن، خواندن، نوشتن و صحبت کردن تمرین می‌شود و تمرکز ویژه‌ای بر رایتینگ آکادمیک و اسپیکینگ دارد.',
                'category': 'زبان',
                'resume_output': 'آمادگی آزمون آیلتس',
                'duration_days': 180,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره آمادگی IELTS",
                        "category": "زبان",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "مهارت‌های چهارگانه زبان، رایتینگ آکادمیک، اسپیکینگ"
                    },
                },
            },

            # باليني
            {
                'title': 'شرکت در دوره BLS',
                'description': 'این دوره مهارت‌های احیای پایه را آموزش می‌دهد و شامل ارزیابی اولیه بیمار، انجام CPR، کمک‌های اولیه اورژانسی و اقدامات ضروری در شرایط بحرانی است.',
                'category': 'بالینی',
                'resume_output': 'مهارت احیای پایه',
                'duration_days': 7,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره BLS",
                        "category": "بالینی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "احیای پایه، ارزیابی بیمار، اقدامات اولیه اورژانسی"
                    },
                },
            },
            {
                'title': 'شرکت در دوره ACLS',
                'description': 'در این دوره مهارت‌های احیای پیشرفته قلبی عروقی، تفسیر ریتم‌های مهم، مدیریت راه هوایی و تصمیم‌گیری در شرایط اورژانس آموزش داده می‌شود.',
                'category': 'بالینی',
                'resume_output': 'مهارت احیای پیشرفته',
                'duration_days': 14,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره ACLS",
                        "category": "بالینی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "احیای پیشرفته، تفسیر ریتم، مدیریت راه هوایی"
                    },
                },
            },
            {
                'title': 'شرکت در دوره تفسیر ECG',
                'description': 'این دوره به آموزش اصول خواندن نوار قلب، تشخیص ریتم‌های شایع، شناسایی آریتمی‌ها و تحلیل یافته‌های مهم قلبی در محیط بالینی می‌پردازد.',
                'category': 'بالینی',
                'resume_output': 'تسلط بر تفسیر ECG',
                'duration_days': 30,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره تفسیر ECG",
                        "category": "بالینی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "تفسیر نوار قلب، تشخیص آریتمی، تحلیل یافته‌های قلبی"
                    },
                },
            },
            {
                'title': 'شرکت در دوره مهارت‌های اورژانس',
                'description': 'در این دوره مهارت‌های کاربردی مدیریت بیمار اورژانسی، تریاژ، ارزیابی اولیه و انجام اقدامات ضروری برای بیماران بدحال آموزش داده می‌شود.',
                'category': 'بالینی',
                'resume_output': 'مدیریت اورژانس بالینی',
                'duration_days': 30,
                'resume_target': 'training_course',
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "دوره مهارت‌های اورژانس",
                        "category": "بالینی",
                        "status": "تکمیل‌شده",
                        "organizer": "Roadmap",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "تریاژ، مدیریت اولیه بیمار بدحال، اقدامات اورژانسی"
                    },
                },
            },

            # مقاله
            {
                'title': 'ثبت مقاله چاپ‌شده داخلی',
                'description': 'این فعالیت برای ثبت یک مقاله پژوهشی چاپ‌شده در ژورنال داخلی استفاده می‌شود و نشان‌دهنده مشارکت در تولید محتوای علمی و انتشار نتایج پژوهش است.',
                'category': 'پژوهشی',
                'resume_output': 'ثبت مقاله داخلی',
                'duration_days': 180,
                'resume_target': 'article',
                'profile_template': {
                    "model": "articles",
                    "data": {
                        "title": "مقاله پژوهشی چاپ‌شده در ژورنال داخلی",
                        "journal": "مجله علمی پژوهشی دانشگاهی",
                        "impact_factor": None,
                        "quartile": "",
                        "year": 1403,
                        "author_rank": 1,
                        "total_authors": 4,
                        "index": "سایر"
                    },
                },
            },
            {
                'title': 'ثبت مقاله اسکوپوس',
                'description': 'این فعالیت مربوط به ثبت مقاله چاپ‌شده در مجله نمایه‌شده در Scopus است و می‌تواند جایگاه پژوهشی فرد را در رزومه علمی تقویت کند.',
                'category': 'پژوهشی',
                'resume_output': 'ثبت مقاله اسکوپوس',
                'duration_days': 240,
                'resume_target': 'article',
                'profile_template': {
                    "model": "articles",
                    "data": {
                        "title": "مقاله چاپ‌شده در مجله نمایه‌شده در Scopus",
                        "journal": "Scopus Indexed Journal",
                        "impact_factor": 2.5,
                        "quartile": "Q3",
                        "year": 1403,
                        "author_rank": 2,
                        "total_authors": 5,
                        "index": "Scopus"
                    },
                },
            },
            {
                'title': 'ثبت مقاله ISI',
                'description': 'این فعالیت برای ثبت مقاله منتشرشده در مجلات ISI یا Web of Science است و نشان‌دهنده تجربه پژوهشی معتبر و انتشار علمی در سطح بین‌المللی محسوب می‌شود.',
                'category': 'پژوهشی',
                'resume_output': 'ثبت مقاله ISI',
                'duration_days': 300,
                'resume_target': 'article',
                'profile_template': {
                    "model": "articles",
                    "data": {
                        "title": "مقاله چاپ‌شده در مجله ISI",
                        "journal": "Web of Science Journal",
                        "impact_factor": 4.2,
                        "quartile": "Q2",
                        "year": 1403,
                        "author_rank": 1,
                        "total_authors": 6,
                        "index": "ISI / Web of Science"
                    },
                },
            },
            {
                'title': 'ثبت مقاله پابمد',
                'description': 'این فعالیت مربوط به ثبت مقاله نمایه‌شده در PubMed است و برای نمایش سوابق پژوهشی در حوزه علوم پزشکی و زیستی در رزومه کاربرد دارد.',
                'category': 'پژوهشی',
                'resume_output': 'ثبت مقاله پابمد',
                'duration_days': 210,
                'resume_target': 'article',
                'profile_template': {
                    "model": "articles",
                    "data": {
                        "title": "مقاله ثبت‌شده در PubMed",
                        "journal": "PubMed Indexed Journal",
                        "impact_factor": 1.8,
                        "quartile": "Q4",
                        "year": 1402,
                        "author_rank": 3,
                        "total_authors": 5,
                        "index": "PubMed"
                    },
                },
            },

            # ارائه
            {
                'title': 'ارائه پوستر در همایش دانشجویی',
                'description': 'این فعالیت نشان‌دهنده ارائه نتایج یک کار علمی به شکل پوستر در همایش دانشجویی است و تجربه خوبی برای ورود به فضای ارائه‌های پژوهشی محسوب می‌شود.',
                'category': 'پژوهشی',
                'resume_output': 'ارائه پوستر علمی',
                'duration_days': 30,
                'resume_target': 'presentation',
                'profile_template': {
                    "model": "presentations",
                    "data": {
                        "title": "ارائه پوستر علمی",
                        "event": "همایش دانشجویی پژوهش",
                        "level": "دانشگاهی",
                        "result": "ارائه عادی"
                    },
                },
            },
            {
                'title': 'ارائه سخنرانی در کنگره ملی',
                'description': 'این فعالیت مربوط به ارائه شفاهی یک موضوع علمی در کنگره ملی است و نشان‌دهنده توانایی انتقال یافته‌های پژوهشی و حضور فعال در رویدادهای علمی کشور است.',
                'category': 'پژوهشی',
                'resume_output': 'ارائه سخنرانی ملی',
                'duration_days': 45,
                'resume_target': 'presentation',
                'profile_template': {
                    "model": "presentations",
                    "data": {
                        "title": "سخنرانی علمی در کنگره ملی",
                        "event": "کنگره ملی تخصصی",
                        "level": "ملی",
                        "result": "ارائه عادی"
                    },
                },
            },
            {
                'title': 'کسب جایزه در کنگره بین‌المللی',
                'description': 'این فعالیت برای ثبت ارائه برگزیده یا کسب جایزه در یک کنگره بین‌المللی استفاده می‌شود و نشان‌دهنده کیفیت بالای کار علمی و رقابت‌پذیری در سطح بین‌المللی است.',
                'category': 'پژوهشی',
                'resume_output': 'کسب جایزه بین‌المللی',
                'duration_days': 60,
                'resume_target': 'presentation',
                'profile_template': {
                    "model": "presentations",
                    "data": {
                        "title": "ارائه برگزیده در کنگره بین‌المللی",
                        "event": "کنگره بین‌المللی علوم پزشکی",
                        "level": "بین‌المللی",
                        "result": "برگزیده / جایزه"
                    },
                },
            },

            # اجرايي
            {
                'title': 'عضویت در انجمن علمی',
                'description': 'این فعالیت نشان‌دهنده عضویت در انجمن علمی دانشکده و مشارکت در برنامه‌های آموزشی، پژوهشی یا دانشجویی است و می‌تواند تجربه کار گروهی را تقویت کند.',
                'category': 'آموزشی',
                'resume_output': 'عضویت انجمن علمی',
                'duration_days': 180,
                'resume_target': 'executive_record',
                'profile_template': {
                    "model": "executive_records",
                    "data": {
                        "title": "عضو انجمن علمی دانشکده",
                        "start_date": "{today}",
                        "end_date": ""
                    },
                },
            },
            {
                'title': 'دبیری انجمن علمی',
                'description': 'این فعالیت برای ثبت نقش دبیری انجمن علمی است و نشان‌دهنده تجربه مدیریت تیم، برنامه‌ریزی فعالیت‌ها و هماهنگی رویدادهای علمی و آموزشی محسوب می‌شود.',
                'category': 'آموزشی',
                'resume_output': 'دبیری انجمن علمی',
                'duration_days': 365,
                'resume_target': 'executive_record',
                'profile_template': {
                    "model": "executive_records",
                    "data": {
                        "title": "دبیر انجمن علمی دانشکده",
                        "start_date": "{today}",
                        "end_date": ""
                    },
                },
            },
            {
                'title': 'عضویت در کمیته تحقیقات',
                'description': 'این فعالیت مربوط به عضویت در کمیته تحقیقات دانشجویی است و نشان‌دهنده علاقه و مشارکت فعال در فعالیت‌های پژوهشی، کارگاه‌ها و پروژه‌های علمی دانشجویی است.',
                'category': 'پژوهشی',
                'resume_output': 'عضویت کمیته تحقیقات',
                'duration_days': 180,
                'resume_target': 'executive_record',
                'profile_template': {
                    "model": "executive_records",
                    "data": {
                        "title": "عضو کمیته تحقیقات دانشجویی",
                        "start_date": "{today}",
                        "end_date": ""
                    },
                },
            },
            {
                'title': 'مسئولیت اجرایی در کنگره یا سمینار',
                'description': 'این فعالیت برای ثبت تجربه اجرایی در برگزاری کنگره، سمینار یا رویداد علمی است و نشان‌دهنده مهارت در هماهنگی، اجرا و همکاری تیمی در فضای علمی است.',
                'category': 'آموزشی',
                'resume_output': 'مسئولیت اجرایی علمی',
                'duration_days': 30,
                'resume_target': 'executive_record',
                'profile_template': {
                    "model": "executive_records",
                    "data": {
                        "title": "عضو اجرایی کنگره یا سمینار علمی",
                        "start_date": "{today}",
                        "end_date": ""
                    },
                },
            },

            # پروفايل اجتماعي
            {
                'title': 'ساخت پروفایل LinkedIn',
                'description': 'این فعالیت برای ایجاد یا تکمیل پروفایل LinkedIn است تا سوابق آموزشی، پژوهشی، مهارتی و حرفه‌ای شما به شکل منظم در یک شبکه تخصصی نمایش داده شود.',
                'category': 'آموزشی',
                'resume_output': 'ساخت پروفایل لینکدین',
                'duration_days': 7,
                'resume_target': 'social_profile',
                'profile_template': {
                    "model": "social_profiles",
                    "data": {
                        "social_type": "LinkedIn",
                        "url": "https://linkedin.com/in/your-profile"
                    },
                },
            },
            {
                'title': 'ساخت پروفایل Google Scholar',
                'description': 'این فعالیت برای ساخت پروفایل Google Scholar استفاده می‌شود تا مقالات، ارجاعات علمی و سوابق پژوهشی شما در یک صفحه علمی قابل مشاهده و پیگیری باشد.',
                'category': 'پژوهشی',
                'resume_output': 'ساخت پروفایل گوگل اسکالر',
                'duration_days': 7,
                'resume_target': 'social_profile',
                'profile_template': {
                    "model": "social_profiles",
                    "data": {
                        "social_type": "Google Scholar",
                        "url": "https://scholar.google.com/citations?user=your-id"
                    },
                },
            },
            {
                'title': 'ساخت پروفایل ResearchGate',
                'description': 'این فعالیت مربوط به ایجاد پروفایل ResearchGate است و به شما کمک می‌کند آثار پژوهشی خود را معرفی کنید، با پژوهشگران دیگر ارتباط بگیرید و فعالیت علمی خود را نمایش دهید.',
                'category': 'پژوهشی',
                'resume_output': 'ساخت پروفایل ریسرچ‌گیت',
                'duration_days': 7,
                'resume_target': 'social_profile',
                'profile_template': {
                    "model": "social_profiles",
                    "data": {
                        "social_type": "ResearchGate",
                        "url": "https://www.researchgate.net/profile/your-profile"
                    },
                },
            },
        ]
                
        for activity_data in activities_data:
            activity, created = Activity.objects.update_or_create(
                title=activity_data['title'],
                defaults=activity_data
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'فعالیت "{activity.title}" ایجاد شد')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'فعالیت "{activity.title}" قبلاً وجود دارد')
                )
