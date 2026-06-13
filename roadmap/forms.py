# roadmap/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Roadmap, Stage, StageActivity, Activity


class RoadmapForm(forms.ModelForm):
    class Meta:
        model = Roadmap
        fields = ['title', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان رود مپ را وارد کنید'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'توضیح رود مپ را وارد کنید'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['title', 'description', 'objectives', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان مرحله'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'توضیح مرحله'
            }),
            'objectives': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'اهداف مرحله را وارد کنید'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'
            }),
        }


class StageActivityForm(forms.ModelForm):
    activity = forms.ModelChoiceField(
        queryset=Activity.objects.filter(is_active=True).order_by('category', 'title'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%;'
        }),
        label='فعالیت',
        required=False,
        empty_label='--- انتخاب کنید ---'
    )

    class Meta:
        model = StageActivity
        fields = ['activity', 'order']
        widgets = {

            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].required = False
        self.fields['order'].initial = 0

    def clean_order(self):
        return self.cleaned_data.get('order') or 0

    def validate_unique(self):
        # اگه activity انتخاب نشده، unique check نزن
        if not self.cleaned_data.get('activity'):
            return
        super().validate_unique()



StageActivityFormSet = inlineformset_factory(
    Stage,
    StageActivity,
    form=StageActivityForm,
    extra=0,
    can_delete=True,
)
