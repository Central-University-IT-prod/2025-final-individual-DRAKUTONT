# Generated by Django 5.1.6 on 2025-02-21 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisers', '0004_campaign_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertiser',
            name='name',
            field=models.CharField(),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='ad_text',
            field=models.CharField(),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='ad_title',
            field=models.CharField(),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
