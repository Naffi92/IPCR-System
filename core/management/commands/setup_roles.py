from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import (
    Office, Position, Employee, RatingPeriod, Template, TemplateCategory, 
    TemplateGoal, TemplateKRA, TemplateColumn, AdjectivalMatrix, PositionCategoryWeight, 
    IPCR, IPCRRow, OPCR, DPCR, AuditTrail, Notification
)

ROLE_PERMISSIONS = {
    'HRMO': {
        'view': [Office, Position, Employee, RatingPeriod, Template, TemplateCategory, 
                 TemplateGoal, TemplateKRA, TemplateColumn, AdjectivalMatrix, PositionCategoryWeight, 
                 IPCR, IPCRRow, OPCR, DPCR, AuditTrail, Notification],
        'add': [Office, Position, Employee, RatingPeriod, Template, TemplateCategory, 
                TemplateGoal, TemplateKRA, TemplateColumn, AdjectivalMatrix, PositionCategoryWeight, 
                IPCR, IPCRRow, OPCR, DPCR, AuditTrail, Notification],
        'change': [Office, Position, Employee, RatingPeriod, Template, TemplateCategory, 
                   TemplateGoal, TemplateKRA, TemplateColumn, AdjectivalMatrix, PositionCategoryWeight, 
                   IPCR, IPCRRow, OPCR, DPCR, AuditTrail, Notification],
        'delete': [Template, TemplateCategory, TemplateGoal, TemplateKRA, TemplateColumn, 
                   AdjectivalMatrix, PositionCategoryWeight, IPCR, IPCRRow, OPCR, DPCR, Notification],
    },
    'Division Head': {
        'view': [Employee, Template, IPCR, IPCRRow, OPCR, DPCR, AuditTrail],
        'add': [AuditTrail],
        'change': [IPCR, OPCR, DPCR],
    },
    'Rater': {
        'view': [Employee, IPCR, IPCRRow, AuditTrail],
        'add': [AuditTrail],
        'change': [IPCR, IPCRRow],
    },
    'Ratee': {
        'view': [Template, IPCR, IPCRRow, AuditTrail],
        'add': [IPCRRow, AuditTrail],
        'change': [IPCRRow],
    },
    'Agency Head': {
        'view': [RatingPeriod, Office, Employee, OPCR, DPCR, IPCR, AuditTrail],
        'change': [OPCR, DPCR],
    },
}

class Command(BaseCommand):
    help = 'Create default role groups and assign permissions.'

    def handle(self, *args, **options):
        for role_name, perms in ROLE_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=role_name)
            action = 'Created' if created else 'Updated'
            group.permissions.clear()

            for action_type, models in perms.items():
                for model in models:
                    ct = ContentType.objects.get_for_model(model)
                    codename = f'{action_type}_{model._meta.model_name}'
                    try:
                        perm = Permission.objects.get(content_type=ct, codename=codename)
                        group.permissions.add(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Missing permission: {codename}'))

            self.stdout.write(self.style.SUCCESS(f'{action} group: {role_name} ({group.permissions.count()} perms)'))

        self.stdout.write(self.style.SUCCESS('Role groups setup complete.'))