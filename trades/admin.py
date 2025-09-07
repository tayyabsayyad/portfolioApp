# trades/admin.py
from django.contrib import admin
from django.http import HttpResponse
import csv
from django.utils.html import format_html
from .models import ActivityLog
from . import models


# --- Utility: CSV export action ---
def export_as_csv_action(description="Export selected objects as CSV",
                         fields=None, header=True):
    """
    Return an admin action that exports selected queryset to CSV.
    Usage:
        actions = [export_as_csv_action(fields=['ticker','buy_price'])]
    """

    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        field_names = fields or [f.name for f in opts.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % opts.verbose_name_plural.replace(' ', '_')
        writer = csv.writer(response)

        if header:
            writer.writerow(field_names)

        for obj in queryset:
            row = []
            for field in field_names:
                val = getattr(obj, field, '')
                # call callable if present
                if callable(val):
                    try:
                        val = val()
                    except Exception:
                        val = ''
                row.append(val)
            writer.writerow(row)
        return response

    export_as_csv.short_description = description
    return export_as_csv


# --- Inline for TradeChart ---
class TradeChartInline(admin.TabularInline):
    model = getattr(models, 'TradeChart', None)
    extra = 0
    readonly_fields = ('thumbnail', 'uploaded_at') if hasattr(models, 'TradeChart') else ()
    fields = ('image', 'caption') if not hasattr(models, 'TradeChart') else (
    'thumbnail', 'image', 'caption', 'uploaded_at')

    def thumbnail(self, obj):
        if not obj or not getattr(obj, 'image', None):
            return ""
        try:
            return format_html('<img src="{}" style="height:80px; object-fit:cover; border-radius:4px;" />',
                               obj.image.url)
        except Exception:
            return ""

    thumbnail.short_description = 'Thumb'


# --- Admin for Trade ---
try:
    Trade = models.Trade


    @admin.register(Trade)
    class TradeAdmin(admin.ModelAdmin):
        list_display = ('ticker', 'user', 'quantity', 'buy_price', 'buy_date', 'is_closed', 'sell_price', 'sell_date',
                        'realized_pnl_display')
        list_filter = ('is_closed', 'exit_reason', 'buy_date', 'sell_date')
        search_fields = ('ticker', 'buy_notes', 'sell_notes', 'user__username')
        date_hierarchy = 'buy_date'
        inlines = [TradeChartInline]
        actions = [export_as_csv_action(
            fields=['id', 'ticker', 'user', 'quantity', 'buy_price', 'buy_date', 'is_closed', 'sell_price', 'sell_date',
                    'exit_reason'])]

        readonly_fields = ('created_at',) if hasattr(Trade, 'created_at') else tuple()

        def realized_pnl_display(self, obj):
            # prefer model method `realized_pnl()` or attribute `realized_pnl`
            try:
                if hasattr(obj, 'realized_pnl') and callable(obj.realized_pnl):
                    val = obj.realized_pnl()
                else:
                    val = getattr(obj, 'realized_pnl', None)
                if val is None:
                    return "-"
                # color positive/negative
                cls = "color:green" if float(val) > 0 else "color:red" if float(val) < 0 else "color:gray"
                return format_html('<span style="{}">{}</span>', cls, val)
            except Exception:
                return "-"

        realized_pnl_display.short_description = 'Realized P&L'

except Exception:
    # if model not present, skip registration
    pass

# --- Admin for TradeChart (standalone) ---
try:
    TradeChart = models.TradeChart


    @admin.register(TradeChart)
    class TradeChartAdmin(admin.ModelAdmin):
        list_display = ('trade', 'caption', 'thumbnail', 'uploaded_at')
        search_fields = ('caption', 'trade__ticker', 'trade__user__username')
        readonly_fields = ('thumbnail',)

        def thumbnail(self, obj):
            if not obj or not getattr(obj, 'image', None):
                return ""
            try:
                return format_html('<img src="{}" style="height:80px; object-fit:cover; border-radius:4px;" />',
                                   obj.image.url)
            except Exception:
                return ""

        thumbnail.short_description = 'Thumb'
except Exception:
    pass

# --- Admin for Rules (or UserRules) ---
# Try common names used earlier: Rules or UserRules
for model_name in ('Rules', 'UserRules', 'Rule', 'UserRule'):
    if hasattr(models, model_name):
        Model = getattr(models, model_name)


        @admin.register(Model)
        class RulesAdmin(admin.ModelAdmin):
            list_display = ('title', 'user') if hasattr(Model, 'user') else ('title',)
            search_fields = ('title', 'content')
            readonly_fields = tuple()
            actions = [export_as_csv_action(fields=['id', 'title'])]


        break

# --- Fallback: register any other models not registered yet (convenience) ---
# This will register models that haven't been explicitly registered above.
from django.apps import apps

app_models = apps.get_app_config('trades').get_models()
for m in app_models:
    # if model is already registered, skip
    if m in admin.site._registry:
        continue
    try:
        admin.site.register(m)
    except admin.sites.AlreadyRegistered:
        pass
    except Exception:
        # skip models that need special admin
        pass

