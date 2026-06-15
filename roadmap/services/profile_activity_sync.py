# roadmap/services/profile_activity_sync.py



from accounts.models import (
    TrainingCourse,
    Presentation,
    Article,
    ExecutiveRecord
)

from django.utils.timezone import now


MODEL_MAP = {
    "training_courses": TrainingCourse,
    "presentations": Presentation,
    "articles": Article,
    "executive_records": ExecutiveRecord
}


def save_activity_to_profile(profile, activity):

    template = activity.profile_template

    if not template:
        return

    model_key = template["model"]
    data = template["data"].copy()

    # dynamic replacements
    if "date" in data and data["date"] == "{today}":
        data["date"] = now().strftime("%Y/%m/%d")

    model = MODEL_MAP.get(model_key)

    if not model:
        return

    model.objects.create(
        profile=profile,
        **data
    )
