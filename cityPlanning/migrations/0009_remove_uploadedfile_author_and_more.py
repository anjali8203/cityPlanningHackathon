# Generated by Django 4.2.16 on 2025-02-23 05:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cityPlanning', "0008_remove_vote_hacky_sol"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="uploadedfile",
            name="author",
        ),
        migrations.RemoveField(
            model_name="uploadedfile",
            name="project",
        ),
        migrations.DeleteModel(
            name="JoinRequest",
        ),
        migrations.DeleteModel(
            name="UploadedFile",
        ),
    ]
