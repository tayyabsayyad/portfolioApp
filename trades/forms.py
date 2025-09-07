from django import forms
from .models import Trade, TradeChart


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = [
            'ticker',
            'quantity',
            'buy_price',
            'buy_date',
            'indicators_text',
            'buy_notes',
        ]
        widgets = {
            'ticker': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'buy_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'buy_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'indicators_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'buy_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ChartUploadForm(forms.ModelForm):
    class Meta:
        model = TradeChart
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CloseTradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = [
            'sell_price',
            'sell_date',
            'exit_reason',
            'sell_notes',
        ]
        widgets = {
            'sell_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'sell_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'exit_reason': forms.Select(attrs={'class': 'form-select'}),
            'sell_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }