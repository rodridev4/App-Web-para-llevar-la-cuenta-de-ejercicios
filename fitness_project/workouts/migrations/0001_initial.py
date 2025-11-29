from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(default='anonymous', max_length=255)),
                ('exercise_name', models.CharField(max_length=100)),
                ('sets', models.IntegerField()),
                ('reps', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'workouts',
                'ordering': ['-created_at'],
            },
        ),
    ]
