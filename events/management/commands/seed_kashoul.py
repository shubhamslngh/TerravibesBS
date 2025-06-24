from django.core.management.base import BaseCommand
from events.models import Mood, HealingIntent, HealingActivity, EventPackage, Content


class Command(BaseCommand):
    help = "Seed database with Kashoul Retreat, moods, intent, and activities"

    def handle(self, *args, **kwargs):
        # Step 1: Create Moods
        mood_names = [
            "Overwhelmed",
            "Exhausted",
            "Emotionally Numb",
            "Spiritually Disconnected",
        ]
        moods = []
        for name in mood_names:
            mood, _ = Mood.objects.get_or_create(
                name=name, defaults={"description": f"Mood: {name}"}
            )
            moods.append(mood)
        self.stdout.write(self.style.SUCCESS(f"Created {len(moods)} moods."))

        # Step 2: Create Healing Intent
        intent, _ = HealingIntent.objects.get_or_create(
            name="Solitude & Reflection",
            defaults={
                "description": "A deeply restorative experience designed for individuals who need space to disconnect, reflect, and renew their inner calm.",
                "recommended_duration": 5,
                "emoji": "🌲",
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Healing Intent: {intent.name}"))

        # Step 3: Create Healing Activities
        activities = [
            {
                "title": "Guided Forest Meditation",
                "description": "A deep listening exercise amidst nature, guided by a local mindfulness practitioner.",
                "activity_type": "meditation",
            },
            {
                "title": "Silent Journaling by the Stream",
                "description": "Write without filters. Let your thoughts flow as water does.",
                "activity_type": "journaling",
            },
            {
                "title": "Sound Healing at Sunset",
                "description": "Immerse yourself in Tibetan singing bowls and ancient healing frequencies.",
                "activity_type": "sound_therapy",
            },
        ]

        for act in activities:
            obj, _ = HealingActivity.objects.get_or_create(
                title=act["title"],
                intent=intent,
                defaults={
                    "description": act["description"],
                    "activity_type": act["activity_type"],
                },
            )
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(activities)} healing activities.")
        )

        # Step 4: Create Kashoul Event Package
        package, _ = EventPackage.objects.get_or_create(
            title="Kashoul Silent Nature Retreat",
            defaults={
                "description": "An immersive 5-day retreat in the Himalayas where you reconnect with yourself through silence, stillness, and nature.",
                "price": 32000.00,
                "services": {
                    "location": "Dharamshala, Himachal Pradesh",
                    "stay": "Eco-friendly cabins in secluded forest",
                    "food": "Ayurvedic sattvic meals, herbal teas",
                    "activities": [
                        "guided forest meditation",
                        "silent journaling",
                        "sound healing",
                        "digital detox",
                    ],
                    "wellness": "Evening herbal bath & chakra cleansing",
                    "customizations": [
                        "private therapist call",
                        "1-on-1 mindfulness session",
                        "detox box",
                    ],
                },
            },
        )

        # Link healing intent
        package.healing_intents.add(intent)

        # (Optional) Add moods
        for mood in moods:
            package.moods.add(mood)

        self.stdout.write(
            self.style.SUCCESS(f"Kashoul Package: {package.title} created and linked.")
        )
