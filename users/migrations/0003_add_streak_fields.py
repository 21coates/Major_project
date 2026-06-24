# Generated migration to add streak fields to Profile
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile_age_profile_full_name_profile_gender_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='streak_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_workout_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
