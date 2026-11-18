from django.contrib import admin
from .models import (
    Office, Position, Employee, RatingPeriod, Template, TemplateCategory, 
    TemplateGoal, TemplateKRA, TemplateColumn, AdjectivalMatrix, PositionCategoryWeight, 
    IPCR, IPCRRow, OPCR, DPCR, AuditTrail, Notification
)

@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'head')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'office', 'position')

@admin.register(RatingPeriod)
class RatingPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'target_start', 'target_end')

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'applicable_to')

@admin.register(TemplateCategory)
class TemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'default_weight') # FIXED

@admin.register(TemplateGoal)
class TemplateGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

@admin.register(TemplateKRA)
class TemplateKRAAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal') # FIXED

@admin.register(TemplateColumn)
class TemplateColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'phase_availability', 'is_required')

@admin.register(PositionCategoryWeight)
class PositionCategoryWeightAdmin(admin.ModelAdmin):
    list_display = ('position', 'category', 'weight_percentage')

@admin.register(AdjectivalMatrix)
class AdjectivalMatrixAdmin(admin.ModelAdmin):
    list_display = ('label', 'template', 'min_score', 'max_score')

@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'document_type')
    readonly_fields = ('timestamp',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')

admin.site.register(IPCR)
admin.site.register(IPCRRow)
admin.site.register(OPCR)
admin.site.register(DPCR)