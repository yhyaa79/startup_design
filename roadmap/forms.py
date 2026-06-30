# roadmap/forms.py
from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Roadmap, Stage, Activity, StageActivity


class RoadmapCreateForm(forms.ModelForm):
    """فرم ایجاد رودمپ"""
    
    GOAL_CHOICES = [
        ('estedad_darakhshan', '🌟 استعداد درخشان'),
        ('40_emtiaz', '📊 ۴۰ امتیازی'),
        ('heyat_elmi', '👨‍🎓 هیات علمی'),
        ('research_position', '🌍 ریسرچ پوزیشن / فلوشیپ خارج'),
        ('general', '📈 بهبود عمومی'),
    ]
    
    goal = forms.ChoiceField(
        choices=GOAL_CHOICES,
        widget=forms.RadioSelect,
        label='هدف خود را انتخاب کنید'
    )
    
    duration_days = forms.IntegerField(
        min_value=30,
        max_value=1095,
        label='مدت زمان (روز)',
        help_text='حداقل 30 روز، حداکثر 3 سال'
    )
    
    goal_details = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='جزئیات اضافی (اختیاری)',
        help_text='توضیحات بیشتری درباره اهدافتان بنویسید'
    )
    
    class Meta:
        model = Roadmap
        fields = ['goal', 'duration_days', 'goal_details']
    
    def clean_duration_days(self):
        duration = self.cleaned_data.get('duration_days')
        return duration



class StageForm(forms.ModelForm):
    """فرم ایجاد/ویرایش مرحله"""
    
    success_criteria = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='معیارهای موفقیت (هر یک در خط جدید)',
        help_text='معیارهای تکمیل مرحله را وارد کنید'
    )
    
    risks = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='ریسک‌های احتمالی (هر یک در خط جدید)',
        help_text='چالش‌های احتمالی را لیست کنید'
    )
    
    class Meta:
        model = Stage
        fields = [
            'title', 'description', 'objectives', 'phase_type',
            'priority', 'milestone'
        ]

        labels = {
            'title': 'عنوان مرحله',
            'description': 'توضیحات',
            'objectives': 'اهداف مرحله',
            'phase_type': 'نوع فاز',
            'priority': 'اولویت',
            'duration_days': 'مدت زمان (روز)',
            'milestone': 'نقطه عطف (معیار تکمیل)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # تبدیل معیارهای موفقیت
        criteria_text = cleaned_data.get('success_criteria', '')
        if criteria_text:
            criteria = [c.strip() for c in criteria_text.split('\n') if c.strip()]
            self.instance.success_criteria = criteria
        
        # تبدیل ریسک‌ها
        risks_text = cleaned_data.get('risks', '')
        if risks_text:
            risks = [r.strip() for r in risks_text.split('\n') if r.strip()]
            self.instance.risks = risks
        
        return cleaned_data


class ActivityForm(forms.ModelForm):
    """فرم ایجاد/ویرایش فعالیت"""
    
    class Meta:
        model = Activity
        fields = [
            'title', 'description', 'category', 'duration_days',
            'impact_score', 'difficulty_rating', 'resume_output'
        ]
        labels = {
            'title': 'عنوان فعالیت',
            'description': 'توضیحات',
            'category': 'دسته',
            'duration_days': 'مدت زمان (روز)',
            'impact_score': 'امتیاز تاثیر',
            'difficulty_rating': 'سطح دشواری',
            'resume_output': 'خروجی رزومه',
        }
