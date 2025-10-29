from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Section, ProductivityEntry

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Role & Sections', {'fields':('role','sections')}),
    )
    list_display = ('username','email','role','is_staff')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name','description')

@admin.register(ProductivityEntry)
class ProductivityEntryAdmin(admin.ModelAdmin):
    list_display = (
        'lead', 'section', 'date', 'bundle_opening', 'sorting', 'loading',
        'sticker', 'scanning', 'put_away', 'picking', 'remarks', 'created_at'
    )
    list_filter = ('section', 'date', 'lead')
    search_fields = ('lead__username', 'remarks')

