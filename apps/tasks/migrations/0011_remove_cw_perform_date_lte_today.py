# Generated by Django 5.0.1 on 2024-01-09 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_remove_cw_perform_date_gt_today_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='cw',
            name='perform_date_lte_today',
        ),
    ]
