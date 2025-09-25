from django.contrib import admin
from .models import Pet

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'age', 'adopted', 'created_at')
    list_filter = ('breed', 'age', 'adopted', 'created_at')
    search_fields = ('name', 'breed', 'description')
    list_editable = ('adopted',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'breed', 'age')
        }),
        ('Details', {
            'fields': ('description', 'image')
        }),
        ('Status', {
            'fields': ('adopted',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('-created_at')
