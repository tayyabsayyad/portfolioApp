from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.db import models

User = get_user_model()

EXIT_REASONS = [
    ('SL', 'Stop Loss hit'),
    ('RES', 'Resistance above'),
    ('EMA', 'EMA slope decreasing'),
    ('SECT', 'Sector weak'),
    ('MAN', 'Manual'),
]


class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=20)

    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    buy_price = models.DecimalField(max_digits=12, decimal_places=4)
    buy_date = models.DateField()

    # manually entered indicators (raw text or JSON string). Use whichever you prefer.
    indicators_text = models.TextField(
        blank=True,
        help_text="Write manual indicators and checklist (e.g. 'Above 30w EMA: Yes; Mansfield: Positive; Volume OK: Yes')"
    )

    # optional: structured JSON snapshot if you prefer structure later
    indicators_json = models.JSONField(null=True, blank=True)

    # chart images you upload when buying — allow multiple with a related model
    buy_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # close fields
    is_closed = models.BooleanField(default=False)
    sell_price = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    sell_date = models.DateField(null=True, blank=True)
    exit_reason = models.CharField(max_length=8, choices=EXIT_REASONS, null=True, blank=True)
    sell_notes = models.TextField(blank=True)

    def realized_pnl(self):
        if not self.is_closed or self.sell_price is None:
            return None
        # do arithmetic carefully: (sell - buy) * qty
        return (float(self.sell_price) - float(self.buy_price)) * float(self.quantity)

    def unrealized_pnl(self, last_price):
        return (float(last_price) - float(self.buy_price)) * float(self.quantity)


class TradeChart(models.Model):
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='charts')
    image = models.ImageField(upload_to='trade_charts/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Rules(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, default='Stage Analysis Rules')
    content = models.TextField(blank=True)  # markdown or plain text
    updated_at = models.DateTimeField(auto_now=True)


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=200)
    target_type = models.CharField(max_length=100, blank=True, null=True)  # e.g. 'Trade'
    target_id = models.CharField(max_length=100, blank=True, null=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        who = self.user.username if self.user else "System"
        return f"{self.created_at:%Y-%m-%d %H:%M} — {who}: {self.action}"
