# Generated by Django 4.2.9 on 2024-02-21 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipe_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='desc',
            field=models.TextField(default='No description provided.', null=True),
        ),
    ]
