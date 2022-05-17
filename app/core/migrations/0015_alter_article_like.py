# Generated by Django 3.2.13 on 2022-05-16 14:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_article_like'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='like',
            field=models.ManyToManyField(blank=True, related_name='likes', to=settings.AUTH_USER_MODEL),
        ),
    ]