# networking/forms.py

from django import forms
from accounts.models import Profile

class ProfileSearchFilterForm(forms.Form):
    """فرم برای سرچ و فیلتر پروفایل‌ها"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'جستجو بر اساس نام یا تخصص...',
            'aria-label': 'جستجو'
        })
    )
    
    goal = forms.ChoiceField(
        required=False,
        choices=[('', 'تمام اهداف')] + Profile.GOAL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    english_level = forms.ChoiceField(
        required=False,
        choices=[('', 'تمام سطح‌ها')] + Profile.ENGLISH_LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'تمام جنسیت‌ها')] + Profile.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کشور...'
        })
    )
    
    military_status = forms.ChoiceField(
        required=False,
        choices=[('', 'تمام وضعیت‌ها')] + Profile.MILITARY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
