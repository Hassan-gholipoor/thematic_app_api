# Generated by Django 3.2.12 on 2022-04-16 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_category_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=155)),
                ('description', models.TextField()),
                ('slug', models.SlugField(max_length=155, unique=True)),
                ('publish_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('categories', models.ManyToManyField(related_name='articles', to='core.Category')),
            ],
        ),
    ]
