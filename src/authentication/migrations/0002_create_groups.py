from django.db import migrations

def create_groups(apps, schema_editor):
    # On ne peut pas importer directement le modèle Group car il pourrait avoir changé
    # On utilise apps.get_model pour récupérer la version du modèle à ce stade des migrations
    Group = apps.get_model('auth', 'Group')
    
    creators_group, created = Group.objects.get_or_create(name='creators')
    subscribers_group, created = Group.objects.get_or_create(name='subscribers')
    
    # On pourrait aussi ajouter des permissions ici si nécessaire

def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='creators').delete()
    Group.objects.filter(name='subscribers').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
