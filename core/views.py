# core/views.py

from django.shortcuts import render
from django.views.generic import TemplateView 
from django.contrib.auth.decorators import login_required

class ComingSoonView(TemplateView):
    template_name = 'coming_soon.html'



# core/views.py
from roadmap.models import Roadmap

@login_required
def home(request):
    roadmap = getattr(request.user.profile, 'roadmap', None)
    active_stage = None
    stages = []
    
    if roadmap:
        stages = roadmap.stages.all().order_by('order')
        # پیدا کردن اولین مرحله‌ای که ۱۰۰ درصد نشده است
        for stage in stages:
            if stage.get_progress() < 100:
                active_stage = stage
                break
                
    context = {
        'roadmap': roadmap,
        'stages': stages,
        'active_stage': active_stage,
        'total_progress': roadmap.get_total_progress() if roadmap else 0,
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

