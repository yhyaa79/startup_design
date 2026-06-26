# project/forms.py

from django import forms
from django.utils.text import slugify
from .models import ResearchProject, ProjectApplication, ProjectUpdate, ProjectFile


class ResearchProjectForm(forms.ModelForm):
    class Meta:
        model = ResearchProject
        fields = [
            'title',
            'slug',
            'short_description',
            'description',
            'category',
            'status',
            'collaboration_status',
            'visibility',
            'field',
            'keywords',
            'methodology',
            'required_skills',
            'expected_output',
            'supervisor',
            'institution',
            'ethics_code',
            'start_date',
            'estimated_end_date',
            'capacity',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'slug': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'short_description': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'description': forms.Textarea(attrs={'class': 'pr-form-textarea', 'rows': 6}),
            'category': forms.Select(attrs={'class': 'pr-form-select'}),
            'status': forms.Select(attrs={'class': 'pr-form-select'}),
            'collaboration_status': forms.Select(attrs={'class': 'pr-form-select'}),
            'visibility': forms.Select(attrs={'class': 'pr-form-select'}),
            'field': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'keywords': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'methodology': forms.Textarea(attrs={'class': 'pr-form-textarea', 'rows': 4}),
            'required_skills': forms.Textarea(attrs={'class': 'pr-form-textarea', 'rows': 4}),
            'expected_output': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'supervisor': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'institution': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'ethics_code': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'start_date': forms.TextInput(attrs={'class': 'pr-form-input', 'placeholder': 'مثلاً 1405/04'}),
            'estimated_end_date': forms.TextInput(attrs={'class': 'pr-form-input', 'placeholder': 'مثلاً 1405/12'}),
            'capacity': forms.NumberInput(attrs={'class': 'pr-form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'pr-form-checkbox'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')

        if not slug and title:
            slug = slugify(title, allow_unicode=True)

        return slug


class ProjectApplicationForm(forms.ModelForm):
    class Meta:
        model = ProjectApplication
        fields = ['message', 'skills']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'pr-form-textarea',
                'rows': 5,
                'placeholder': 'توضیح دهید چرا می‌خواهید در این پروژه همکاری کنید...'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'pr-form-textarea',
                'rows': 4,
                'placeholder': 'مهارت‌ها، تجربه‌ها، دوره‌ها یا مقالات مرتبط خود را بنویسید...'
            }),
        }


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = ProjectUpdate
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'text': forms.Textarea(attrs={'class': 'pr-form-textarea', 'rows': 5}),
        }


class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'pr-form-input'}),
            'file': forms.ClearableFileInput(attrs={'class': 'pr-form-input'}),
        }
