# Generated by Django 5.0.1 on 2024-01-18 11:58

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0015_remove_task_next_due_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tolerance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Changed')),
                ('pos_adj', models.IntegerField(blank=True, null=True, verbose_name='Positive adj')),
                ('neg_adj', models.IntegerField(blank=True, null=True, verbose_name='Negative_adj')),
                ('adj_unit', models.CharField(choices=[('M', 'Months'), ('D', 'Days'), ('P', 'Percents')], max_length=1, verbose_name='Adj type')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adjustments', to='tasks.task')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
