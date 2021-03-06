# Generated by Django 3.0.7 on 2020-06-30 00:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20200625_0319'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckIn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField()),
                ('retrospective', models.CharField(blank=True, max_length=65536)),
                ('number', models.IntegerField(default=1, editable=False)),
                ('complete', models.BooleanField(default=False)),
                ('experiments', models.ManyToManyField(related_name='check_ins', to='api.Issue')),
                ('lab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='check_ins', to='api.Lab')),
            ],
        ),
        migrations.AddConstraint(
            model_name='checkin',
            constraint=models.UniqueConstraint(fields=('number', 'lab'), name='check_in_unique_number_in_lab'),
        ),
        migrations.AddConstraint(
            model_name='checkin',
            constraint=models.CheckConstraint(check=models.Q(number__gte=1), name='check_in_number_gte_1'),
        ),
    ]
