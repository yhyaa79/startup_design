# regulation_assessment/models.py

from django.db import models
from django.core.validators import RegexValidator

class UserVideoInterest(models.Model):
    # اطلاعات کاربر
    first_name = models.CharField(max_length=100, verbose_name='نام')
    last_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message="شماره تلفن باید به فرمت 09xxxxxxxxx باشد"
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=11,
        unique=True,
        verbose_name='شماره تلفن'
    )
    
    email = models.EmailField(verbose_name='ایمیل')
    
    # اطلاعات امتیازات
    total_score = models.IntegerField(default=0, verbose_name='امتیاز کل')
    breakdown = models.JSONField(default=dict, verbose_name='جزئیات امتیازات')
    
    # لیست عناوین دوره‌های درخواستی
    requested_courses = models.JSONField(default=list, verbose_name='دوره‌های درخواستی')
    
    # تاریخ ثبت و آخرین بروزرسانی
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'علاقه‌مندی کاربر به ویدیو'
        verbose_name_plural = 'علاقه‌مندی‌های کاربران به ویدیوها'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"
    
    def add_course(self, course_title):
        """اضافه کردن عنوان دوره به لیست (اگر تکراری نباشد)"""
        if course_title not in self.requested_courses:
            self.requested_courses.append(course_title)
            self.save()
