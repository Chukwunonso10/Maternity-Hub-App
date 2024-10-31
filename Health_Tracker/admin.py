from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserSymptoms,AnalysisResults,DailyCheckup,CustomUser

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('first_name', 'last_name','phoneNumber','email','is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    search_fields = ('email','first_name',)
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phoneNumber',)}),
    )


admin.site.register(UserSymptoms)
admin.site.register(AnalysisResults)
admin.site.register(DailyCheckup)
admin.site.register(CustomUser, CustomUserAdmin)