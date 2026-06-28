# event_hub/management/commands/import_events.py


import json
from pathlib import Path

from django.core.management.base import BaseCommand
from event_hub.models import Event


class Command(BaseCommand):
    help = 'Import resume_builder_events from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True)

    def handle(self, *args, **options):
        file_path = Path(options['file'])

        if not file_path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)

        events = data.get('resume_builder_events', [])
        created = 0
        updated = 0

        for item in events:
            quick_info = item.get('quick_info', {})
            quick_summary_card = item.get('quick_summary_card', {})
            full_intro = item.get('full_introduction', {})

            _, is_created = Event.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'title': item.get('title', ''),
                    'section': item.get('section', ''),
                    'short_description': item.get('short_description', ''),
                    'compiler': quick_info.get('compiler', ''),
                    'audience': quick_info.get('audience', []),
                    'goal': quick_info.get('goal', ''),
                    'resume_impact': quick_info.get('resume_impact', ''),
                    'activity_type': quick_info.get('activity_type', ''),
                    'activity_level': quick_summary_card.get('activity_level', ''),
                    'difficulty': quick_summary_card.get('difficulty', ''),
                    'main_advantage': quick_summary_card.get('main_advantage', ''),
                    'suitable_for': quick_summary_card.get('suitable_for', ''),
                    'required_time': quick_summary_card.get('required_time', ''),
                    'intro': full_intro.get('intro', ''),
                    'research_audiences': full_intro.get('research_audiences', []),
                    'skills_learned': full_intro.get('skills_learned', []),
                    'completion_steps': item.get('completion_steps', []),
                    'terms_and_conditions': item.get('terms_and_conditions', []),
                    'benefits': item.get('benefits', {}),
                    'common_mistakes': item.get('common_mistakes', []),
                    'practical_recommendations': item.get('practical_recommendations', []),
                    'similar_opportunities': item.get('similar_opportunities', []),
                    'inline_cta_buttons': item.get('inline_cta_buttons', []),
                    'page_cta_buttons': item.get('page_cta_buttons', []),
                }
            )

            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Imported. Created: {created}, Updated: {updated}'))
