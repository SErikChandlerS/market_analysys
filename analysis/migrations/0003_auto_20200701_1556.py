# Generated by Django 3.0.7 on 2020-07-01 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0002_auto_20200701_0210'),
    ]

    operations = [
        migrations.CreateModel(
            name='cv',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField(null=True)),
                ('link', models.TextField(null=True)),
                ('age', models.IntegerField(unique=True)),
                ('salary', models.IntegerField(unique=True)),
                ('salary_in', models.TextField(null=True)),
                ('experience_years', models.TextField(null=True)),
                ('experience_months', models.TextField(null=True)),
                ('last_work', models.TextField(null=True)),
                ('sex', models.TextField(null=True)),
                ('city', models.TextField(null=True)),
                ('specialization_category', models.TextField(null=True)),
                ('specializations', models.TextField(null=True)),
                ('employment_modes', models.TextField(null=True)),
                ('schedule', models.TextField(null=True)),
                ('previous_positions', models.TextField(null=True)),
                ('key_skills', models.TextField(null=True)),
                ('education', models.TextField(null=True)),
                ('languages', models.TextField(null=True)),
            ],
            options={
                'verbose_name': 'CV',
                'verbose_name_plural': 'CVs',
            },
        ),
        migrations.AddField(
            model_name='vacancy',
            name='query',
            field=models.TextField(default='Тестировщик ПО'),
            preserve_default=False,
        ),
    ]