# Generated by Django 3.2.12 on 2022-04-21 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_comment_comment_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment_text',
            field=models.TextField(),
        ),
    ]
