# course/models.py

from django.db import models


class Category(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'

    def __str__(self):
        return self.name


class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    short_desc = models.CharField(max_length=300)
    long_desc = models.TextField()
    stars = models.PositiveSmallIntegerField(default=5)
    duration = models.CharField(max_length=50, blank=True)
    main_price = models.CharField(max_length=30, blank=True)
    discount_price = models.CharField(max_length=30, blank=True)
    percentage = models.CharField(max_length=10, blank=True)
    instructor = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='image_card/', blank=True, null=True)
    video_link = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__order', 'course_id']
        verbose_name = 'دوره'
        verbose_name_plural = 'دوره‌ها'

    def __str__(self):
        return self.title

    def has_discount(self):
        return bool(self.discount_price and self.percentage)