from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import (
    RatingPeriod, Division, Employee, OPCR, OPCRTarget,
    DPCR, DPCRTarget, IPCR, IPCRTarget,
    BehavioralDimension, BehavioralRating,
    CriticalIncident, CoachingJournal,
)


ROLE_PERMISSIONS = {
    'HRMO': {
        'view': [RatingPeriod, Division, Employee, OPCR, DPCR, IPCR,
                 BehavioralDimension, BehavioralRating,
                 CriticalIncident, CoachingJournal],
        'add': [RatingPeriod, Division, Employee, OPCR, DPCR, IPCR,
                BehavioralDimension, BehavioralRating,
                CriticalIncident, CoachingJournal],
        'change': [RatingPeriod, Division, Employee, OPCR, DPCR, IPCR,
                   BehavioralDimension, BehavioralRating,
                   CriticalIncident, CoachingJournal],
        'delete': [RatingPeriod, Division, Employee, IPCR, BehavioralDimension],
    },
    'Division Head': {
        'view': [Employee, OPCR, OPCRTarget, DPCR, DPCRTarget, IPCR,
                 IPCRTarget, CriticalIncident, CoachingJournal],
        'add': [DPCR, DPCRTarget, CriticalIncident, CoachingJournal],
        'change': [DPCR, DPCRTarget, IPCR, IPCRTarget,
                   CriticalIncident, CoachingJournal],
    },
    'Rater': {
        'view': [IPCR, IPCRTarget, BehavioralRating,
                 CriticalIncident, CoachingJournal],
        'add': [BehavioralRating, CriticalIncident, CoachingJournal],
        'change': [IPCR, IPCRTarget, BehavioralRating,
                   CriticalIncident, CoachingJournal],
    },
    'Ratee': {
        'view': [IPCR, IPCRTarget, BehavioralRating,
                 CriticalIncident, CoachingJournal],
        'add': [IPCRTarget],
        'change': [IPCRTarget],
    },
    'Agency Head': {
        'view': [RatingPeriod, Division, Employee, OPCR, OPCRTarget,
                 DPCR, DPCRTarget, IPCR, IPCRTarget],
        'change': [OPCR, OPCRTarget],
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
                        perm = Permission.objects.get(
                            content_type=ct, codename=codename
                        )
                        group.permissions.add(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f'Missing permission: {codename}'
                        ))

            self.stdout.write(self.style.SUCCESS(
                f'{action} group: {role_name} ({group.permissions.count()} perms)'
            ))

        self.stdout.write(self.style.SUCCESS('Role groups setup complete.'))