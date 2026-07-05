# core/middleware.py

from datetime import timedelta
from django.utils import timezone
from .models import DailyOnlineActivity

class OnlineActivityTrackerMiddleware:
    """
    زمان بین request های کاربر را حساب می‌کند و در DailyOnlineActivity ذخیره می‌کند.
    فرض: اگر فاصله‌ی دو ریکوئست کمتر از 5 دقیقه باشد، آن فاصله جزو زمان آنلاین حساب می‌شود.
    """
    SESSION_GAP_MINUTES = 5
    SESSION_KEY_LAST_SEEN = '_last_seen_at'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            self._track(request)

        return response

    def _track(self, request):
        now = timezone.now()
        last_seen_str = request.session.get(self.SESSION_KEY_LAST_SEEN)
        today = now.date()

        obj, _ = DailyOnlineActivity.objects.get_or_create(
            user=request.user, date=today,
            defaults={'duration_minutes': 0, 'session_count': 1}
        )

        if last_seen_str:
            last_seen = timezone.datetime.fromisoformat(last_seen_str)
            if timezone.is_naive(last_seen):
                last_seen = timezone.make_aware(last_seen)

            gap = now - last_seen
            if gap <= timedelta(minutes=self.SESSION_GAP_MINUTES) and last_seen.date() == today:
                added_minutes = int(gap.total_seconds() // 60)
                if added_minutes > 0:
                    obj.duration_minutes += added_minutes
                    obj.save(update_fields=['duration_minutes'])
            elif last_seen.date() != today:
                obj.session_count += 1
                obj.save(update_fields=['session_count'])

        request.session[self.SESSION_KEY_LAST_SEEN] = now.isoformat()
