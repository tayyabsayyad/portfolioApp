# trades/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import F
from .forms import TradeForm, ChartUploadForm, CloseTradeForm
import csv
import datetime
# trades/views.py (replace the existing trade_list view)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from .models import Trade
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import math
from .utils import log_activity
from django.contrib.auth.decorators import login_required

# Optional: yfinance for live pricing. If not installed, the API will return last_price = None.
try:
    import yfinance as yf
except Exception:
    yf = None

from .models import Trade, TradeChart, Rules
from .forms import TradeForm, ChartUploadForm


@login_required
def add_trade(request):
    """Create a new buy trade and optionally upload charts."""
    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.user = request.user
            trade.save()
            log_activity(request.user, f"Added trade {trade.ticker}", target=trade,
                         details=f"qty={trade.quantity} buy={trade.buy_price}")
            # handle multiple file uploads named 'charts'
            for f in request.FILES.getlist('charts'):
                TradeChart.objects.create(trade=trade, image=f)
                log_activity(request.user, f"Uploaded chart for {trade.ticker}", target=trade, details=f.name)
            messages.success(request, f"Trade for {trade.ticker} added.")
            return redirect('trade_detail', trade.id)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = TradeForm(initial={'buy_date': datetime.date.today()})
    chart_form = ChartUploadForm()

    # <-- add this: get recent open trades for right-column display
    recent_open_trades = Trade.objects.filter(user=request.user, is_closed=False).order_by('-buy_date')[:5]

    return render(request, 'trades/add_trade.html', {
        'form': form,
        'chart_form': chart_form,
        'recent_open_trades': recent_open_trades,
    })


@login_required
def trade_detail(request, trade_id):
    """Show trade detail, charts, and a small form to upload more charts or notes."""
    trade = get_object_or_404(Trade, id=trade_id, user=request.user)
    chart_form = ChartUploadForm()
    if request.method == 'POST' and 'upload_chart' in request.POST:
        # handle chart upload from detail page
        chart_form = ChartUploadForm(request.POST, request.FILES)
        if chart_form.is_valid():
            chart = chart_form.save(commit=False)
            chart.trade = trade
            chart.save()
            messages.success(request, "Chart uploaded.")
            return redirect('trade_detail', trade.id)
    return render(request, 'trades/trade_detail.html', {'trade': trade, 'chart_form': chart_form})


@login_required
def close_trade(request, trade_id):
    """Close an open trade (sell). Uses CloseTradeForm for validation and display."""
    trade = get_object_or_404(Trade, id=trade_id, user=request.user)

    if request.method == 'POST':
        form = CloseTradeForm(request.POST, instance=trade)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.is_closed = True
            # if sell_date not provided, set today
            if not trade.sell_date:
                trade.sell_date = datetime.date.today()
            trade.save()
            log_activity(request.user, f"Closed trade {trade.ticker}", target=trade,
                         details=f"sell={trade.sell_price} exit={trade.exit_reason}")
            # upload sell charts (input name: 'sell_charts')
            for f in request.FILES.getlist('sell_charts'):
                TradeChart.objects.create(trade=trade, image=f, caption="Sell chart")

            messages.success(request, f"Trade {trade.ticker} closed.")
            return redirect('trade_detail', trade.id)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        # prefill form with existing sell fields (if any)
        form = CloseTradeForm(instance=trade)

    return render(request, 'trades/close_trade.html', {'trade': trade, 'form': form})


