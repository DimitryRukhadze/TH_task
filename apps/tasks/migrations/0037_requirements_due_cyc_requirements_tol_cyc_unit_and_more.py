# Generated by Django 5.0.1 on 2024-02-07 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0036_cw_perform_hrs'),
    ]

    operations = [
        migrations.AddField(
            model_name='requirements',
            name='due_cyc',
            field=models.IntegerField(blank=True, null=True, verbose_name='Due cycles'),
        ),
        migrations.AddField(
            model_name='requirements',
            name='tol_cyc_unit',
            field=models.CharField(blank=True, choices=[('C', 'Cycles'), ('P', 'Percents')], max_length=1, null=True, verbose_name='CYC tol unit'),
        ),
        migrations.AddField(
            model_name='requirements',
            name='tol_neg_cyc',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='CYC negative'),
        ),
        migrations.AddField(
            model_name='requirements',
            name='tol_pos_cyc',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='CYC positive'),
        ),
        migrations.AlterField(
            model_name='requirements',
            name='due_hrs',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Due hours'),
        ),
        migrations.AlterField(
            model_name='requirements',
            name='tol_hrs_unit',
            field=models.CharField(blank=True, choices=[('H', 'Hours'), ('P', 'Percents')], max_length=1, null=True, verbose_name='HRS tol unit'),
        ),
    ]