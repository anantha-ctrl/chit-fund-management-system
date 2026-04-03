from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0001_initial'),
        ('chits', '0002_chitgroup_commission_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='chitgroup',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chit_groups', to='branches.branch'),
        ),
    ]
