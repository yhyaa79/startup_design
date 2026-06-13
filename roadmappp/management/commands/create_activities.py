# roadmap/management/commands/create_activities.py

from django.core.management.base import BaseCommand
from roadmap.models import Activity


class Command(BaseCommand):
    help = 'ایجاد فعالیت‌های پیش‌فرض'

    def handle(self, *args, **options):
        activities_data = [
            # پژوهشی
            {'title': 'نوشتن پروپوزال پژوهشی', 'category': 'پژوهشی', 'duration_hours': 40, 'difficulty_level': 'سخت'},
            {'title': 'مطالعه منابع و مقالات', 'category': 'پژوهشی', 'duration_hours': 60, 'difficulty_level': 'متوسط'},
            {'title': 'تجزیه و تحلیل داده‌ها', 'category': 'پژوهشی', 'duration_hours': 50, 'difficulty_level': 'سخت'},
            {'title': 'نوشتن مقاله علمی', 'category': 'پژوهشی', 'duration_hours': 80, 'difficulty_level': 'سخت'},
            {'title': 'ارائه در کنفرانس', 'category': 'پژوهشی', 'duration_hours': 20, 'difficulty_level': 'متوسط'},
            {'title': 'بررسی متون علمی', 'category': 'پژوهشی', 'duration_hours': 30, 'difficulty_level': 'متوسط'},

            # بالینی
            {'title': 'کار بالینی در بخش', 'category': 'بالینی', 'duration_hours': 120, 'difficulty_level': 'سخت'},
            {'title': 'یادگیری پروسیجرهای بالینی', 'category': 'بالینی', 'duration_hours': 40, 'difficulty_level': 'سخت'},
            {'title': 'ارتقاء مهارت‌های ارتباطی', 'category': 'بالینی', 'duration_hours': 20, 'difficulty_level': 'متوسط'},
            {'title': 'کار تحت نظارت متخصص', 'category': 'بالینی', 'duration_hours': 60, 'difficulty_level': 'متوسط'},

            # آموزشی
            {'title': 'شرکت در کارگاه آموزشی', 'category': 'آموزشی', 'duration_hours': 16, 'difficulty_level': 'آسان'},
            {'title': 'کسب مدرک آموزشی', 'category': 'آموزشی', 'duration_hours': 40, 'difficulty_level': 'متوسط'},
            {'title': 'تدریس و آموزش همتایان', 'category': 'آموزشی', 'duration_hours': 30, 'difficulty_level': 'متوسط'},

            # نرم‌افزاری
            {'title': 'یادگیری نرم‌افزار آماری', 'category': 'نرم‌افزاری', 'duration_hours': 50, 'difficulty_level': 'متوسط'},
            {'title': 'یادگیری Python/R', 'category': 'نرم‌افزاری', 'duration_hours': 60, 'difficulty_level': 'سخت'},
            {'title': 'یادگیری LaTeX', 'category': 'نرم‌افزاری', 'duration_hours': 20, 'difficulty_level': 'آسان'},
            {'title': 'یادگیری Mendeley/Zotero', 'category': 'نرم‌افزاری', 'duration_hours': 10, 'difficulty_level': 'آسان'},

            # زبان
            {'title': 'کلاس زبان انگلیسی', 'category': 'زبان', 'duration_hours': 100, 'difficulty_level': 'متوسط'},
            {'title': 'مطالعه خود‌درس زبان', 'category': 'زبان', 'duration_hours': 80, 'difficulty_level': 'متوسط'},
            {'title': 'امتحان IELTS/TOEFL', 'category': 'زبان', 'duration_hours': 30, 'difficulty_level': 'سخت'},

            # سایر
            {'title': 'فعالیت‌های فوق برنامه', 'category': 'سایر', 'duration_hours': 40, 'difficulty_level': 'آسان'},
            {'title': 'مشارکت در پروژه‌های تیمی', 'category': 'سایر', 'duration_hours': 50, 'difficulty_level': 'متوسط'},
            {'title': 'توسعه مهارت‌های رهبری', 'category': 'سایر', 'duration_hours': 30, 'difficulty_level': 'متوسط'},
        ]

        for data in activities_data:
            activity, created = Activity.objects.get_or_create(
                title=data['title'],
                defaults={
                    'description': f"فعالیت: {data['title']}",
                    'category': data['category'],
                    'duration_hours': data['duration_hours'],
                    'difficulty_level': data['difficulty_level'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'ایجاد شد: {activity.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'موجود است: {activity.title}'))

        self.stdout.write(self.style.SUCCESS('تمام فعالیت‌ها ایجاد شدند'))
