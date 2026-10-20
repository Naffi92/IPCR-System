from django.contrib import admin
from .models import (
    RatingPeriod, Division, Employee,
    OPCR, OPCRTarget, DPCR, DPCRTarget,
    IPCR, IPCRTarget,
    BehavioralDimension, BehavioralRating,
    CriticalIncident, CoachingJournal,
)


@admin.register(RatingPeriod)
class RatingPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'head')
    search_fields = ('code', 'name')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'division', 'position', 'employment_status')
    list_filter = ('division', 'employment_status')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name')


class OPCRTargetInline(admin.TabularInline):
    model = OPCRTarget
    extra = 1


@admin.register(OPCR)
class OPCRAdmin(admin.ModelAdmin):
    list_display = ('office_name', 'rating_period', 'status')
    list_filter = ('status', 'rating_period')
    inlines = [OPCRTargetInline]


class DPCRTargetInline(admin.TabularInline):
    model = DPCRTarget
    extra = 1


@admin.register(DPCR)
class DPCRAdmin(admin.ModelAdmin):
    list_display = ('division', 'rating_period', 'status')
    list_filter = ('status', 'rating_period', 'division')
    inlines = [DPCRTargetInline]


class IPCRTargetInline(admin.TabularInline):
    model = IPCRTarget
    extra = 1


@admin.register(IPCR)
class IPCRAdmin(admin.ModelAdmin):
    list_display = ('employee', 'rating_period', 'status', 'main_appraiser', 'display_final_rating')
    list_filter = ('status', 'rating_period')
    search_fields = ('employee__employee_id', 'employee__user__username')
    inlines = [IPCRTargetInline]

    @admin.display(description='Final Rating')
    def display_final_rating(self, obj):
        return obj.final_rating


@admin.register(BehavioralDimension)
class BehavioralDimensionAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'is_active')
    list_filter = ('is_active',)


@admin.register(BehavioralRating)
class BehavioralRatingAdmin(admin.ModelAdmin):
    list_display = ('ipcr', 'dimension', 'rating')
    list_filter = ('dimension',)


@admin.register(CriticalIncident)
class CriticalIncidentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'incident_type', 'date_occurred', 'rating_period')
    list_filter = ('incident_type', 'rating_period')
    search_fields = ('employee__employee_id', 'description')


@admin.register(CoachingJournal)
class CoachingJournalAdmin(admin.ModelAdmin):
    list_display = ('ipcr', 'date', 'recorded_by')
    list_filter = ('date',)