# Generated by Django 3.2.9 on 2022-01-06 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20220101_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatar'),
        ),
        migrations.AddField(
            model_name='profile',
            name='bio',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]