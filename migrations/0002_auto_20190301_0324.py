# Generated by Django 2.0.2 on 2019-03-01 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nattracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='allowed_subjects',
            field=models.ManyToManyField(blank=True, related_name='_user_allowed_subjects_+', to='nattracker.User'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_client',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_name='nattracker_groups', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_name='nattracker_permissions', to='auth.Permission'),
        ),
    ]
