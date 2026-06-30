# regulation_assessment/views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import UserVideoInterest

def evaluation_form(request):
    """نمایش فرم ارزیابی"""
    return render(request, 'regulation_assessment/evaluation_form.html')


@csrf_exempt
@require_http_methods(["POST"])
def save_user_video_interest(request):
    try:
        data = json.loads(request.body)
        
        # دریافت اطلاعات از درخواست
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        phone = data.get('phone')
        email = data.get('email')
        total_score = data.get('totalScore', 0)
        breakdown = data.get('breakdown', {})
        course_title = data.get('courseTitle')
        
        # بررسی وجود فیلدهای ضروری
        if not all([first_name, last_name, phone, email, course_title]):
            return JsonResponse({
                'success': False,
                'message': 'لطفاً تمام فیلدهای ضروری را پر کنید'
            }, status=400)
        
        # بررسی وجود کاربر با این شماره تلفن
        user_interest, created = UserVideoInterest.objects.get_or_create(
            phone=phone,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'total_score': total_score,
                'breakdown': breakdown,
                'requested_courses': [course_title]
            }
        )
        
        if not created:
            # اگر کاربر قبلاً وجود داشت، اطلاعات را بروزرسانی کن
            user_interest.first_name = first_name
            user_interest.last_name = last_name
            user_interest.email = email
            user_interest.total_score = total_score
            user_interest.breakdown = breakdown
            
            # اضافه کردن عنوان دوره جدید به لیست
            user_interest.add_course(course_title)
        
        return JsonResponse({
            'success': True,
            'message': 'اطلاعات با موفقیت ذخیره شد',
            'created': created
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'فرمت داده‌های ارسالی نامعتبر است'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در ذخیره‌سازی: {str(e)}'
        }, status=500)


def thank_you_page(request):
    """صفحه تشکر بعد از ثبت درخواست"""
    return render(request, 'regulation_assessment/thank_you.html')
