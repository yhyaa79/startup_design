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
            {
                'title': 'شرکت در کارگاه مقاله‌نویسی علمی',
                'description': 'در این کارگاه با اصول نگارش مقاله علمی، ساختار بخش‌های مختلف مقاله و نکات مهم برای آماده‌سازی متن پژوهشی قابل ارسال به ژورنال آشنا می‌شوید.',
                'category': 'پژوهشی',
                'field': 'عمومی',
                'resume_output': 'تقویت مهارت مقاله‌نویسی علمی و آشنایی با ساختار مقالات ISI',
                'duration_days': 14,
                'difficulty_level': 'متوسط',
                'prerequisites': 'آشنایی پایه با زبان انگلیسی علمی',
                'resources': 'سایت Pubmed، کتاب How to Write and Publish a Scientific Paper',
                'resume_target': 'training_course',
                'suitable_goals': ['استعداد درخشان', '۴۰ امتیازی', 'هیات علمی', 'ریسرچ پوزیشن / فلوشیپ خارج'],
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
                    }
                },
            },
            {
                'title': 'شرکت در کارگاه پروپوزال‌نویسی',
                'description': 'این کارگاه به شما کمک می‌کند ایده پژوهشی خود را به یک پروپوزال منظم تبدیل کنید و با نحوه تدوین سوال پژوهش، اهداف، روش اجرا و اهمیت مطالعه آشنا شوید.',
                'category': 'پژوهشی',
                'field': 'عمومی',
                'resume_output': 'توانایی نوشتن پروپوزال تحقیقاتی استاندارد',
                'duration_days': 14,
                'difficulty_level': 'متوسط',
                'prerequisites': 'آشنایی پایه با روش تحقیق',
                'resources': 'دستورالعمل‌های معاونت تحقیقات دانشگاه علوم پزشکی',
                'resume_target': 'training_course',
                'suitable_goals': ['استعداد درخشان', '۴۰ امتیازی', 'هیات علمی', 'ریسرچ پوزیشن / فلوشیپ خارج'],
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
                    }
                },
            },
            {
                'title': 'دریافت نمره IELTS یا TOEFL معتبر',
                'description': 'آمادگی و شرکت در آزمون زبان انگلیسی IELTS Academic یا TOEFL iBT برای اثبات توانایی زبانی در سطح بین‌المللی، ضروری برای ارسال مقاله، شرکت در کنگره خارجی و اپلای.',
                'category': 'زبان',
                'field': 'عمومی',
                'resume_output': 'مدرک زبان معتبر بین‌المللی (IELTS/TOEFL)',
                'duration_days': 90,
                'difficulty_level': 'سخت',
                'prerequisites': 'سطح زبان حداقل B1',
                'resources': 'Cambridge IELTS books, Magoosh TOEFL, سایت ielts.org',
                'resume_target': 'training_course',
                'suitable_goals': ['ریسرچ پوزیشن / فلوشیپ خارج', 'هیات علمی'],
                'profile_template': {
                    "model": "training_courses",
                    "data": {
                        "title": "آزمون زبان بین‌المللی IELTS/TOEFL",
                        "category": "زبان",
                        "status": "تکمیل‌شده",
                        "organizer": "مرکز آزمون بین‌المللی",
                        "date": "{today}",
                        "certificate": "دارد",
                        "skills_gained": "مهارت‌های چهارگانه زبان انگلیسی در سطح آکادمیک"
                    }
                },
            },
            {
                'title': 'ارائه پوستر یا سخنرانی در کنگره ملی',
                'description': 'ارائه نتایج یک مطالعه یا پروژه تحقیقاتی در قالب پوستر یا سخنرانی در یک کنگره یا همایش علمی در سطح ملی. این فعالیت مهارت ارائه و شبکه‌سازی حرفه‌ای را تقویت می‌کند.',
                'category': 'پژوهشی',
                'field': 'عمومی',
                'resume_output': 'سابقه ارائه علمی در کنگره ملی',
                'duration_days': 30,
                'difficulty_level': 'متوسط',
                'prerequisites': 'داشتن یک مطالعه یا پروژه تحقیقاتی قابل ارائه',
                'resources': 'سایت‌های کنگره‌های پزشکی ایران، ایمیل انجمن‌های علمی تخصصی',
                'resume_target': 'presentation',
                'suitable_goals': ['استعداد درخشان', '۴۰ امتیازی', 'هیات علمی', 'ریسرچ پوزیشن / فلوشیپ خارج'],
                'profile_template': {
                    "model": "presentations",
                    "data": {
                        "title": "ارائه در کنگره علمی ملی",
                        "event": "کنگره علمی ملی",
                        "level": "ملی",
                        "result": "ارائه عادی"
                    }
                },
            },
            {
                'title': 'عضویت فعال در کمیته تحقیقات دانشجویی',
                'description': 'عضویت و فعالیت مستمر در کمیته تحقیقات دانشجویی (EDC/SDC) دانشگاه، شامل شرکت در جلسات، همکاری در برگزاری رویدادهای پژوهشی و کمک به اجرای پروژه‌های تحقیقاتی.',
                'category': 'شبکه‌سازی',
                'field': 'عمومی',
                'resume_output': 'سابقه اجرایی در کمیته تحقیقات دانشجویی',
                'duration_days': 180,
                'difficulty_level': 'آسان',
                'prerequisites': '',
                'resources': 'معاونت تحقیقات دانشگاه علوم پزشکی',
                'resume_target': 'executive_record',
                'suitable_goals': ['استعداد درخشان', '۴۰ امتیازی'],
                'profile_template': {
                    "model": "executive_records",
                    "data": {
                        "title": "عضو فعال کمیته تحقیقات دانشجویی",
                        "start_date": "{today}",
                        "end_date": ""
                    }
                },
            },
        ]

        for activity_data in activities_data:
            activity, created = Activity.objects.update_or_create(
                title=activity_data['title'],
                defaults=activity_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'فعالیت "{activity.title}" ایجاد شد'))
            else:
                self.stdout.write(self.style.WARNING(f'فعالیت "{activity.title}" به‌روز شد'))