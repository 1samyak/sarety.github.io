"""
NSE Data Backend Server
========================

This Flask server fetches real-time NSE data and serves it to your SARETY website.

Installation:
-------------
pip install flask flask-cors yfinance

Usage:
------
python nse_backend.py

Then open your SARETY website and it will fetch data from http://localhost:5000

"""

from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# ─── Cache Configuration ─────────────────────────────────────────────────────
CACHE_TTL = 60  # seconds
cache = {}
cache_lock = threading.Lock()


def get_cached(key):
    """Get a cached value if it exists and hasn't expired."""
    with cache_lock:
        if key in cache:
            data, timestamp = cache[key]
            if time.time() - timestamp < CACHE_TTL:
                return data
    return None


def set_cached(key, data):
    """Store data in cache with current timestamp."""
    with cache_lock:
        cache[key] = (data, time.time())


# ─── Stock Data ──────────────────────────────────────────────────────────────

# NSE Index symbols (Yahoo Finance format)
NSE_INDICES = {
    'NIFTY 50': '^NSEI',
    'SENSEX': '^BSESN',
    'BANK NIFTY': '^NSEBANK',
    'NIFTY IT': '^CNXIT',
    'NIFTY PHARMA': '^CNXPHARMA',
    'NIFTY AUTO': '^CNXAUTO'
}

# Popular NSE stocks
NIFTY_50_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
    'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
    'TITAN.NS', 'WIPRO.NS', 'TATAMOTORS.NS', 'BAJFINANCE.NS', 'M&M.NS',
    'NESTLEIND.NS', 'HCLTECH.NS', 'ULTRACEMCO.NS', 'ONGC.NS', 'POWERGRID.NS',
    'NTPC.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'ADANIENT.NS', 'ADANIPORTS.NS'
]


def get_stock_data(symbol):
    """Fetch stock data from Yahoo Finance with caching."""
    # Check cache first
    cached = get_cached(f"stock_{symbol}")
    if cached:
        return cached

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        history = ticker.history(period='1d')

        if history.empty:
            return None

        current_price = history['Close'].iloc[-1]
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close else 0

        result = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'price': round(current_price, 2),
            'change': round(change, 2),
            'changePercent': round(change_percent, 2),
            'open': round(history['Open'].iloc[-1], 2) if not history['Open'].empty else None,
            'high': round(history['High'].iloc[-1], 2) if not history['High'].empty else None,
            'low': round(history['Low'].iloc[-1], 2) if not history['Low'].empty else None,
            'volume': int(history['Volume'].iloc[-1]) if not history['Volume'].empty else 0,
            'marketCap': info.get('marketCap', 0),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A')
        }

        # Cache the result
        set_cached(f"stock_{symbol}", result)
        return result
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        return None


def fetch_stocks_concurrent(symbols):
    """Fetch multiple stocks concurrently using thread pool."""
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_symbol = {executor.submit(get_stock_data, symbol): symbol for symbol in symbols}
        for future in as_completed(future_to_symbol):
            data = future.result()
            if data:
                results.append(data)
    return results


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    """API information"""
    return jsonify({
        'name': 'NSE Data API',
        'version': '1.0',
        'status': 'active',
        'endpoints': {
            '/api/indices': 'Get all NSE indices',
            '/api/stocks': 'Get NIFTY 50 stocks',
            '/api/stock/<symbol>': 'Get specific stock data',
            '/api/market-status': 'Get market status',
            '/api/gainers': 'Get top gainers',
            '/api/losers': 'Get top losers',
            '/api/search/<query>': 'Search for stocks'
        }
    })


@app.route('/api/market-status')
def market_status():
    """Check if NSE market is open (uses IST timezone)"""
    now = datetime.now(IST)
    is_weekday = now.weekday() < 5  # Monday = 0, Sunday = 6
    current_time = now.time()

    # NSE trading hours: 9:15 AM to 3:30 PM IST
    market_open = is_weekday and (
        (current_time.hour == 9 and current_time.minute >= 15) or
        (9 < current_time.hour < 15) or
        (current_time.hour == 15 and current_time.minute <= 30)
    )

    return jsonify({
        'isOpen': market_open,
        'timestamp': now.isoformat(),
        'day': now.strftime('%A'),
        'message': 'Market is open' if market_open else 'Market is closed'
    })


