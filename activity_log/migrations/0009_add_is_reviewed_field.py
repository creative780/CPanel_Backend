# Generated manually for Admin Controls feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_log', '0008_merge_0005_0007'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityevent',
            name='is_reviewed',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]

