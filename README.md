# 📊 Stage Analysis Portfolio Tracker

A **personal Django web app** to track trades using Stan Weinstein’s Stage Analysis.  
Mobile-friendly, lightweight, and focused on **weekly Stage 2 entries and disciplined exits**.  

Features:
- User authentication (login/logout).
- Add, close, and manage trades.
- Attach notes, stage-2 conditions, and chart images to each trade.
- Dashboard with portfolio value, unrealized/realized P&L, gains %, and sortable table of positions.
- Reports: closed trades, win rate, CSV export.
- Rules page: personal Stage Analysis checklist with interactive checkboxes + modal editor.
- Admin: full management of trades, charts, rules, and activity logs.
- Activity log: every add/close/upload logged with user and timestamp.

---

## 🚀 Quickstart

### 1. Clone & install
```bash
git clone https://github.com/yourusername/stage-portfolio.git
cd stage-portfolio
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

📘 [User Guide](./USER_GUIDE.md)