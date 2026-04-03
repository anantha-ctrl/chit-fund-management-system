from django.db import migrations

def create_initial_settings(apps, schema_editor):
    SystemSetting = apps.get_model('system_settings', 'SystemSetting')
    
    settings = [
        {
            'key': 'CHIT_INTEREST_RATE',
            'value': '2.0',
            'description': 'Default monthly interest rate percentage for late payments.',
            'is_editable': True
        },
        {
            'key': 'BID_INCREMENT_STEP',
            'value': '500',
            'description': 'Minimum amount a bid must increase in an auction (₹).',
            'is_editable': True
        },
        {
            'key': 'PENALTY_GRACE_PERIOD',
            'value': '5',
            'description': 'Number of days allowed after due date before late fee applies.',
            'is_editable': True
        },
        {
            'key': 'SYSTEM_CURRENCY',
            'value': 'INR',
            'description': 'Base currency for all financial calculations.',
            'is_editable': False
        },
        {
            'key': 'ADMIN_CONTACT_EMAIL',
            'value': 'admin@chitfund.com',
            'description': 'System-wide contact email for user notifications.',
            'is_editable': True
        },
        {
            'key': 'MAX_MEMBERS_PER_CHIT',
            'value': '50',
            'description': 'Standard restriction for the number of participants in new groups.',
            'is_editable': True
        }
    ]
    
    for s in settings:
        SystemSetting.objects.get_or_create(key=s['key'], defaults=s)

class Migration(migrations.Migration):
    dependencies = [
        ('system_settings', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_settings),
    ]
