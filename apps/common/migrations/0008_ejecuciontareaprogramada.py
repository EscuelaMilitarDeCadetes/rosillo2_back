from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_tipodocumento_es_acta_inicio_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EjecucionTareaProgramada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('ultima_fecha', models.DateField(blank=True, null=True)),
                ('ultima_ejecucion', models.DateTimeField(blank=True, null=True)),
                ('ultimo_resultado', models.TextField(blank=True, default='')),
                ('ultimo_error', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Ejecución de tarea programada',
                'verbose_name_plural': 'Ejecuciones de tareas programadas',
            },
        ),
    ]
