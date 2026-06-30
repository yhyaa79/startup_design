'''from django.core.management.base import BaseCommand
from roadmap.models import Activity

STATIC_ITEMS = {
    "course": [
        {"id": "c1", "title": "کارگاه مقاله‌نویسی علمی ISI", "organizer": "معاونت تحقیقات", "duration": 14},
        {"id": "c2", "title": "کارگاه پروپوزال‌نویسی", "organizer": "معاونت تحقیقات", "duration": 10},
        {"id": "c3", "title": "دوره آمار پزشکی و SPSS", "organizer": "آنلاین", "duration": 30},
        {"id": "c4", "title": "دوره زبان تخصصی پزشکی", "organizer": "آنلاین", "duration": 45},
        {"id": "c5", "title": "کارگاه مهارت‌های ارائه علمی", "organizer": "دانشگاه", "duration": 7},
        {"id": "c6", "title": "دوره EndNote / Mendeley", "organizer": "آنلاین", "duration": 5},
        {"id": "c7", "title": "دوره Systematic Review", "organizer": "آنلاین", "duration": 20},
        {"id": "c8", "title": "کارگاه اخلاق در پژوهش", "organizer": "دانشگاه", "duration": 8},
        {"id": "c9", "title": "دوره نرم‌افزار R برای پزشکان", "organizer": "آنلاین", "duration": 35},
        {"id": "c10", "title": "کارگاه Clinical Trial Design", "organizer": "دانشگاه", "duration": 12},
    ],
    "event": [
        {"id": "e1", "title": "کنگره سراسری پزشکی", "level": "ملی", "duration": 3},
        {"id": "e2", "title": "سمپوزیوم دانشجویی علوم پزشکی", "level": "دانشگاهی", "duration": 1},
        {"id": "e3", "title": "کنفرانس بین‌المللی تحقیقات پزشکی", "level": "بین‌المللی", "duration": 5},
        {"id": "e4", "title": "جشنواره شهید رهنمون", "level": "ملی", "duration": 2},
        {"id": "e5", "title": "Journal Club دانشگاهی", "level": "دانشگاهی", "duration": 1},
        {"id": "e6", "title": "وبینار تخصصی حوزه پژوهش", "level": "ملی", "duration": 2},
        {"id": "e7", "title": "کنگره تخصصی رشته", "level": "ملی", "duration": 3},
        {"id": "e8", "title": "رویداد networking IFMSA", "level": "بین‌المللی", "duration": 2},
    ],
    "project": [
        {"id": "p1", "title": "پروژه تحقیقاتی دانشجویی", "duration": 60},
        {"id": "p2", "title": "همکاری در طرح تحقیقاتی استاد", "duration": 90},
        {"id": "p3", "title": "پروژه کارآموزی بالینی تحقیقاتی", "duration": 45},
        {"id": "p4", "title": "پروژه نرم‌افزاری سلامت", "duration": 60},
        {"id": "p5", "title": "طراحی اپلیکیشن پزشکی", "duration": 75},
        {"id": "p6", "title": "پروژه آموزشی (تولید محتوا)", "duration": 30},
        {"id": "p7", "title": "پروژه خدمات اجتماعی سلامت", "duration": 20},
    ],
    "research": [
        {"id": "r1", "title": "نگارش و ارسال مقاله Case Report", "duration": 45},
        {"id": "r2", "title": "نگارش و ارسال مقاله Original Article", "duration": 90},
        {"id": "r3", "title": "نگارش و ارسال مقاله Review Article", "duration": 60},
        {"id": "r4", "title": "نگارش و ارسال مقاله Letter to Editor", "duration": 14},
        {"id": "r5", "title": "ثبت پروپوزال در معاونت تحقیقات", "duration": 21},
        {"id": "r6", "title": "انجام Systematic Review", "duration": 120},
        {"id": "r7", "title": "ثبت طرح در کارآزمایی بالینی", "duration": 30},
        {"id": "r8", "title": "همکاری در نگارش فصل کتاب", "duration": 60},
    ],
}

class Command(BaseCommand):
    help = 'بارگذاری فعالیت‌های استاتیک'

    def handle(self, *args, **options):
        for category, items in STATIC_ITEMS.items():
            for item in items:
                Activity.objects.get_or_create(
                    external_id=item['id'],
                    defaults={
                        'title': item['title'],
                        'category': category,
                        'duration_days': item.get('duration', 7),
                        'organizer': item.get('organizer', ''),
                        'level': item.get('level', ''),
                        'impact_score': 7,
                        'difficulty_rating': 'medium',
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('فعالیت‌ها با موفقیت بارگذاری شدند'))
'''