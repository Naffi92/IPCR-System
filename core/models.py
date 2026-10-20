from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class RatingPeriod(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    target_setting_deadline = models.DateField()
    appraisal_deadline = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Division(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    head = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='headed_divisions'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} — {self.name}"


class Employee(models.Model):
    EMPLOYMENT_STATUS = [
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
        ('casual', 'Casual'),
        ('contractual', 'Contractual'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    employee_id = models.CharField(max_length=30, unique=True)
    division = models.ForeignKey(
        Division, on_delete=models.SET_NULL, null=True,
        related_name='employees'
    )
    position = models.CharField(max_length=200)
    employment_status = models.CharField(
        max_length=20, choices=EMPLOYMENT_STATUS, default='permanent'
    )
    supervisor = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subordinates'
    )
    date_hired = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee_id} — {self.user.get_full_name() or self.user.username}"


class OPCR(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
    ]

    rating_period = models.ForeignKey(
        RatingPeriod, on_delete=models.CASCADE, related_name='opcrs'
    )
    office_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_opcrs'
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_opcrs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating_period__start_date']

    def __str__(self):
        return f"OPCR — {self.office_name} ({self.rating_period.name})"


class OPCRTarget(models.Model):
    opcr = models.ForeignKey(OPCR, on_delete=models.CASCADE, related_name='targets')
    mfo = models.CharField(max_length=500, help_text='Major Final Output')
    success_indicator = models.TextField()
    weight = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))]
    )

    def __str__(self):
        return f"{self.mfo} ({self.weight}%)"


class DPCR(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
    ]

    rating_period = models.ForeignKey(
        RatingPeriod, on_delete=models.CASCADE, related_name='dpcrs'
    )
    division = models.ForeignKey(
        Division, on_delete=models.CASCADE, related_name='dpcrs'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_dpcrs'
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_dpcrs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DPCR — {self.division.name} ({self.rating_period.name})"


class DPCRTarget(models.Model):
    dpcr = models.ForeignKey(DPCR, on_delete=models.CASCADE, related_name='targets')
    opcr_target = models.ForeignKey(
        OPCRTarget, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='dpcr_targets'
    )
    output = models.CharField(max_length=500)
    success_indicator = models.TextField()
    weight = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))]
    )

    def __str__(self):
        return f"{self.output} ({self.weight}%)"


class IPCR(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('returned', 'Returned for Revision'),
        ('appraised', 'Appraised (Scored)'),
    ]

    rating_period = models.ForeignKey(
        RatingPeriod, on_delete=models.CASCADE, related_name='ipcrs'
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='ipcrs'
    )
    main_appraiser = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='appraised_ipcrs'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['rating_period', 'employee']
        ordering = ['-rating_period__start_date']

    def __str__(self):
        return f"IPCR — {self.employee} ({self.rating_period.name})"

    @property
    def final_rating(self):
        targets = self.targets.all()
        if not targets:
            return None
        total_weight = sum(t.weight for t in targets)
        if total_weight == 0:
            return None
        weighted_sum = sum((t.average_rating or 0) * t.weight for t in targets)
        return round(weighted_sum / total_weight, 2)


class IPCRTarget(models.Model):
    ipcr = models.ForeignKey(IPCR, on_delete=models.CASCADE, related_name='targets')
    dpcr_target = models.ForeignKey(
        DPCRTarget, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ipcr_targets'
    )
    output = models.CharField(max_length=500)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))]
    )

    quality_target = models.TextField(blank=True)
    efficiency_target = models.TextField(blank=True)
    timeliness_target = models.TextField(blank=True)

    quality_actual = models.TextField(blank=True)
    efficiency_actual = models.TextField(blank=True)
    timeliness_actual = models.TextField(blank=True)

    quality_rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    efficiency_rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    timeliness_rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return self.output

    @property
    def average_rating(self):
        ratings = [
            r for r in [
                self.quality_rating, self.efficiency_rating, self.timeliness_rating
            ] if r is not None
        ]
        return sum(ratings) / len(ratings) if ratings else None


class BehavioralDimension(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class BehavioralRating(models.Model):
    ipcr = models.ForeignKey(IPCR, on_delete=models.CASCADE, related_name='behavioral_ratings')
    dimension = models.ForeignKey(BehavioralDimension, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ['ipcr', 'dimension']

    def __str__(self):
        return f"{self.dimension.name}: {self.rating}"


class CriticalIncident(models.Model):
    INCIDENT_TYPE = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='critical_incidents'
    )
    rating_period = models.ForeignKey(
        RatingPeriod, on_delete=models.CASCADE, related_name='critical_incidents'
    )
    incident_type = models.CharField(max_length=10, choices=INCIDENT_TYPE)
    description = models.TextField()
    date_occurred = models.DateField()
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='recorded_incidents'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_occurred']

    def __str__(self):
        return f"{self.incident_type} — {self.employee} ({self.date_occurred})"


class CoachingJournal(models.Model):
    ipcr = models.ForeignKey(IPCR, on_delete=models.CASCADE, related_name='coaching_entries')
    date = models.DateField()
    discussion = models.TextField()
    action_plan = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='coaching_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Coaching — {self.ipcr.employee} ({self.date})"