from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, NoReverseMatch
from django import forms

from .models import DailyOnlineActivity, Tool


class ToolAdminForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'icon_svg': forms.Textarea(attrs={
                'rows': 6, 'style': 'font-family: monospace; direction: ltr;'
            }),
        }

    def clean(self):
        cleaned = super().clean()
        url_name = cleaned.get('url_name')
        external_url = cleaned.get('external_url')
        if not url_name and not external_url:
            raise forms.ValidationError(
                'باید حداقل یکی از «نام URL» یا «لینک جایگزین» را وارد کنید.'
            )
        if url_name:
            try:
                reverse(url_name)
            except NoReverseMatch:
                self.add_error(
                    'url_name',
                    'این نام URL در پروژه پیدا نشد. بررسی کنید namespace:name درست باشد.'
                )
        return cleaned


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    form = ToolAdminForm

    list_display = (
        'icon_preview', 'title', 'link_preview', 'status_badge',
        'is_new', 'order', 'updated_at',
    )
    list_display_links = ('title',)
    list_editable = ('is_new', 'order')
    list_filter = ('is_active', 'is_new')
    search_fields = ('title', 'description', 'url_name', 'external_url')
    ordering = ('order', '-created_at')

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description'),
        }),
        ('لینک ابزار', {
            'fields': ('url_name', 'external_url'),
            'description': 'اگر ابزار داخل خود پروژه است url_name را پر کنید '
                            '(مثال: regulation_assessment:evaluation_form). '
                            'در غیر این‌صورت لینک جایگزین را وارد کنید.',
        }),
        ('نمایش', {
            'fields': ('icon_svg', 'icon_preview_large'),
        }),
        ('وضعیت', {
            'fields': ('is_active', 'is_new', 'order'),
        }),
    )
    readonly_fields = ('icon_preview_large',)

    @admin.display(description='آیکون')
    def icon_preview(self, obj):
        if obj.icon_svg:
            return format_html(
                '<div style="width:28px;height:28px;">'
                '<svg viewBox="0 0 24 24" width="28" height="28" '
                'fill="none" stroke="currentColor" stroke-width="2">{}</svg></div>',
                format_html(obj.icon_svg)
            )
        return '—'

    @admin.display(description='پیش‌نمایش آیکون')
    def icon_preview_large(self, obj):
        if not obj.icon_svg:
            return 'برای پیش‌نمایش، ابتدا آیکون را ذخیره کنید.'
        return format_html(
            '<div style="width:64px;height:64px;color:#4f46e5;">'
            '<svg viewBox="0 0 24 24" width="64" height="64" '
            'fill="none" stroke="currentColor" stroke-width="2">{}</svg></div>',
            format_html(obj.icon_svg)
        )

    @admin.display(description='لینک')
    def link_preview(self, obj):
        url = obj.get_url()
        if url and url != '#':
            return format_html('<a href="{}" target="_blank">{}</a>', url, url[:50])
        return format_html('<span style="color:#dc2626;">لینک تنظیم نشده</span>')

    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        color = '#16a34a' if obj.is_active else '#dc2626'
        text = 'فعال' if obj.is_active else 'غیرفعال'
        return format_html(
            '<span style="background:{}22;color:{};padding:2px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            color, color, text
        )


@admin.register(DailyOnlineActivity)
class DailyOnlineActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'duration_minutes', 'session_count')
    list_filter = ('date',)
    search_fields = ('user__username', 'user__email')
