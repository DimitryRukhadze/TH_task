# Generated by Django 5.0.1 on 2024-01-19 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0019_cw_adjusted_days_alter_tolerance_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tolerance',
            name='neg_tol',
            field=models.FloatField(default=0, verbose_name='Negative_adj'),
        ),
        migrations.AlterField(
            model_name='tolerance',
            name='pos_tol',
            field=models.FloatField(default=0, verbose_name='Positive adj'),
        ),
    ]
