# event_hub/views.py

from django.shortcuts import get_object_or_404, render
from .models import Event


def event_list(request):
    events = Event.objects.all()
    return render(request, 'event_hub/event_list.html', {'events': events})


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'event_hub/event_detail.html', {'event': event})
