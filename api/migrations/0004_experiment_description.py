# Generated by Django 3.0.7 on 2020-06-25 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200622_0404'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='description',
            field=models.CharField(default='', max_length=65536),
            preserve_default=False,
        ),
    ]