@login_required
def trade_list(request):
    """
    List trades:
      - open_trades: all open positions (no pagination)
      - closed_trades: filtered + paginated
    Filters via GET params:
      - q: ticker (substring, case-insensitive)
      - start_date: ISO date (YYYY-MM-DD) for sell_date >= start_date
      - end_date: ISO date for sell_date <= end_date
      - exit_reason: exact exit reason code (SL, RES, EMA, SECT, MAN)
      - page: page number for pagination
    """
    user = request.user
    open_trades = Trade.objects.filter(user=user, is_closed=False).order_by('-buy_date')

    # Base closed queryset
    closed_qs = Trade.objects.filter(user=user, is_closed=True).order_by('-sell_date')

    # Apply filters
    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()
    exit_reason = request.GET.get('exit_reason', '').strip()

    if q:
        closed_qs = closed_qs.filter(ticker__icontains=q)

    if exit_reason:
        closed_qs = closed_qs.filter(exit_reason=exit_reason)

    # date filtering (sell_date)
    if start_date:
        try:
            closed_qs = closed_qs.filter(sell_date__gte=start_date)
        except Exception:
            pass
    if end_date:
        try:
            closed_qs = closed_qs.filter(sell_date__lte=end_date)
        except Exception:
            pass

    # Pagination for closed trades
    page = request.GET.get('page', 1)
    per_page = 10  # change as you like
    paginator = Paginator(closed_qs, per_page)
    try:
        closed_page = paginator.page(page)
    except PageNotAnInteger:
        closed_page = paginator.page(1)
    except EmptyPage:
        closed_page = paginator.page(paginator.num_pages)

    context = {
        'open_trades': open_trades,
        'closed_trades': closed_page,  # this is a Page object
        'paginator': paginator,
        'filter_q': q,
        'filter_start_date': start_date,
        'filter_end_date': end_date,
        'filter_exit_reason': exit_reason,
    }
    return render(request, 'trades/trade_list.html', context)


@login_required
def dashboard(request):
    """Dashboard page — will fetch positions via portfolio_value_api (JS) or render an initial snapshot."""
    open_trades = Trade.objects.filter(user=request.user, is_closed=False)
    # Optionally compute a quick static snapshot using cached or live values
    # For simplicity: do not call yfinance here; frontend can call the API endpoint to update.
    return render(request, 'trades/dashboard.html', {
        'open_trades': open_trades,
    })


@login_required
def portfolio_value_api(request):
    """
    Returns JSON with:
      - positions: list of tickers aggregated by average buy price
      - total_value, total_cost, total_unrealized, total_gain, total_gain_pct
    """
    trades = Trade.objects.filter(user=request.user, is_closed=False)

    # Group open trades by ticker (case-insensitive)
    from collections import defaultdict
    ticker_groups = defaultdict(list)
    for tr in trades:
        ticker_groups[tr.ticker.upper()].append(tr)

    tickers = list(ticker_groups.keys())

    # Fetch last prices
    prices = {}
    if 'yf' in globals() and yf and tickers:
        for t in tickers:
            try:
                tk = yf.Ticker(t)
                last = None
                fast = getattr(tk, 'fast_info', None)
                if fast:
                    last = getattr(fast, 'last_price', None)
                if not last:
                    hist = tk.history(period='1d', interval='1m', progress=False)
                    if not hist.empty:
                        last = float(hist['Close'].iloc[-1])
                prices[t] = float(last) if last is not None else None
            except Exception:
                prices[t] = None
    else:
        for t in tickers:
            prices[t] = None

    positions = []
    total_value = 0.0
    total_cost = 0.0
    total_unrealized = 0.0

    # --- aggregate by ticker ---
    for ticker, group in ticker_groups.items():
        total_qty = sum(float(t.quantity) for t in group)
        total_buy_cost = sum(float(t.quantity) * float(t.buy_price) for t in group)
        avg_buy_price = total_buy_cost / total_qty if total_qty else 0

        last = prices.get(ticker, None)
        market_value = (last * total_qty) if last is not None else 0.0
        unrealized = (last - avg_buy_price) * total_qty if last is not None else None

        total_value += market_value
        total_cost += total_buy_cost
        if unrealized is not None:
            total_unrealized += unrealized

        pnl_pct = None
        if unrealized is not None and total_buy_cost:
            pnl_pct = (unrealized / total_buy_cost) * 100

        # oldest buy date (for “days held” display)
        buy_dates = [t.buy_date for t in group if t.buy_date]
        oldest_buy = min(buy_dates).isoformat() if buy_dates else None

        positions.append({
            'id': group[0].id,
            'ticker': ticker,
            'quantity': round(total_qty, 2),
            'buy_price': round(avg_buy_price, 2),
            'cost': round(total_buy_cost, 2),
            'last_price': round(last, 2) if last else None,
            'market_value': round(market_value, 2),
            'unrealized_pnl': round(unrealized, 2) if unrealized else None,
            'pnl_pct': round(pnl_pct, 2) if pnl_pct else None,
            'buy_date': oldest_buy,
        })

    total_gain = total_unrealized
    total_gain_pct = (total_gain / total_cost * 100) if total_cost else None

    def maybe_round(x):
        try:
            return None if x is None else round(float(x), 2)
        except Exception:
            return x

    data = {
        'positions': positions,
        'total_value': maybe_round(total_value),
        'total_cost': maybe_round(total_cost),
        'total_unrealized': maybe_round(total_unrealized),
        'total_gain': maybe_round(total_gain),
        'total_gain_pct': maybe_round(total_gain_pct),
    }

    return JsonResponse(data)

