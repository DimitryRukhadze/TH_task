# Generated by Django 5.0.1 on 2024-01-22 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0033_cw_adjusted_hrs_alter_cw_adjusted_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='cw',
            name='adjusted_cycles',
            field=models.FloatField(default=0, verbose_name='Adjustment cycles'),
        ),
    ]
