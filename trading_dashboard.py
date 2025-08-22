#!/usr/bin/env python3
"""
AI Trading Simulator Dashboard
Features: Real-time charts, multi-asset monitoring, interactive trading
"""

import http.server
import socketserver
import json
import time
import random
import threading
from datetime import datetime, timedelta
from urllib.parse import urlparse
import math


class TradingSimulator:
    """Realistic trading simulator for the web dashboard."""
    
    def __init__(self):
        self.running = False
        # Real-world asset data with realistic starting prices
        self.assets = {
            'AAPL': {'price': 175.50, 'volume': 45000000, 'type': 'stock', 'vwap': 175.50, 'rsi': 52.3, 'sector': 'Technology'},
            'MSFT': {'price': 338.20, 'volume': 22000000, 'type': 'stock', 'vwap': 338.20, 'rsi': 48.7, 'sector': 'Technology'},
            'GOOGL': {'price': 142.80, 'volume': 18000000, 'type': 'stock', 'vwap': 142.80, 'rsi': 55.2, 'sector': 'Technology'},
            'TSLA': {'price': 248.90, 'volume': 85000000, 'type': 'stock', 'vwap': 248.90, 'rsi': 41.8, 'sector': 'Automotive'},
            'NVDA': {'price': 485.30, 'volume': 55000000, 'type': 'stock', 'vwap': 485.30, 'rsi': 62.1, 'sector': 'Technology'},
            'BTC': {'price': 43250.00, 'volume': 280000, 'type': 'crypto', 'vwap': 43250.00, 'rsi': 44.5, 'sector': 'Digital Assets'},
            'ETH': {'price': 2650.00, 'volume': 420000, 'type': 'crypto', 'vwap': 2650.00, 'rsi': 51.3, 'sector': 'Digital Assets'},
            'EUR/USD': {'price': 1.0875, 'volume': 125000, 'type': 'forex', 'vwap': 1.0875, 'rsi': 47.8, 'sector': 'Currency'},
            'GOLD': {'price': 1985.50, 'volume': 8500, 'type': 'commodity', 'vwap': 1985.50, 'rsi': 58.9, 'sector': 'Precious Metals'},
            'SPY': {'price': 456.80, 'volume': 75000000, 'type': 'etf', 'vwap': 456.80, 'rsi': 49.2, 'sector': 'Market Index'}
        }
        
        self.portfolio = {
            'cash': 1000000.0,
            'total_value': 1000000.0,
            'daily_pnl': 0.0,
            'total_pnl': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'positions': {},
            'trades': [],
            'watchlist': ['AAPL', 'MSFT', 'NVDA', 'BTC'],
            'risk_level': 'moderate',  # conservative, moderate, aggressive
            'max_position_size': 0.15,  # 15% max per position
            'daily_loss_limit': 0.03    # 3% daily loss limit
        }
        
        self.price_history = {symbol: [] for symbol in self.assets}
        self.performance_history = []
        self.trade_count = 0
        self.market_sentiment = 'neutral'  # bullish, bearish, neutral
        self.news_events = []
        
    def start(self):
        """Start the simulator."""
        self.running = True
        print("🚀 AI Trading Simulator Started!")
        
    def stop(self):
        """Stop the simulator."""
        self.running = False
        print("🛑 AI Trading Simulator Stopped")
        
    def update_market_data(self):
        """Update market data with realistic movements."""
        if not self.running:
            return
            
        # Update market sentiment based on overall performance
        if len(self.performance_history) > 10:
            recent_performance = [p['total_value'] for p in self.performance_history[-10:]]
            if recent_performance[-1] > recent_performance[0] * 1.02:
                self.market_sentiment = 'bullish'
            elif recent_performance[-1] < recent_performance[0] * 0.98:
                self.market_sentiment = 'bearish'
            else:
                self.market_sentiment = 'neutral'
        
        # Generate realistic price movements based on asset type and market sentiment
        for symbol, asset in self.assets.items():
            # Base volatility by asset type
            base_volatility = {
                'stock': 0.015,
                'crypto': 0.035,
                'forex': 0.008,
                'commodity': 0.012,
                'etf': 0.010
            }.get(asset['type'], 0.020)
            
            # Adjust volatility based on market sentiment
            sentiment_multiplier = {
                'bullish': 1.2,
                'bearish': 1.3,
                'neutral': 1.0
            }.get(self.market_sentiment, 1.0)
            
            # Sector-specific volatility adjustments
            sector_volatility = {
                'Technology': 1.3,
                'Automotive': 1.4,
                'Digital Assets': 1.5,
                'Currency': 0.8,
                'Precious Metals': 0.9,
                'Market Index': 0.7
            }.get(asset.get('sector', 'Other'), 1.0)
            
            # Calculate final volatility
            final_volatility = base_volatility * sentiment_multiplier * sector_volatility
            
            # Generate price movement with realistic distribution
            if random.random() < 0.7:  # 70% normal movement
                price_change = random.gauss(0, final_volatility)
            else:  # 30% larger movement (market events)
                price_change = random.gauss(0, final_volatility * 2)
            
            # Apply price change
            new_price = asset['price'] * (1 + price_change)
            
            # Ensure prices stay realistic
            if asset['type'] == 'stock':
                new_price = max(new_price, 1.0)  # Stocks can't go below $1
            elif asset['type'] == 'crypto':
                new_price = max(new_price, 0.01)  # Crypto can't go below $0.01
            
            # Update price history with timestamp
            self.price_history[symbol].append({
                'price': new_price,
                'timestamp': datetime.now().isoformat(),
                'volume': asset['volume'],
                'vwap': asset['vwap'],
                'rsi': asset['rsi']
            })
            
            # Keep only last 200 data points for better charts
            if len(self.price_history[symbol]) > 200:
                self.price_history[symbol].pop(0)
            
            # Update VWAP with realistic calculation
            if len(self.price_history[symbol]) > 0:
                recent_data = self.price_history[symbol][-20:]  # Last 20 data points
                total_pv = sum(d['price'] * d['volume'] for d in recent_data)
                total_volume = sum(d['volume'] for d in recent_data)
                asset['vwap'] = total_pv / total_volume if total_volume > 0 else new_price
            
            # Update RSI with realistic momentum
            if len(self.price_history[symbol]) > 14:
                asset['rsi'] = self._calculate_rsi([d['price'] for d in self.price_history[symbol]])
            
            # Update volume with realistic patterns
            volume_change = random.gauss(0, 0.15)  # Normal distribution for volume
            new_volume = max(int(asset['volume'] * (1 + volume_change)), 1000)
            asset['volume'] = new_volume
            
            # Update price
            asset['price'] = new_price
            
            # Generate trading signals with enhanced logic
            self._generate_trading_signals(symbol, asset)
        
        # Update portfolio and generate news events
        self._update_portfolio()
        self._generate_news_events()
        
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI with realistic smoothing."""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Use exponential moving average for more realistic RSI
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _generate_trading_signals(self, symbol, asset):
        """Generate enhanced trading signals."""
        price = asset['price']
        vwap = asset['vwap']
        rsi = asset['rsi']
        
        # Enhanced signal generation with multiple factors
        vwap_deviation = (price - vwap) / vwap if vwap > 0 else 0
        rsi_signal = 0
        
        # RSI signals with realistic thresholds
        if rsi < 25:  # Strong oversold
            rsi_signal = 2
        elif rsi < 35:  # Oversold
            rsi_signal = 1
        elif rsi > 75:  # Strong overbought
            rsi_signal = -2
        elif rsi > 65:  # Overbought
            rsi_signal = -1
        
        # Volume confirmation
        volume_signal = 0
        if len(self.price_history[symbol]) > 5:
            recent_volume = [d['volume'] for d in self.price_history[symbol][-5:]]
            avg_volume = sum(recent_volume) / len(recent_volume)
            if asset['volume'] > avg_volume * 1.5:  # High volume
                volume_signal = 1
            elif asset['volume'] < avg_volume * 0.5:  # Low volume
                volume_signal = -1
        
        # Combined signal strength
        signal_strength = 0
        if vwap_deviation < -0.02 and rsi_signal >= 1:  # Strong buy
            signal_strength = 2
        elif vwap_deviation < -0.01 and rsi_signal >= 1:  # Buy
            signal_strength = 1
        elif vwap_deviation > 0.02 and rsi_signal <= -1:  # Strong sell
            signal_strength = -2
        elif vwap_deviation > 0.01 and rsi_signal <= -1:  # Sell
            signal_strength = -1
        
        # Execute trades based on signal strength and risk management
        if signal_strength >= 1:
            quantity = int(1000 * signal_strength * (1 + volume_signal * 0.2))
            self._execute_trade(symbol, "BUY", quantity, price)
        elif signal_strength <= -1:
            quantity = int(1000 * abs(signal_strength) * (1 + abs(volume_signal) * 0.2))
            self._execute_trade(symbol, "SELL", quantity, price)
    
    def _execute_trade(self, symbol, side, quantity, price):
        """Execute trade with enhanced risk management."""
        # Check position limits
        position_value = abs(quantity * price)
        if position_value > self.portfolio['total_value'] * self.portfolio['max_position_size']:
            quantity = int(self.portfolio['total_value'] * self.portfolio['max_position_size'] / price)
        
        # Check daily loss limit
        if self.portfolio['daily_pnl'] < -self.portfolio['total_value'] * self.portfolio['daily_loss_limit']:
            return  # Stop trading if daily loss limit reached
        
        trade_value = quantity * price
        fees = trade_value * 0.001  # Realistic commission
        
        if side == "BUY":
            if self.portfolio['cash'] >= (trade_value + fees):
                self.portfolio['cash'] -= (trade_value + fees)
                self.portfolio['positions'][symbol] = self.portfolio['positions'].get(symbol, 0) + quantity
                self._record_trade(symbol, side, quantity, price, fees)
        else:  # SELL
            if self.portfolio['positions'].get(symbol, 0) >= quantity:
                self.portfolio['cash'] += (trade_value - fees)
                self.portfolio['positions'][symbol] = self.portfolio['positions'].get(symbol, 0) - quantity
                self._record_trade(symbol, side, quantity, price, fees)
    
    def _record_trade(self, symbol, side, quantity, price, fees):
        """Record trade with enhanced details."""
        self.trade_count += 1
        
        # Calculate P&L for this trade
        pnl = 0
        if side == "SELL" and symbol in self.portfolio['positions']:
            # Simplified P&L calculation
            pnl = quantity * (price - self.assets[symbol]['vwap'])
        
        trade = {
            'id': f"T{self.trade_count:06d}",
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now().isoformat(),
            'fees': fees,
            'pnl': pnl,
            'vwap_at_trade': self.assets[symbol]['vwap'],
            'rsi_at_trade': self.assets[symbol]['rsi']
        }
        self.portfolio['trades'].append(trade)
        
        # Keep only last 200 trades
        if len(self.portfolio['trades']) > 200:
            self.portfolio['trades'].pop(0)
    
    def _update_portfolio(self):
        """Update portfolio with enhanced metrics."""
        total_value = self.portfolio['cash']
        
        for symbol, quantity in self.portfolio['positions'].items():
            if quantity != 0 and symbol in self.assets:
                price = self.assets[symbol]['price']
                total_value += quantity * price
        
        self.portfolio['total_value'] = total_value
        
        # Calculate daily P&L
        if self.performance_history:
            last_value = self.performance_history[-1]['total_value']
            self.portfolio['daily_pnl'] = total_value - last_value
        else:
            self.portfolio['daily_pnl'] = 0.0
        
        # Update performance history
        self.performance_history.append({
            'timestamp': datetime.now().isoformat(),
            'total_value': total_value,
            'cash': self.portfolio['cash'],
            'market_sentiment': self.market_sentiment
        })
        
        # Keep only last 200 data points
        if len(self.performance_history) > 200:
            self.performance_history.pop(0)
        
        # Calculate performance metrics
        self._calculate_performance_metrics()
    
    def _calculate_performance_metrics(self):
        """Calculate enhanced performance metrics."""
        if len(self.performance_history) < 2:
            return
        
        # Calculate returns
        returns = []
        for i in range(1, len(self.performance_history)):
            prev_value = self.performance_history[i-1]['total_value']
            curr_value = self.performance_history[i]['total_value']
            if prev_value > 0:
                returns.append((curr_value - prev_value) / prev_value)
        
        if returns:
            # Enhanced Sharpe ratio
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            std_return = math.sqrt(variance) if variance > 0 else 0
            self.portfolio['sharpe_ratio'] = mean_return / std_return if std_return > 0 else 0
            
            # Max drawdown with time tracking
            peak = self.performance_history[0]['total_value']
            max_dd = 0
            for metric in self.performance_history:
                if metric['total_value'] > peak:
                    peak = metric['total_value']
                dd = (peak - metric['total_value']) / peak
                max_dd = max(max_dd, dd)
            self.portfolio['max_drawdown'] = max_dd
            
            # Win rate calculation
            winning_days = sum(1 for r in returns if r > 0)
            self.portfolio['win_rate'] = winning_days / len(returns) if returns else 0
    
    def _generate_news_events(self):
        """Generate realistic market news events."""
        if random.random() < 0.1:  # 10% chance per update
            events = [
                "Fed announces interest rate decision",
                "Tech earnings beat expectations",
                "Oil prices surge on supply concerns",
                "Crypto adoption increases",
                "Market volatility spikes",
                "Economic data shows strong growth",
                "Trade tensions ease",
                "Inflation data released"
            ]
            
            event = random.choice(events)
            timestamp = datetime.now().isoformat()
            
            self.news_events.append({
                'event': event,
                'timestamp': timestamp,
                'impact': random.choice(['positive', 'negative', 'neutral'])
            })
            
            # Keep only last 10 news events
            if len(self.news_events) > 10:
                self.news_events.pop(0)
    
    def get_status(self):
        """Get comprehensive simulator status."""
        return {
            "running": self.running,
            "assets": self.assets,
            "portfolio": self.portfolio,
            "price_history": self.price_history,
            "performance_history": self.performance_history,
            "market_sentiment": self.market_sentiment,
            "news_events": self.news_events,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }


# Global simulator instance
trading_simulator = TradingSimulator()


class TradingDashboardHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for the trading dashboard."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == "/":
            self.send_dashboard()
        elif path == "/api/status":
            self.send_api_response(trading_simulator.get_status())
        elif path == "/api/start":
            trading_simulator.start()
            self.send_api_response({"message": "Trading simulator started"})
        elif path == "/api/stop":
            trading_simulator.stop()
            self.send_api_response({"message": "Trading simulator stopped"})
        else:
            self.send_error(404, "Not found")
    
    def send_dashboard(self):
        """Send the main dashboard HTML."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Trading Simulator Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: #333;
                    min-height: 100vh;
                }
                
                .container { 
                    max-width: 1400px; 
                    margin: 0 auto; 
                    padding: 20px;
                }
                
                .header { 
                    background: rgba(255,255,255,0.95);
                    backdrop-filter: blur(10px);
                    padding: 30px;
                    border-radius: 20px;
                    margin-bottom: 30px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                }
                
                .header h1 {
                    font-size: 2.5em;
                    color: #1e3c72;
                    margin-bottom: 10px;
                }
                
                .header p {
                    font-size: 1.2em;
                    color: #666;
                }
                
                .controls {
                    display: flex;
                    gap: 20px;
                    justify-content: center;
                    margin: 20px 0;
                }
                
                .btn {
                    background: linear-gradient(45deg, #4CAF50, #45a049);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 50px;
                    cursor: pointer;
                    font-size: 1.1em;
                    font-weight: bold;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
                }
                
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
                }
                
                .btn.danger {
                    background: linear-gradient(45deg, #f44336, #da190b);
                    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
                }
                
                .btn.danger:hover {
                    box-shadow: 0 6px 20px rgba(244, 67, 54, 0.4);
                }
                
                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 25px;
                    margin-bottom: 30px;
                }
                
                .card {
                    background: rgba(255,255,255,0.95);
                    backdrop-filter: blur(10px);
                    padding: 25px;
                    border-radius: 20px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }
                
                .card:hover {
                    transform: translateY(-5px);
                }
                
                .card h3 {
                    color: #1e3c72;
                    margin-bottom: 20px;
                    font-size: 1.3em;
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 10px;
                }
                
                .status {
                    padding: 15px;
                    border-radius: 15px;
                    margin: 15px 0;
                    text-align: center;
                    font-weight: bold;
                    font-size: 1.1em;
                }
                
                .status.running {
                    background: linear-gradient(45deg, #4CAF50, #45a049);
                    color: white;
                }
                
                .status.stopped {
                    background: linear-gradient(45deg, #f44336, #da190b);
                    color: white;
                }
                
                .metric {
                    text-align: center;
                    margin: 20px 0;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 15px;
                }
                
                .metric-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #1e3c72;
                    margin-bottom: 5px;
                }
                
                .metric-label {
                    color: #666;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                .price-up { color: #4CAF50; }
                .price-down { color: #f44336; }
                .price-same { color: #666; }
                
                .asset-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 20px;
                }
                
                .asset-item {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    border-left: 4px solid #1e3c72;
                    transition: all 0.3s ease;
                }
                
                .asset-item:hover {
                    transform: scale(1.02);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }
                
                .asset-symbol {
                    font-weight: bold;
                    font-size: 1.1em;
                    color: #1e3c72;
                    margin-bottom: 5px;
                }
                
                .asset-price {
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                
                .asset-type {
                    font-size: 0.8em;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                .chart-container {
                    height: 300px;
                    margin-top: 20px;
                }
                
                .trades-list {
                    max-height: 300px;
                    overflow-y: auto;
                    margin-top: 20px;
                }
                
                .trade-item {
                    background: #f8f9fa;
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 8px;
                    border-left: 4px solid #1e3c72;
                    font-size: 0.9em;
                }
                
                .trade-buy { border-left-color: #4CAF50; }
                .trade-sell { border-left-color: #f44336; }
                
                .loading {
                    text-align: center;
                    padding: 40px;
                    color: #666;
                }
                
                .market-sentiment {
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 10px 0;
                }
                
                .sentiment-bullish { background: #d4edda; color: #155724; }
                .sentiment-bearish { background: #f8d7da; color: #721c24; }
                .sentiment-neutral { background: #d1ecf1; color: #0c5460; }
                
                .news-events {
                    max-height: 200px;
                    overflow-y: auto;
                    margin-top: 15px;
                }
                
                .news-item {
                    background: #f8f9fa;
                    padding: 8px;
                    margin: 5px 0;
                    border-radius: 6px;
                    font-size: 0.85em;
                    border-left: 3px solid #1e3c72;
                }
                
                .news-positive { border-left-color: #4CAF50; }
                .news-negative { border-left-color: #f44336; }
                .news-neutral { border-left-color: #2196F3; }
                
                @media (max-width: 768px) {
                    .grid {
                        grid-template-columns: 1fr;
                    }
                    .header h1 {
                        font-size: 2em;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 AI Trading Simulator Dashboard</h1>
                    <p>Multi-Asset Portfolio • Real-Time Trading • Professional Analytics</p>
                    <div class="controls">
                        <button class="btn" onclick="startSimulator()">🚀 Start Trading</button>
                        <button class="btn danger" onclick="stopSimulator()">⏹️ Stop Trading</button>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>📊 Portfolio Overview</h3>
                        <div id="status" class="status stopped">STOPPED</div>
                        <div class="metric">
                            <div id="totalValue" class="metric-value">$0</div>
                            <div class="metric-label">Total Portfolio Value</div>
                        </div>
                        <div class="metric">
                            <div id="dailyPnl" class="metric-value">$0</div>
                            <div class="metric-label">Daily P&L</div>
                        </div>
                        <div class="metric">
                            <div id="totalPnl" class="metric-value">$0</div>
                            <div class="metric-label">Total P&L</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>📈 Performance Metrics</h3>
                        <div class="metric">
                            <div id="sharpeRatio" class="metric-value">0.000</div>
                            <div class="metric-label">Sharpe Ratio</div>
                        </div>
                        <div class="metric">
                            <div id="maxDrawdown" class="metric-value">0.00%</div>
                            <div class="metric-label">Max Drawdown</div>
                        </div>
                        <div class="metric">
                            <div id="winRate" class="metric-value">0.00%</div>
                            <div class="metric-label">Win Rate</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>💰 Trading Activity</h3>
                        <div class="metric">
                            <div id="totalTrades" class="metric-value">0</div>
                            <div class="metric-label">Total Trades</div>
                        </div>
                        <div class="metric">
                            <div id="activePositions" class="metric-value">0</div>
                            <div class="metric-label">Active Positions</div>
                        </div>
                        <div class="metric">
                            <div id="cash" class="metric-value">$0</div>
                            <div class="metric-label">Available Cash</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>📊 Portfolio Performance Chart</h3>
                        <div class="chart-container">
                            <canvas id="performanceChart"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🎯 Multi-Asset Trading</h3>
                    <div id="marketSentiment" class="market-sentiment sentiment-neutral">Market: Neutral</div>
                    <div class="asset-grid" id="assetGrid">
                        <div class="loading">Loading assets...</div>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>📈 Price Charts</h3>
                        <div class="chart-container">
                            <canvas id="priceChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>🔄 Recent Trades</h3>
                        <div id="tradesList" class="trades-list">
                            <div class="loading">No trades yet</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📰 Market News & Events</h3>
                    <div id="newsEvents" class="news-events">
                        <div class="loading">Waiting for market events...</div>
                    </div>
                </div>
            </div>
            
            <script>
                let updateInterval = null;
                let performanceChart = null;
                let priceChart = null;
                
                // Initialize charts
                function initializeCharts() {
                    // Performance Chart
                    const perfCtx = document.getElementById('performanceChart').getContext('2d');
                    performanceChart = new Chart(perfCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Portfolio Value',
                                data: [],
                                borderColor: '#1e3c72',
                                backgroundColor: 'rgba(30, 60, 114, 0.1)',
                                tension: 0.4,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                y: {
                                    beginAtZero: false,
                                    grid: { color: 'rgba(0,0,0,0.1)' }
                                },
                                x: {
                                    grid: { color: 'rgba(0,0,0,0.1)' }
                                }
                            }
                        }
                    });
                    
                    // Price Chart
                    const priceCtx = document.getElementById('priceChart').getContext('2d');
                    priceChart = new Chart(priceCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'AAPL',
                                data: [],
                                borderColor: '#4CAF50',
                                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                                tension: 0.4
                            }, {
                                label: 'BTC',
                                data: [],
                                borderColor: '#FF9800',
                                backgroundColor: 'rgba(255, 152, 0, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: true }
                            },
                            scales: {
                                y: {
                                    beginAtZero: false,
                                    grid: { color: 'rgba(0,0,0,0.1)' }
                                },
                                x: {
                                    grid: { color: 'rgba(0,0,0,0.1)' }
                                }
                            }
                        }
                    });
                }
                
                function updateDashboard() {
                    fetch('/api/status')
                        .then(response => response.json())
                        .then(data => {
                            // Update status
                            const statusDiv = document.getElementById('status');
                            statusDiv.textContent = data.running ? 'RUNNING' : 'STOPPED';
                            statusDiv.className = 'status ' + (data.running ? 'running' : 'stopped');
                            
                            // Update market sentiment
                            updateMarketSentiment(data.market_sentiment);
                            
                            // Update portfolio metrics
                            document.getElementById('totalValue').textContent = '$' + data.portfolio.total_value.toLocaleString();
                            document.getElementById('dailyPnl').textContent = '$' + data.portfolio.daily_pnl.toLocaleString();
                            document.getElementById('totalPnl').textContent = '$' + data.portfolio.total_pnl.toLocaleString();
                            document.getElementById('sharpeRatio').textContent = data.portfolio.sharpe_ratio.toFixed(3);
                            document.getElementById('maxDrawdown').textContent = (data.portfolio.max_drawdown * 100).toFixed(2) + '%';
                            document.getElementById('winRate').textContent = (data.portfolio.win_rate * 100).toFixed(2) + '%';
                            document.getElementById('totalTrades').textContent = data.portfolio.trades.length;
                            document.getElementById('activePositions').textContent = Object.keys(data.portfolio.positions).length;
                            document.getElementById('cash').textContent = '$' + data.portfolio.cash.toLocaleString();
                            
                            // Update asset grid
                            updateAssetGrid(data.assets);
                            
                            // Update trades list
                            updateTradesList(data.portfolio.trades);
                            
                            // Update news events
                            updateNewsEvents(data.news_events);
                            
                            // Update charts
                            updateCharts(data);
                        })
                        .catch(error => console.error('Error fetching status:', error));
                }
                
                function updateMarketSentiment(sentiment) {
                    const sentimentDiv = document.getElementById('marketSentiment');
                    sentimentDiv.textContent = 'Market: ' + sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
                    sentimentDiv.className = 'market-sentiment sentiment-' + sentiment;
                }
                
                function updateAssetGrid(assets) {
                    const grid = document.getElementById('assetGrid');
                    grid.innerHTML = '';
                    
                    Object.entries(assets).forEach(([symbol, asset]) => {
                        const assetDiv = document.createElement('div');
                        assetDiv.className = 'asset-item';
                        
                        const priceClass = asset.price > asset.vwap ? 'price-up' : 
                                         asset.price < asset.vwap ? 'price-down' : 'price-same';
                        
                        assetDiv.innerHTML = `
                            <div class="asset-symbol">${symbol}</div>
                            <div class="asset-price ${priceClass}">$${asset.price.toFixed(2)}</div>
                            <div class="asset-type">${asset.type}</div>
                            <div style="font-size: 0.8em; color: #666;">
                                VWAP: $${asset.vwap.toFixed(2)}<br>
                                RSI: ${asset.rsi.toFixed(1)}<br>
                                Volume: ${asset.volume.toLocaleString()}
                            </div>
                        `;
                        
                        grid.appendChild(assetDiv);
                    });
                }
                
                function updateTradesList(trades) {
                    const tradesDiv = document.getElementById('tradesList');
                    
                    if (trades.length === 0) {
                        tradesDiv.innerHTML = '<div class="loading">No trades yet</div>';
                        return;
                    }
                    
                    tradesDiv.innerHTML = '';
                    const recentTrades = trades.slice(-10).reverse(); // Show last 10 trades
                    
                    recentTrades.forEach(trade => {
                        const tradeDiv = document.createElement('div');
                        tradeDiv.className = `trade-item trade-${trade.side.toLowerCase()}`;
                        
                        const timestamp = new Date(trade.timestamp).toLocaleTimeString();
                        const pnlClass = trade.pnl > 0 ? 'price-up' : trade.pnl < 0 ? 'price-down' : 'price-same';
                        
                        tradeDiv.innerHTML = `
                            <strong>${trade.symbol}</strong> ${trade.side} ${trade.quantity} @ $${trade.price.toFixed(2)}<br>
                            <small>${timestamp} | Fees: $${trade.fees.toFixed(2)} | P&L: <span class="${pnlClass}">$${trade.pnl.toFixed(2)}</span></small>
                        `;
                        
                        tradesDiv.appendChild(tradeDiv);
                    });
                }
                
                function updateNewsEvents(news) {
                    const newsDiv = document.getElementById('newsEvents');
                    
                    if (news.length === 0) {
                        newsDiv.innerHTML = '<div class="loading">Waiting for market events...</div>';
                        return;
                    }
                    
                    newsDiv.innerHTML = '';
                    news.forEach(event => {
                        const newsDiv = document.createElement('div');
                        newsDiv.className = `news-item news-${event.impact}`;
                        
                        const timestamp = new Date(event.timestamp).toLocaleTimeString();
                        newsDiv.innerHTML = `
                            <strong>${event.event}</strong><br>
                            <small>${timestamp} | Impact: ${event.impact}</small>
                        `;
                        
                        document.getElementById('newsEvents').appendChild(newsDiv);
                    });
                }
                
                function updateCharts(data) {
                    // Update performance chart
                    if (data.performance_history && data.performance_history.length > 0) {
                        const labels = data.performance_history.map(p => 
                            new Date(p.timestamp).toLocaleTimeString()
                        );
                        const values = data.performance_history.map(p => p.total_value);
                        
                        performanceChart.data.labels = labels;
                        performanceChart.data.datasets[0].data = values;
                        performanceChart.update();
                    }
                    
                    // Update price chart
                    if (data.price_history && data.price_history.AAPL && data.price_history.BTC) {
                        const aaplData = data.price_history.AAPL.slice(-20);
                        const btcData = data.price_history.BTC.slice(-20);
                        
                        const labels = aaplData.map(p => 
                            new Date(p.timestamp).toLocaleTimeString()
                        );
                        
                        priceChart.data.labels = labels;
                        priceChart.data.datasets[0].data = aaplData.map(p => p.price);
                        priceChart.data.datasets[1].data = btcData.map(p => p.price);
                        priceChart.update();
                    }
                }
                
                function startSimulator() {
                    fetch('/api/start')
                        .then(response => response.json())
                        .then(data => {
                            console.log('Trading simulator started');
                            if (!updateInterval) {
                                updateInterval = setInterval(updateDashboard, 1000);
                            }
                            updateDashboard();
                        })
                        .catch(error => console.error('Error starting simulator:', error));
                }
                
                function stopSimulator() {
                    fetch('/api/stop')
                        .then(response => response.json())
                        .then(data => {
                            console.log('Trading simulator stopped');
                            if (updateInterval) {
                                clearInterval(updateInterval);
                                updateInterval = null;
                            }
                            updateDashboard();
                        })
                        .catch(error => console.error('Error stopping simulator:', error));
                }
                
                // Initialize dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    initializeCharts();
                    updateDashboard();
                });
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_api_response(self, data):
        """Send JSON API response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def start_trading_dashboard(port=8001):
    """Start the trading dashboard."""
    with socketserver.TCPServer(("", port), TradingDashboardHandler) as httpd:
        print(f"🚀 AI Trading Dashboard started at http://localhost:{port}")
        print("📊 Multi-Asset Trading Simulator with Real-Time Data")
        print("🎯 Features: VWAP + RSI Strategies, Risk Management, Live Charts")
        print("⏹️  Press Ctrl+C to stop")
        
        # Start simulator update thread
        def update_simulator():
            while True:
                trading_simulator.update_market_data()
                time.sleep(1)
        
        update_thread = threading.Thread(target=update_simulator, daemon=True)
        update_thread.start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Stopping trading dashboard...")
            trading_simulator.stop()


if __name__ == "__main__":
    print("🚀 Starting AI Trading Simulator Dashboard...")
    start_trading_dashboard()
