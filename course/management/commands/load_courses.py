# course/management/commands/load_courses.py


"python manage.py load_courses"

from django.core.management.base import BaseCommand
from django.db import transaction
from course.models import Category, Course
from course.data import VIDEO_DATABASE

CATEGORY_LABELS = {
    'olampiad_elmi': 'المپیاد علمی',
    'tahghighat': 'تحقیقات',
    'maghaleh': 'مقاله‌نویسی',
    'maghale_congress': 'کنگره',
    'ketab': 'تألیف کتاب',
    'ekhtera': 'ثبت اختراع',
    'noavari': 'نوآوری',
    'jashnvare': 'جشنواره',
    'bedone_dastebandi': 'متفرقه',
}


class Command(BaseCommand):
    help = "Import courses from data.py VIDEO_DATABASE into the database"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        error_count = 0

        for order, (cat_key, courses) in enumerate(VIDEO_DATABASE.items()):
            category, _ = Category.objects.get_or_create(
                slug=cat_key,
                defaults={'name': CATEGORY_LABELS.get(cat_key, cat_key), 'order': order}
            )

            self.stdout.write(f"\n--- دسته: {cat_key} ({len(courses)} دوره) ---")

            for c in courses:
                try:
                    with transaction.atomic():
                        defaults = {
                            'title': c.get('title', ''),
                            'category': category,
                            'short_desc': c.get('shortDesc', '')[:300],
                            'long_desc': c.get('longDesc', ''),
                            'stars': c.get('stars', 5),
                            'duration': c.get('duration', ''),
                            'main_price': c.get('mainPrice', ''),
                            'discount_price': c.get('discountPrice', ''),
                            'percentage': c.get('percentage', ''),
                            'instructor': c.get('instructor', ''),
                            'video_link': c.get('videoLink', ''),
                            'active': c.get('active', True),
                        }

                        obj, created = Course.objects.update_or_create(
                            course_id=c['id'],
                            defaults=defaults,
                        )

                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f"  + ایجاد شد: {c['id']} - {c.get('title')}"))
                    else:
                        updated_count += 1
                        self.stdout.write(f"  ~ به‌روزرسانی شد: {c['id']} - {c.get('title')}")

                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(
                        f"  ✗ خطا در '{c.get('id', 'نامشخص')}': {e}"
                    ))

        self.stdout.write(self.style.SUCCESS(
            f"\n\nنتیجه نهایی: {created_count} ایجاد، {updated_count} به‌روزرسانی، {error_count} خطا."
        ))
        self.stdout.write(f"مجموع دوره‌ها در دیتابیس: {Course.objects.count()}")