@app.route('/api/indices')
def get_indices():
    """Fetch all NSE indices data (concurrent + cached)"""
    # Check full response cache
    cached = get_cached('indices_response')
    if cached:
        logger.info("Returning cached indices")
        return jsonify(cached)

    logger.info("Fetching NSE indices...")
    symbols = list(NSE_INDICES.values())
    names = list(NSE_INDICES.keys())

    indices_data = []
    results = fetch_stocks_concurrent(symbols)

    # Map results back to names
    symbol_to_name = dict(zip(NSE_INDICES.values(), NSE_INDICES.keys()))
    for data in results:
        name = symbol_to_name.get(data['symbol'], data['symbol'])
        indices_data.append({
            'name': name,
            'symbol': data['symbol'],
            'price': data['price'],
            'change': data['change'],
            'changePercent': data['changePercent'],
            'timestamp': datetime.now(IST).isoformat()
        })

    response = {
        'success': True,
        'count': len(indices_data),
        'data': indices_data,
        'timestamp': datetime.now(IST).isoformat()
    }

    set_cached('indices_response', response)
    return jsonify(response)


@app.route('/api/stocks')
def get_stocks():
    """Fetch NIFTY 50 stocks data (concurrent + cached)"""
    cached = get_cached('stocks_response')
    if cached:
        logger.info("Returning cached stocks")
        return jsonify(cached)

    logger.info("Fetching NIFTY 50 stocks...")
    stocks_data = fetch_stocks_concurrent(NIFTY_50_STOCKS[:20])

    # Sort by absolute change percentage
    stocks_data.sort(key=lambda x: abs(x['changePercent']), reverse=True)

    response = {
        'success': True,
        'count': len(stocks_data),
        'data': stocks_data,
        'timestamp': datetime.now(IST).isoformat()
    }

    set_cached('stocks_response', response)
    return jsonify(response)


@app.route('/api/stock/<symbol>')
def get_single_stock(symbol):
    """Fetch specific stock data"""
    logger.info(f"Fetching {symbol}...")

    # Add .NS if not present
    if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
        symbol = f"{symbol}.NS"

    data = get_stock_data(symbol)

    if data:
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now(IST).isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Stock not found or data unavailable'
        }), 404


@app.route('/api/gainers')
def get_gainers():
    """Get top gainers (concurrent + cached)"""
    cached = get_cached('gainers_response')
    if cached:
        logger.info("Returning cached gainers")
        return jsonify(cached)

    logger.info("Fetching top gainers...")
    all_stocks = fetch_stocks_concurrent(NIFTY_50_STOCKS[:30])
    stocks_data = [s for s in all_stocks if s['changePercent'] > 0]
    stocks_data.sort(key=lambda x: x['changePercent'], reverse=True)

    response = {
        'success': True,
        'count': len(stocks_data[:10]),
        'data': stocks_data[:10],
        'timestamp': datetime.now(IST).isoformat()
    }

    set_cached('gainers_response', response)
    return jsonify(response)


@app.route('/api/losers')
def get_losers():
    """Get top losers (concurrent + cached)"""
    cached = get_cached('losers_response')
    if cached:
        logger.info("Returning cached losers")
        return jsonify(cached)

    logger.info("Fetching top losers...")
    all_stocks = fetch_stocks_concurrent(NIFTY_50_STOCKS[:30])
    stocks_data = [s for s in all_stocks if s['changePercent'] < 0]
    stocks_data.sort(key=lambda x: x['changePercent'])

    response = {
        'success': True,
        'count': len(stocks_data[:10]),
        'data': stocks_data[:10],
        'timestamp': datetime.now(IST).isoformat()
    }

    set_cached('losers_response', response)
    return jsonify(response)


@app.route('/api/search/<query>')
def search_stocks(query):
    """Search for stocks"""
    logger.info(f"Searching for: {query}")
    query = query.upper()

    matching_symbols = [s for s in NIFTY_50_STOCKS if query in s.upper()]
    results = fetch_stocks_concurrent(matching_symbols) if matching_symbols else []

    return jsonify({
        'success': True,
        'query': query,
        'count': len(results),
        'data': results
    })


if __name__ == '__main__':
    print("=" * 60)
    print("NSE DATA BACKEND SERVER")
    print("=" * 60)
    print("\nStarting server on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  - http://localhost:5000/api/indices")
    print("  - http://localhost:5000/api/stocks")
    print("  - http://localhost:5000/api/gainers")
    print("  - http://localhost:5000/api/losers")
    print("  - http://localhost:5000/api/market-status")
    print("  - http://localhost:5000/api/stock/<SYMBOL>")
    print("  - http://localhost:5000/api/search/<QUERY>")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
