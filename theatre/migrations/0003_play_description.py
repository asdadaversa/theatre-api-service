# Generated by Django 5.0 on 2023-12-28 07:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("theatre", "0002_alter_theatrehall_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="play",
            name="description",
            field=models.TextField(
                default="Some play description. Good play, without any age restrictions"
            ),
            preserve_default=False,
        ),
    ]