# SARETY.COM - Real-Time NSE Market Data Platform

A Google Finance-inspired terminal-themed website that displays real-time NSE (National Stock Exchange) market data.

## 🚀 Quick Start

You have **3 versions** to choose from:

### 1. **sarety-website.html** - Simulated Data (No Setup Required)
- **Best for**: Quick demo, testing UI
- **Features**: Realistic simulated NSE data
- Just open the file in your browser - it works immediately!

### 2. **sarety-live-nse.html** - Direct API (Limited)
- **Best for**: Testing without backend
- **Features**: Attempts to fetch from Yahoo Finance
- Note: May have CORS issues and rate limits

### 3. **sarety-integrated.html** + **nse_backend.py** - Full Real-Time Data ⭐ RECOMMENDED
- **Best for**: Production use with real NSE data
- **Features**: Complete real-time NSE data via Python backend
- Requires simple setup (see below)

---

## 📦 Setup for Real NSE Data (Option 3)

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Install Required Python Packages**
```bash
pip install flask flask-cors yfinance
```

2. **Start the Backend Server**
```bash
python nse_backend.py
```

You should see:
```
============================================================
NSE DATA BACKEND SERVER
============================================================

Starting server on http://localhost:5000

Available endpoints:
  - http://localhost:5000/api/indices
  - http://localhost:5000/api/stocks
  - http://localhost:5000/api/gainers
  - http://localhost:5000/api/losers
  - http://localhost:5000/api/market-status
  - http://localhost:5000/api/stock/<SYMBOL>
  - http://localhost:5000/api/search/<QUERY>
```

3. **Open the Website**
- Open `sarety-integrated.html` in your browser
- The website will automatically connect to the backend
- You'll see real-time NSE data!

---

## 🎯 Features

### Real-Time Data
- ✅ NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT indices
- ✅ Top 30 NIFTY 50 stocks with live prices
- ✅ Top gainers and losers
- ✅ Market status (Open/Closed)
- ✅ Auto-refresh every 30 seconds
- ✅ Search functionality

### UI/UX
- 🎨 Terminal green hacker aesthetic
- 📱 Fully responsive design
- ⚡ CRT scanline effects
- 🔄 Live data updates
- 🎯 Clean Google Finance-inspired layout

---

## 🔧 API Endpoints Reference

The backend provides these endpoints:

### Market Status
```bash
GET http://localhost:5000/api/market-status
```

### All Indices
```bash
GET http://localhost:5000/api/indices
```

### NIFTY 50 Stocks
```bash
GET http://localhost:5000/api/stocks
```

### Top Gainers
```bash
GET http://localhost:5000/api/gainers
```

### Top Losers
```bash
GET http://localhost:5000/api/losers
```

### Specific Stock
```bash
GET http://localhost:5000/api/stock/RELIANCE
GET http://localhost:5000/api/stock/TCS.NS
```

### Search
```bash
GET http://localhost:5000/api/search/TATA
```

---

## 🛠️ Customization

### Adding More Stocks
Edit `nse_backend.py` and add symbols to the `NIFTY_50_STOCKS` list:

```python
NIFTY_50_STOCKS = [
    'RELIANCE.NS',
    'TCS.NS',
    'YOUR_STOCK.NS',  # Add here
    # ...
]
```

### Adding More Indices
Edit the `NSE_INDICES` dictionary:

```python
NSE_INDICES = {
    'NIFTY 50': '^NSEI',
    'YOUR INDEX': '^SYMBOL',  # Add here
}
```

### Changing Update Frequency
In `sarety-integrated.html`, find this line:

```javascript
setInterval(() => {
    if (isBackendAvailable) {
        loadCurrentView();
    }
}, 30000);  // Change 30000 (30 seconds) to your preferred interval
```

### Changing Theme Colors
In the HTML file, modify the CSS variables:

```css
:root {
    --terminal-green: #00ff90;  /* Main color */
    --terminal-bg: #000;        /* Background */
}
```

---

## 🚨 Troubleshooting

### Backend Not Connecting
**Problem**: Website shows "Backend server not running"

**Solutions**:
1. Check if Python server is running:
   ```bash
   python nse_backend.py
   ```
2. Check if port 5000 is available:
   ```bash
   # On Linux/Mac
   lsof -i :5000
   
   # On Windows
   netstat -ano | findstr :5000
   ```
3. Make sure firewall allows port 5000

### CORS Errors
**Problem**: Browser console shows CORS errors

**Solution**: The backend already has CORS enabled. If issues persist:
1. Make sure you're accessing the HTML file via `file://` or a local server
2. Try opening with: `python -m http.server 8000`
3. Then access: `http://localhost:8000/sarety-integrated.html`

### No Data Showing
**Problem**: Empty lists or "No data available"

**Possible Causes**:
1. Market is closed (NSE only operates weekdays 9:15 AM - 3:30 PM IST)
2. Yahoo Finance rate limiting
3. Internet connection issues

**Solutions**:
- Check your internet connection
- Wait a few minutes and refresh
- Check backend logs for errors

### Slow Loading
**Problem**: Data takes long to load

**Solution**: Reduce the number of stocks fetched:
```python
# In nse_backend.py, change:
for symbol in NIFTY_50_STOCKS[:20]:  # Reduce from 30 to 10
```

---

## 📊 Data Source

This project uses **Yahoo Finance** (via yfinance library) which provides:
- Real-time NSE data (15-20 minute delay for free tier)
- Historical data
- Company fundamentals

### Data Accuracy
- ✅ Prices: Accurate (15-20 min delay)
- ✅ Changes: Calculated accurately
- ✅ Volume: Real-time
- ⚠️ Not suitable for actual trading decisions

---

## 🔐 Production Deployment

### Using a Cloud Server

1. **Deploy Backend to Heroku/AWS/DigitalOcean**:
```bash
# Example for Heroku
heroku create your-app-name
git push heroku main
```

2. **Update API URL in HTML**:
```javascript
const API_BASE_URL = 'https://your-app.herokuapp.com/api';
```

3. **Enable HTTPS**:
```python
# In nse_backend.py
if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # For development only
```

### Environment Variables
For production, use environment variables:

```python
import os
PORT = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=PORT)
```

---

## 📝 License & Disclaimer

### License
This project is for educational purposes only.

### Disclaimer
⚠️ **IMPORTANT**: This is NOT financial advice.
- Data may have delays (15-20 minutes)
- Do not use for actual trading decisions
- Always verify data from official sources
- NSE India and Yahoo Finance are trademarks of their respective owners

---

## 🤝 Contributing

Want to improve this project? Here are some ideas:
- Add more indices (NIFTY NEXT 50, etc.)
- Implement candlestick charts
- Add news feed integration
- Create user portfolios with local storage
- Add price alerts
- Implement WebSocket for real-time updates

---

## 📧 Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify backend is running: `http://localhost:5000`
3. Check browser console for errors (F12)
4. Review backend logs

---

## 🎉 Acknowledgments

- NSE India for market data structure
- Yahoo Finance for data API
- Google Finance for UI inspiration
- Chart.js for beautiful charts

---

## 📦 File Structure

```
├── sarety-website.html          # Simulated data version
├── sarety-live-nse.html         # Direct API version
├── sarety-integrated.html       # Full version (frontend)
├── nse_backend.py              # Backend server
└── README.md                   # This file
```

---

## 🚀 Quick Commands Reference

```bash
# Install dependencies
pip install flask flask-cors yfinance

# Start backend
python nse_backend.py

# Open website (after backend is running)
# Just double-click sarety-integrated.html

# Test API manually
curl http://localhost:5000/api/indices
curl http://localhost:5000/api/stocks
curl http://localhost:5000/api/market-status
```

---

**Made with ❤️ for the NSE trading community**

Happy Trading! 📈
