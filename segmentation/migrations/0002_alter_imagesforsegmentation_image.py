from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('segmentation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagesforsegmentation',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='client_image'),
        ),
    ]
