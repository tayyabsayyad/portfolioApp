# 📘 User Guide — Stage Analysis Portfolio Tracker

Welcome to your personal **Stage Analysis Portfolio Tracker**.  
This guide explains how to log in, add trades, manage your portfolio, and use the built-in reports and rules.

---

## 🔐 Login & Logout

- **Login**:  
  Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) → you will be taken to the login page.  
  Enter your username and password (created via admin or given by system owner).  

- **Logout**:  
  Click the **Logout** button in the top navigation bar. You will return to the login page.  

---

## 📊 Dashboard

The dashboard is your home page after logging in.

- **Portfolio Value** — total current value of open trades.  
- **Open Positions** — how many trades are active.  
- **Unrealized P&L** — profit or loss not yet realized.  
- **Positions List** — table of your trades, showing:
  - Ticker  
  - Quantity and buy price  
  - Last price and market value  
  - Unrealized P&L (%)  

👉 Click **Details** to open the full trade record.

---

## ➕ Add a Trade

1. From the top bar, click **Add Trade**.  
2. Fill in:
   - **Ticker** (e.g., TCS, INFY, AAPL).  
   - **Quantity**.  
   - **Buy Price** and **Buy Date**.  
   - **Indicators / Checklist** (paste your Stage 2 notes).  
   - **Buy Notes** (why you entered).  
   - **Upload Charts** (screenshots of weekly charts, etc.).  
3. Click **Save Trade**.  
4. The trade appears in your dashboard and **Open Positions** list.

---

## ❌ Closing a Trade

1. From the **Trades** page or **Trade Detail**, click **Close Trade**.  
2. Fill in:
   - **Sell Price**.  
   - **Sell Date**.  
   - **Exit Reason** (SL, resistance, EMA slope, sector weak, manual).  
   - **Sell Notes / Post-mortem** (what worked or went wrong).  
   - Optionally upload **Sell Charts**.  
3. Click **Close Trade**.  
4. The trade moves into **Reports → Closed Trades**.

---

## 📑 Reports

- **Summary cards**:  
  - Closed Trades count.  
  - Wins count.  
  - Win Rate %.  

- **Closed Trades table**:  
  - Ticker, buy & sell info, realized P&L (green/red).  
  - Exit reason.  
  - Links to trade details.  

- **Export CSV**: Download your closed trades for external analysis.

---

## 📋 Rules Page

Keep your **Stage Analysis checklist** always at hand.

- Rules are displayed as a **large interactive checklist**.  
- Use checkboxes while reviewing a potential trade (local-only, not saved).  
- Edit rules using the **Edit (modal)** button.  
- Save rules → they refresh as the live checklist.  
- Example rules:
  - Stage 2 entry only.  
  - Price above rising 30-week MA.  
  - Mansfield RS positive.  
  - Sector strong, market in uptrend.  

---

## 📂 Trade Details

Click any trade ticker to view its details:

- **Buy details** — buy price/date, indicators, notes.  
- **Charts** — thumbnails of uploaded charts, with captions.  
- **Sell details** (if closed) — sell price/date, exit reason, realized P&L.  
- **Upload more charts** anytime.

---

## 🛠 Admin (for superusers)

- Visit `/admin/` to access the Django admin panel.  
- Manage **Trades**, **Charts**, **Rules**, and **Activity Logs**.  
- Use built-in **CSV export** from the list view.  
- Inline edit charts directly in a trade.  

---

## ✅ Best Practices

- Always upload a **chart screenshot** with each trade — helps review later.  
- Write clear notes on **why you entered/exited**.  
- Regularly check **Reports → Win Rate** to see how well you follow Stage rules.  
- Use the **Rules page** daily before making trades to stay disciplined.  

---

## ℹ️ Troubleshooting

- **Forgot password?** → Use the "Forgot password" link on login page or ask admin to reset.  
- **Page asks for login again** → Your session expired, please log in again.  
- **Charts not showing** → Ensure media uploads are enabled and the `/media/` folder is writable.  

---

Enjoy disciplined, Stage 2-focused trading 🚀