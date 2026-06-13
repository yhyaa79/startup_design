# roadmap/forms.py

from django import forms
from .models import Roadmap, Stage, StageActivity, Activity


class RoadmapForm(forms.ModelForm):
    class Meta:
        model = Roadmap
        fields = ['title', 'description', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان رود‌مپ'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'توضیح رود‌مپ',
                'rows': 4
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['title', 'description', 'status', 'order', 'objectives', 'resume_output', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان مرحله'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'توضیح مرحله',
                'rows': 3
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'
            }),
            'objectives': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'اهداف مرحله',
                'rows': 4
            }),
            'resume_output': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'خروجی رزومه‌ای',
                'rows': 3
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class StageActivityForm(forms.ModelForm):
    activity = forms.ModelChoiceField(
        queryset=Activity.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='فعالیت'
    )

    class Meta:
        model = StageActivity
        fields = ['activity', 'repetition', 'is_completed', 'notes', 'order']
        widgets = {
            'repetition': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': 1,
                'value': 1
            }),
            'is_completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'یادداشت‌ها',
                'rows': 2
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'
            }),
        }


class StageActivityFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        activities = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                activity = form.cleaned_data.get('activity')
                if activity in activities:
                    raise forms.ValidationError('نمی‌توانید یک فعالیت را دو بار اضافه کنید')
                activities.append(activity)
