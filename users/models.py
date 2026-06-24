from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

@receiver(post_save, sender=User)
def ensure_profile(sender, instance: User, created, **kwargs):
    profile, made = Profile.objects.get_or_create(user=instance)
    if (made or not profile.nickname):
        default_base = instance.username or (instance.email.split("@")[0] if instance.email else "user")
        profile.nickname = _unique_nickname(default_base)
        profile.save(update_fields=["nickname"])

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    nickname = models.CharField(max_length=30, unique=True)
    # Added fields for user profile details used in the create-profile screen
    full_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHER = 'O'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height_cm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # XP / Leveling system
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    # Streak tracking
    streak_count = models.IntegerField(default=0)
    last_workout_date = models.DateField(blank=True, null=True)

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def __str__(self):
        return self.user.username

    @staticmethod
    def xp_for_next_level(level:int) -> int:
        """Define XP curve. Using quadratic growth: 100 * level^2"""
        return 100 * (level ** 2)

    def add_xp(self, amount:int) -> int:
        """Add xp to profile, handle level ups and return number of levels gained."""
        if amount <= 0:
            return 0
        self.xp = int(self.xp) + int(amount)
        levels_gained = 0
        # loop in case XP overshoots multiple levels
        while self.xp >= Profile.xp_for_next_level(self.level):
            required = Profile.xp_for_next_level(self.level)
            self.xp -= required
            self.level += 1
            levels_gained += 1
        self.save(update_fields=['xp','level'])
        return levels_gained

    @property
    def xp_to_next(self) -> int:
        """XP still required to reach next level."""
        req = Profile.xp_for_next_level(self.level)
        return max(0, req - int(self.xp))

    @property
    def xp_percent(self) -> int:
        """Percent progress toward next level (0-100)."""
        req = Profile.xp_for_next_level(self.level)
        if req <= 0:
            return 0
        return min(100, int((int(self.xp) / req) * 100))

    @property
    def xp_next_total(self) -> int:
        """Total XP required for the current level (useful in templates)."""
        return Profile.xp_for_next_level(self.level)

    @property
    def xp_fraction(self) -> str:
        """Return a 'current/required' formatted string for templates."""
        req = Profile.xp_for_next_level(self.level)
        return f"{int(self.xp)} / {req}"


def _unique_nickname(base: str) -> str:
    base = (base or "user").strip() or "user"
    candidate = base
    i = 1
    from django.db.models import Q
    while Profile.objects.filter(Q(nickname__iexact=candidate)).exists():
        i += 1
        candidate = f"{base}-{i}"
    return candidate