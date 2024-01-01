# Generated by Django 5.0 on 2024-01-01 21:22

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cw',
            name='performed',
        ),
        migrations.AddField(
            model_name='cw',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Создано'),
        ),
        migrations.AddField(
            model_name='cw',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Deleted'),
        ),
        migrations.AddField(
            model_name='cw',
            name='perform_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Была выполнена'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cw',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Изменено'),
        ),
        migrations.AddField(
            model_name='task',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Создано'),
        ),
        migrations.AddField(
            model_name='task',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Deleted'),
        ),
        migrations.AddField(
            model_name='task',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Изменено'),
        ),
        migrations.AlterField(
            model_name='cw',
            name='next_due_date',
            field=models.DateField(verbose_name='Следующее выполнение'),
        ),
        migrations.AlterField(
            model_name='cw',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complied_with', to='tasks.task'),
        ),
        migrations.AlterField(
            model_name='task',
            name='code',
            field=models.CharField(max_length=50, verbose_name='Код задачи'),
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='task',
            name='due_months',
            field=models.IntegerField(null=True, verbose_name='Месяцев до повтора задачи'),
        ),
        migrations.AlterField(
            model_name='task',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
