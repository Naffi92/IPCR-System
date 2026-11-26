from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone

# ==========================================
# 1. HIERARCHY & USER MANAGEMENT
# ==========================================

class Office(models.Model):
    """Represents Colleges, Offices, and Departments in a nested hierarchy."""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_offices')
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_offices')

    def __str__(self):
        return f"{self.code} - {self.name}"

class Position(models.Model):
    """Represents Faculty and Staff positions with specific weight allocations."""
    TYPE_CHOICES = [('Faculty', 'Faculty'), ('Staff', 'Staff')]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    def __str__(self):
        return f"{self.name} ({self.type})"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    employee_id = models.CharField(max_length=30, unique=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, related_name='employees')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='employees')
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    e_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    digital_hash = models.CharField(max_length=64, blank=True, null=True, help_text="Auto-generated SHA-256 hash")

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username}"

# ==========================================
# 2. RATING PERIODS & TEMPLATES
# ==========================================

class RatingPeriod(models.Model):
    name = models.CharField(max_length=100)
    target_start = models.DateField()
    target_end = models.DateField()
    midyear_date = models.DateField(null=True, blank=True)
    accomplishment_start = models.DateField()
    accomplishment_end = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Template(models.Model):
    EVALUATION_TYPES = [
        ('Faculty', 'Faculty (Position Matrix)'),
        ('Staff', 'Staff (80/20 Split)')
    ]
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPES, default='Faculty') # <-- ADD THIS
    applicable_to = models.CharField(max_length=20, choices=[('Faculty', 'Faculty'), ('Staff', 'Staff')])
    staff_split_percentage = models.PositiveIntegerField(default=80, help_text="The percentage for MFOs (e.g., 80 for 80/20 split).")

    def __str__(self):
        return f"{self.name} ({self.evaluation_type})"


class TemplateCategory(models.Model):
    """The math buckets: Instruction, Research, GOALS, CORE, SUPPORT"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100) 
    default_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Default weight (e.g., 55.00). Overridden by Position if applicable.")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.default_weight}%)"

class TemplateGoal(models.Model):
    """Visual headers under a category (e.g., Goal 1: Strengthen Quality)"""
    category = models.ForeignKey(TemplateCategory, on_delete=models.CASCADE, related_name='goals', null=True, blank=True) # <-- ADDED null=True, blank=True
    name = models.CharField(max_length=250)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Under {self.category.name if self.category else 'No Category'})"


class TemplateKRA(models.Model):
    """Key Result Areas under a Goal"""
    goal = models.ForeignKey(TemplateGoal, on_delete=models.CASCADE, related_name='kras', null=True, blank=True) # <-- ADDED null=True, blank=True
    name = models.CharField(max_length=250) 
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Under {self.goal.name if self.goal else 'No Goal'})"

class TemplateColumn(models.Model):
    PHASE_CHOICES = [
        ('Target', 'Target Phase Only'),
        ('Accomplishment', 'Accomplishment Phase Only'),
        ('Both', 'Both Phases')
    ]
    DATA_TYPE_CHOICES = [
        ('Text', 'Text / Paragraph'),
        ('Rating', 'Rating (1-5 Numerical)'),
        ('Number', 'Number (Other)')
    ]
    INPUT_BY_CHOICES = [
        ('Ratee', 'Ratee (Employee)'),
        ('Rater', 'Rater (Supervisor/Head)')
    ]
    template = models.ForeignKey('Template', on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=100) 
    phase_availability = models.CharField(max_length=20, choices=PHASE_CHOICES, default='Both')
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, default='Text')
    input_by_role = models.CharField(max_length=20, choices=INPUT_BY_CHOICES, default='Ratee') # <-- ADDED
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.input_by_role} | {self.data_type})"

class PositionCategoryWeight(models.Model):
    """Overrides the default weight for specific positions (e.g., Professor gets 25% in Instruction)"""
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='category_weights')
    category = models.ForeignKey(TemplateCategory, on_delete=models.CASCADE, related_name='position_weights')
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ('position', 'category')

    def __str__(self):
        return f"{self.position.name} - {self.category.name}: {self.weight_percentage}%"

class AdjectivalMatrix(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='adjectival_ratings')
    min_score = models.DecimalField(max_digits=3, decimal_places=2)
    max_score = models.DecimalField(max_digits=3, decimal_places=2)
    label = models.CharField(max_length=50) 

    def __str__(self):
        return f"{self.label} ({self.min_score} - {self.max_score})"

# ==========================================
# 3. THE DOCUMENTS (OPCR, DPCR, IPCR)
# ==========================================

class BaseDocument(models.Model):
    """Abstract base model for OPCR, DPCR, and IPCR to share state and audit fields."""
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Target Submitted', 'Target Submitted'),
        ('Target Approved', 'Target Approved'),
        ('Mid-Year Review', 'Mid-Year Review'),
        ('Accomplishment Submitted', 'Accomplishment Submitted'),
        ('Rater Scored', 'Rater Scored'),
        ('Final Approved', 'Final Approved'),
        ('Returned', 'Returned for Revision')
    ]
    rating_period = models.ForeignKey(RatingPeriod, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class IPCR(BaseDocument):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='ipcrs')
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True) # <-- ADDED
    
    # Manual Assignments (Validated by System)
    target_approver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='target_approvals')
    assessed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    final_rater = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='final_ratings')

class IPCRRow(models.Model):
    """Represents a single row of output/KPI in the IPCR"""
    ipcr = models.ForeignKey(IPCR, on_delete=models.CASCADE, related_name='rows')
    kra = models.ForeignKey(TemplateKRA, on_delete=models.SET_NULL, null=True)
    dynamic_data = models.JSONField(default=dict) # Stores column values like {"MFO": "Train teachers", "Actual": "Trained 10"}
    created_at = models.DateTimeField(default=timezone.now) # <-- ADD THIS
    
    # Ratings (Filled during Accomplishment Phase)
    q_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    e_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    t_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    remarks = models.TextField(blank=True)

    @property
    def average_rating(self):
        ratings = [r for r in [self.q_rating, self.e_rating, self.t_rating] if r is not None]
        return sum(ratings) / len(ratings) if ratings else None

class OPCR(BaseDocument):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='opcrs')
    # Targets are stored dynamically just like IPCR

class DPCR(BaseDocument):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='dpcrs')

# ==========================================
# 4. SYSTEM LOGS & FEATURES
# ==========================================

class AuditTrail(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50)
    document_id = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.user.username}: {self.message[:30]}"