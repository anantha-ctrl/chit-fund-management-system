from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0001_initial'),
        ('members', '0003_memberdocument_admin_notes_memberdocument_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='branches.branch'),
        ),
        migrations.AddField(
            model_name='member',
            name='nominee_id_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Nominee Aadhaar/PAN'),
        ),
        migrations.AddField(
            model_name='member',
            name='nominee_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='nominee_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='nominee_relationship',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
