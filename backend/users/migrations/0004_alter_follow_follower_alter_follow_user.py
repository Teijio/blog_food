# Generated by Django 4.2.1 on 2023-06-06 20:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="follow",
            name="follower",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="follower",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Тот на кого подписались",
            ),
        ),
        migrations.AlterField(
            model_name="follow",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="following",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Тот кто подписывается",
            ),
        ),
    ]
