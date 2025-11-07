from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from django.utils.text import slugify


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    ROLE_CHOICES = [
        ("client", "Client"),
        ("vendor", "Vendor"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="client")

    def __str__(self):
        return f"{self.username} ({self.role})"


class Vendor(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    portfolio = models.TextField(blank=True)
    availability = models.JSONField(blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class Content(models.Model):
    CONTENT_TYPES = [
        ("blog", "Blog Post"),
        ("case_study", "Case Study"),
        ("gallery", "Gallery Image"),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,  blank=True, unique=True) 
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES)
    body = models.TextField(blank=True)
    media_file = models.FileField(upload_to="uploads/")
    publish_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Content.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.content_type})"


class Mood(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color_palette = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


class HealingIntent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    recommended_duration = models.IntegerField(default=3)  # Days
    emoji = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return self.name


class HealingActivity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    activity_type = models.CharField(
        max_length=50
    )  # e.g., yoga, journaling, cold plunge
    intent = models.ForeignKey(HealingIntent, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class EventPackage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    services = models.JSONField(help_text="List of included services and details")
    images = models.ManyToManyField(Content, blank=True)
    is_active = models.BooleanField(default=True)
    moods = models.ManyToManyField(Mood, related_name='event_packages')
    healing_intents = models.ManyToManyField(HealingIntent, related_name='event_packages')

    def __str__(self):
        return self.title


class Guide(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="guides/", blank=True, null=True)
    expertise = models.CharField(
        max_length=100, help_text="e.g. Yoga, Mindfulness, Adventure Travel"
    )
    packages = models.ManyToManyField(
        "EventPackage",
        related_name="guides",
        blank=True,
        help_text="Which experiences this guide leads",
    )
    def __str__(self):
        return self.name


class Inquiry(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("consultation_scheduled", "Consultation Scheduled"),
        ("converted", "Converted"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    event_date = models.DateField()
    event_type = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inquiry {self.id} - {self.name}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    inquiry = models.OneToOneField(
        Inquiry, on_delete=models.SET_NULL, null=True, blank=True
    )
    package = models.ForeignKey(EventPackage, on_delete=models.SET_NULL, null=True)

    # ✅ Use date range instead of datetime
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    gender = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    name = models.CharField(max_length=255)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.id} - {self.first_name} {self.last_name}"
