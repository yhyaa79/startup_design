# networking/models.py


from django.db import models
from accounts.models import Profile

class NetworkingConnection(models.Model):
    """مدل برای ذخیره ارتباطات بین کاربران"""
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='connections_sent')
    to_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='connections_received')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'در انتظار'),
            ('accepted', 'پذیرفته شده'),
            ('rejected', 'رد شده'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'اتصال شبکه'
        verbose_name_plural = 'اتصالات شبکه'
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}'
