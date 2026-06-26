from django import forms
from .models import Resume, TEMPLATE_CHOICES, PURPOSE_CHOICES


class ResumeCreateForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = [
            'title', 'purpose', 'template', 'use_ai',
            'include_education', 'include_articles', 'include_presentations',
            'include_executive', 'include_training', 'include_clinical',
            'include_languages', 'include_skills', 'include_extracurricular',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: رزومه رزیدنتی ۱۴۰۳'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'template': forms.RadioSelect(attrs={'class': 'template-radio'}),
            'use_ai': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'useAI'}),
            'include_education': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_articles': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_presentations': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_executive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_training': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_clinical': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_languages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_skills': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_extracurricular': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'عنوان رزومه',
            'purpose': 'هدف رزومه',
            'template': 'انتخاب قالب',
            'use_ai': 'بهبود محتوا با هوش مصنوعی',
            'include_education': 'تحصیلات',
            'include_articles': 'مقالات',
            'include_presentations': 'ارائه‌ها در کنگره',
            'include_executive': 'سوابق اجرایی',
            'include_training': 'دوره‌های آموزشی',
            'include_clinical': 'سوابق بالینی',
            'include_languages': 'زبان‌ها',
            'include_skills': 'مهارت‌های نرم‌افزاری',
            'include_extracurricular': 'فعالیت‌های فوق برنامه',
        }