# Generated by Django 4.2.9 on 2024-03-05 17:42

from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_communityactivity_activity_details_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communityactivity',
            name='activity_lead',
            field=models.CharField(blank=True, default='', help_text='Indicate who will lead to the activity (person or organization).', max_length=100),
        ),
        migrations.AlterField(
            model_name='communityactivity',
            name='completedby_quarter',
            field=models.CharField(blank=True, choices=[('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4'), ('N/A', 'N/A')], max_length=3),
        ),
        migrations.AlterField(
            model_name='communityactivity',
            name='completedby_year',
            field=models.CharField(blank=True, choices=[('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('N/A', 'N/A')], max_length=4),
        ),
        migrations.AlterField(
            model_name='communityactivity',
            name='related_objective',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='related_goal', chained_model_field='goal', on_delete=django.db.models.deletion.CASCADE, to='core.objective'),
        ),
        migrations.AlterField(
            model_name='communityactivity',
            name='related_strategy',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='related_objective', chained_model_field='objective', on_delete=django.db.models.deletion.CASCADE, to='core.strategy'),
        ),
        migrations.AlterField(
            model_name='strategyactivity',
            name='activity_lead',
            field=models.CharField(blank=True, default='', help_text='Indicate who will lead the activity (person, organization, or team).', max_length=100),
        ),
        migrations.AlterField(
            model_name='strategyactivity',
            name='completedby_quarter',
            field=models.CharField(choices=[('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4'), ('N/A', 'N/A')], max_length=3),
        ),
        migrations.AlterField(
            model_name='strategyactivity',
            name='completedby_year',
            field=models.CharField(choices=[('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('N/A', 'N/A')], max_length=4),
        ),
    ]