@login_required
def reports(request):
    """
    Reports page showing closed trades and numeric success metrics:
    - total_closed (int)
    - wins (int)
    - losses (int)
    - win_rate (float percent) or None
    - total_realized (float)
    - avg_win (float or None)  -- average realized P&L among winning trades
    - avg_loss (float or None) -- average realized P&L among losing trades (negative number)
    """
    user = request.user
    closed = Trade.objects.filter(user=user, is_closed=True).order_by('-sell_date')

    total_closed = closed.count()
    # winners / losers by realized P&L (sell_price > buy_price)
    wins_qs = closed.filter(sell_price__gt=F('buy_price'))
    losses_qs = closed.filter(sell_price__lte=F('buy_price'))

    wins = wins_qs.count()
    losses = losses_qs.count()
    win_rate = (wins / total_closed * 100) if total_closed else None

    # total realized P&L across all closed trades (use model helper)
    total_realized = 0.0
    realized_list = []
    for t in closed:
        pnl = t.realized_pnl()
        if pnl is None:
            pnl = 0.0
        try:
            pnl = float(pnl)
        except Exception:
            pnl = 0.0
        realized_list.append(pnl)
        total_realized += pnl

    # average win: mean of realized p&l for winning trades
    avg_win = None
    if wins > 0:
        total_win_pnl = 0.0
        for t in wins_qs:
            p = t.realized_pnl() or 0.0
            try:
                total_win_pnl += float(p)
            except Exception:
                pass
        avg_win = total_win_pnl / wins if wins else None

    # average loss: mean of realized p&l for losing trades (will be negative or zero)
    avg_loss = None
    if losses > 0:
        total_loss_pnl = 0.0
        for t in losses_qs:
            p = t.realized_pnl() or 0.0
            try:
                total_loss_pnl += float(p)
            except Exception:
                pass
        avg_loss = total_loss_pnl / losses if losses else None

    context = {
        'closed_trades': closed,
        'total_closed': total_closed,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'total_realized': total_realized,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
    }
    return render(request, 'trades/reports.html', context)


@login_required
def export_closed_csv(request):
    """Export closed trades as CSV download."""
    closed = Trade.objects.filter(user=request.user, is_closed=True).order_by('-sell_date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=closed_trades.csv'
    writer = csv.writer(response)
    writer.writerow(
        ['id', 'ticker', 'quantity', 'buy_price', 'buy_date', 'sell_price', 'sell_date', 'pnl', 'exit_reason',
         'indicators_text', 'charts'])

    for t in closed:
        charts = ";".join([c.image.name for c in t.charts.all()])
        pnl = t.realized_pnl() or 0
        writer.writerow([
            t.id,
            t.ticker,
            str(t.quantity),
            str(t.buy_price),
            t.buy_date.isoformat() if t.buy_date else '',
            str(t.sell_price) if t.sell_price else '',
            t.sell_date.isoformat() if t.sell_date else '',
            str(pnl),
            t.exit_reason or '',
            (t.indicators_text or '').replace('\n', ' | '),
            charts
        ])
    return response


@login_required
def rules_page(request):
    """
    Simple rules editor. We use a single Rules object per user (OneToOne).
    Use a simple textarea for editing (or plug CKEditor in templates/forms).
    """
    rules, created = Rules.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        content = request.POST.get('content', '')
        title = request.POST.get('title', rules.title if rules else 'Stage Analysis Rules')
        rules.title = title
        rules.content = content
        rules.save()
        messages.success(request, "Rules saved.")
        return redirect('rules_page')

    return render(request, 'trades/rules_page.html', {'rules': rules})
