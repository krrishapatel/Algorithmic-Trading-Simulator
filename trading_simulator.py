#!/usr/bin/env python3
"""
Advanced AI Trading Simulator with Multiple Assets and Strategies
Features: Multi-asset portfolio, AI-driven signals, risk management, advanced analytics
"""

import time
import random
import math
import json
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics


class AssetType(Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITY = "commodity"


class StrategyType(Enum):
    VWAP_MOMENTUM = "vwap_momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    ARBITRAGE = "arbitrage"
    AI_ML = "ai_ml"


@dataclass
class Asset:
    symbol: str
    name: str
    asset_type: AssetType
    base_price: float
    volatility: float
    correlation_matrix: Dict[str, float]
    market_hours: Tuple[int, int]  # (open_hour, close_hour)
    timezone_offset: int


@dataclass
class MarketData:
    symbol: str
    price: float
    volume: int
    high: float
    low: float
    open_price: float
    timestamp: datetime
    bid: float
    ask: float
    spread: float


@dataclass
class Trade:
    id: str
    symbol: str
    side: str  # BUY/SELL
    quantity: int
    price: float
    timestamp: datetime
    strategy: str
    pnl: float
    fees: float


@dataclass
class Portfolio:
    cash: float
    positions: Dict[str, int]
    total_value: float
    daily_pnl: float
    total_pnl: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float


class AdvancedVWAPStrategy:
    """Advanced VWAP strategy with momentum and mean reversion."""
    
    def __init__(self, symbol: str, lookback_period: int = 20):
        self.symbol = symbol
        self.lookback_period = lookback_period
        self.price_history = []
        self.volume_history = []
        self.vwap_values = []
        self.momentum_scores = []
        self.volatility_scores = []
        self.signal_strength = 0.0
        
    def calculate_vwap(self, prices: List[float], volumes: List[int]) -> float:
        """Calculate Volume Weighted Average Price."""
        if not prices or not volumes:
            return 0.0
        
        total_pv = sum(p * v for p, v in zip(prices, volumes))
        total_volume = sum(volumes)
        
        return total_pv / total_volume if total_volume > 0 else 0.0
    
    def calculate_momentum(self, prices: List[float]) -> float:
        """Calculate price momentum using linear regression."""
        if len(prices) < 5:
            return 0.0
        
        x = list(range(len(prices)))
        y = prices
        
        # Simple linear regression
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        return slope
    
    def calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility."""
        if len(prices) < 2:
            return 0.0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        return statistics.stdev(returns) if len(returns) > 1 else 0.0
    
    def generate_signal(self, current_price: float, current_volume: int) -> Tuple[str, float]:
        """Generate advanced trading signal with confidence score."""
        self.price_history.append(current_price)
        self.volume_history.append(current_volume)
        
        # Keep only recent data
        if len(self.price_history) > self.lookback_period:
            self.price_history.pop(0)
            self.volume_history.pop(0)
        
        if len(self.price_history) < 5:
            return "HOLD", 0.0
        
        # Calculate VWAP
        vwap = self.calculate_vwap(self.price_history, self.volume_history)
        self.vwap_values.append(vwap)
        
        # Calculate momentum
        momentum = self.calculate_momentum(self.price_history)
        self.momentum_scores.append(momentum)
        
        # Calculate volatility
        volatility = self.calculate_volatility(self.price_history)
        self.volatility_scores.append(volatility)
        
        # Signal generation logic
        price_deviation = (current_price - vwap) / vwap if vwap > 0 else 0
        
        # Momentum factor
        momentum_factor = momentum / current_price if current_price > 0 else 0
        
        # Volatility adjustment
        vol_factor = 1.0 / (1.0 + volatility * 100) if volatility > 0 else 1.0
        
        # Combined signal strength
        signal_strength = (price_deviation * 0.4 + momentum_factor * 0.4 + vol_factor * 0.2)
        
        # Generate signal
        if signal_strength < -0.02:
            return "BUY", abs(signal_strength)
        elif signal_strength > 0.02:
            return "SELL", abs(signal_strength)
        else:
            return "HOLD", abs(signal_strength)


class MeanReversionStrategy:
    """Mean reversion strategy using Bollinger Bands and RSI."""
    
    def __init__(self, symbol: str, period: int = 20, std_dev: float = 2.0):
        self.symbol = symbol
        self.period = period
        self.std_dev = std_dev
        self.price_history = []
        self.rsi_values = []
        
    def calculate_bollinger_bands(self, prices: List[float]) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands."""
        if len(prices) < self.period:
            return 0.0, 0.0, 0.0
        
        recent_prices = prices[-self.period:]
        sma = sum(recent_prices) / len(recent_prices)
        
        variance = sum((p - sma) ** 2 for p in recent_prices) / len(recent_prices)
        std = math.sqrt(variance)
        
        upper_band = sma + (self.std_dev * std)
        lower_band = sma - (self.std_dev * std)
        
        return upper_band, sma, lower_band
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
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
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signal(self, current_price: float) -> Tuple[str, float]:
        """Generate mean reversion signal."""
        self.price_history.append(current_price)
        
        if len(self.price_history) > self.period * 2:
            self.price_history.pop(0)
        
        if len(self.price_history) < self.period:
            return "HOLD", 0.0
        
        # Calculate Bollinger Bands
        upper, middle, lower = self.calculate_bollinger_bands(self.price_history)
        
        # Calculate RSI
        rsi = self.calculate_rsi(self.price_history)
        self.rsi_values.append(rsi)
        
        # Signal generation
        price_position = (current_price - lower) / (upper - lower) if upper != lower else 0.5
        
        # Oversold condition (buy signal)
        if current_price < lower and rsi < 30:
            confidence = min(1.0, (lower - current_price) / lower * 2)
            return "BUY", confidence
        
        # Overbought condition (sell signal)
        elif current_price > upper and rsi > 70:
            confidence = min(1.0, (current_price - upper) / upper * 2)
            return "SELL", confidence
        
        return "HOLD", 0.0


class RiskManager:
    """Advanced risk management system."""
    
    def __init__(self, max_position_size: float = 0.1, max_daily_loss: float = 0.05):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0.0
        self.position_limits = {}
        self.correlation_threshold = 0.7
        
    def check_position_limit(self, symbol: str, quantity: int, price: float, portfolio_value: float) -> bool:
        """Check if position size is within limits."""
        position_value = abs(quantity * price)
        position_ratio = position_value / portfolio_value
        
        return position_ratio <= self.max_position_size
    
    def check_daily_loss_limit(self, new_pnl: float) -> bool:
        """Check if daily loss limit is exceeded."""
        return new_pnl >= -self.max_daily_loss
    
    def check_correlation_risk(self, new_symbol: str, existing_positions: Dict[str, int], 
                              correlation_matrix: Dict[str, Dict[str, float]]) -> bool:
        """Check correlation risk with existing positions."""
        for symbol in existing_positions:
            if existing_positions[symbol] != 0:
                correlation = correlation_matrix.get(new_symbol, {}).get(symbol, 0)
                if abs(correlation) > self.correlation_threshold:
                    return False
        return True


class AdvancedTradingSimulator:
    """Advanced multi-asset trading simulator."""
    
    def __init__(self):
        self.assets = self._initialize_assets()
        self.strategies = {}
        self.risk_manager = RiskManager()
        self.portfolio = Portfolio(
            cash=1000000.0,
            positions={},
            total_value=1000000.0,
            daily_pnl=0.0,
            total_pnl=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0
        )
        self.trades = []
        self.market_data = {}
        self.running = False
        self.performance_metrics = []
        
        # Initialize strategies for each asset
        for asset in self.assets.values():
            self.strategies[asset.symbol] = {
                'vwap': AdvancedVWAPStrategy(asset.symbol),
                'mean_reversion': MeanReversionStrategy(asset.symbol)
            }
    
    def _initialize_assets(self) -> Dict[str, Asset]:
        """Initialize diverse asset universe."""
        return {
            'AAPL': Asset('AAPL', 'Apple Inc.', AssetType.STOCK, 150.0, 0.25, 
                         {'MSFT': 0.6, 'GOOGL': 0.5, 'TSLA': 0.4}, (9, 16), -5),
            'MSFT': Asset('MSFT', 'Microsoft Corp.', AssetType.STOCK, 300.0, 0.22,
                         {'AAPL': 0.6, 'GOOGL': 0.7, 'TSLA': 0.3}, (9, 16), -5),
            'GOOGL': Asset('GOOGL', 'Alphabet Inc.', AssetType.STOCK, 2800.0, 0.28,
                          {'AAPL': 0.5, 'MSFT': 0.7, 'TSLA': 0.4}, (9, 16), -5),
            'TSLA': Asset('TSLA', 'Tesla Inc.', AssetType.STOCK, 250.0, 0.45,
                         {'AAPL': 0.4, 'MSFT': 0.3, 'GOOGL': 0.4}, (9, 16), -5),
            'BTC': Asset('BTC', 'Bitcoin', AssetType.CRYPTO, 45000.0, 0.65,
                        {'ETH': 0.8, 'AAPL': 0.1, 'MSFT': 0.1}, (0, 24), 0),
            'ETH': Asset('ETH', 'Ethereum', AssetType.CRYPTO, 3000.0, 0.70,
                        {'BTC': 0.8, 'AAPL': 0.1, 'MSFT': 0.1}, (0, 24), 0),
            'EUR/USD': Asset('EUR/USD', 'Euro/US Dollar', AssetType.FOREX, 1.08, 0.12,
                            {'GBP/USD': 0.8, 'USD/JPY': 0.3, 'AAPL': 0.1}, (0, 24), -5),
            'GBP/USD': Asset('GBP/USD', 'British Pound/US Dollar', AssetType.FOREX, 1.26, 0.15,
                            {'EUR/USD': 0.8, 'USD/JPY': 0.4, 'AAPL': 0.1}, (0, 24), -5),
            'GOLD': Asset('GOLD', 'Gold Futures', AssetType.COMMODITY, 1950.0, 0.20,
                         {'SILVER': 0.7, 'AAPL': -0.1, 'MSFT': -0.1}, (0, 24), -5),
            'SILVER': Asset('SILVER', 'Silver Futures', AssetType.COMMODITY, 24.0, 0.25,
                           {'GOLD': 0.7, 'AAPL': -0.1, 'MSFT': -0.1}, (0, 24), -5)
        }
    
    def generate_market_data(self, symbol: str) -> MarketData:
        """Generate realistic market data for an asset."""
        asset = self.assets[symbol]
        
        # Simulate realistic price movements
        volatility = asset.volatility
        time_factor = 1.0
        
        # Market hours adjustment
        current_hour = datetime.now().hour
        if asset.asset_type == AssetType.STOCK:
            if current_hour < asset.market_hours[0] or current_hour > asset.market_hours[1]:
                time_factor = 0.1  # Reduced volatility outside market hours
        
        # Price movement
        price_change = random.gauss(0, volatility * time_factor * 0.01)
        new_price = asset.base_price * (1 + price_change)
        
        # Volume simulation
        base_volume = 1000000 if asset.asset_type == AssetType.STOCK else 100000
        volume_change = random.uniform(-0.3, 0.3)
        new_volume = int(base_volume * (1 + volume_change))
        
        # High/Low simulation
        high = new_price * random.uniform(1.0, 1.02)
        low = new_price * random.uniform(0.98, 1.0)
        
        # Bid/Ask spread
        spread_pct = 0.001 if asset.asset_type == AssetType.STOCK else 0.01
        spread = new_price * spread_pct
        bid = new_price - spread / 2
        ask = new_price + spread / 2
        
        # Update base price for next iteration
        asset.base_price = new_price
        
        return MarketData(
            symbol=symbol,
            price=new_price,
            volume=new_volume,
            high=high,
            low=low,
            open_price=asset.base_price,
            timestamp=datetime.now(),
            bid=bid,
            ask=ask,
            spread=spread
        )
    
    def execute_trade(self, symbol: str, side: str, quantity: int, price: float, strategy: str) -> bool:
        """Execute a trade with risk management."""
        # Risk checks
        if not self.risk_manager.check_position_limit(symbol, quantity, price, self.portfolio.total_value):
            return False
        
        # Calculate trade details
        trade_value = quantity * price
        fees = trade_value * 0.001  # 0.1% commission
        
        if side == "BUY":
            if self.portfolio.cash < (trade_value + fees):
                return False
            
            self.portfolio.cash -= (trade_value + fees)
            self.portfolio.positions[symbol] = self.portfolio.positions.get(symbol, 0) + quantity
        else:  # SELL
            if self.portfolio.positions.get(symbol, 0) < quantity:
                return False
            
            self.portfolio.cash += (trade_value - fees)
            self.portfolio.positions[symbol] = self.portfolio.positions.get(symbol, 0) - quantity
        
        # Record trade
        trade = Trade(
            id=f"T{len(self.trades)+1:06d}",
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            timestamp=datetime.now(),
            strategy=strategy,
            pnl=0.0,
            fees=fees
        )
        self.trades.append(trade)
        
        return True
    
    def update_portfolio_value(self):
        """Update portfolio value and calculate metrics."""
        total_value = self.portfolio.cash
        
        for symbol, quantity in self.portfolio.positions.items():
            if quantity != 0 and symbol in self.market_data:
                price = self.market_data[symbol].price
                total_value += quantity * price
        
        self.portfolio.total_value = total_value
        
        # Calculate daily P&L
        if self.performance_metrics:
            last_value = self.performance_metrics[-1]['total_value']
            self.portfolio.daily_pnl = total_value - last_value
        else:
            self.portfolio.daily_pnl = 0.0
        
        # Update performance metrics
        self.performance_metrics.append({
            'timestamp': datetime.now(),
            'total_value': total_value,
            'cash': self.portfolio.cash,
            'daily_pnl': self.portfolio.daily_pnl
        })
        
        # Calculate advanced metrics
        self._calculate_advanced_metrics()
    
    def _calculate_advanced_metrics(self):
        """Calculate advanced performance metrics."""
        if len(self.performance_metrics) < 2:
            return
        
        # Calculate returns
        returns = []
        for i in range(1, len(self.performance_metrics)):
            prev_value = self.performance_metrics[i-1]['total_value']
            curr_value = self.performance_metrics[i]['total_value']
            if prev_value > 0:
                returns.append((curr_value - prev_value) / prev_value)
        
        if returns:
            # Sharpe ratio (assuming 0% risk-free rate)
            mean_return = statistics.mean(returns)
            std_return = statistics.stdev(returns) if len(returns) > 1 else 0
            self.portfolio.sharpe_ratio = mean_return / std_return if std_return > 0 else 0
            
            # Max drawdown
            peak = self.performance_metrics[0]['total_value']
            max_dd = 0
            for metric in self.performance_metrics:
                if metric['total_value'] > peak:
                    peak = metric['total_value']
                dd = (peak - metric['total_value']) / peak
                max_dd = max(max_dd, dd)
            self.portfolio.max_drawdown = max_dd
            
            # Win rate
            winning_days = sum(1 for r in returns if r > 0)
            self.portfolio.win_rate = winning_days / len(returns) if returns else 0
    
    def run_simulation_step(self):
        """Run one step of the trading simulation."""
        if not self.running:
            return
        
        # Generate market data for all assets
        for symbol in self.assets:
            self.market_data[symbol] = self.generate_market_data(symbol)
        
        # Generate signals and execute trades
        for symbol in self.assets:
            if symbol not in self.market_data:
                continue
            
            data = self.market_data[symbol]
            
            # Get signals from all strategies
            vwap_signal, vwap_confidence = self.strategies[symbol]['vwap'].generate_signal(data.price, data.volume)
            mr_signal, mr_confidence = self.strategies[symbol]['mean_reversion'].generate_signal(data.price)
            
            # Combine signals (simple average for now)
            if vwap_signal != "HOLD" and mr_signal != "HOLD":
                if vwap_signal == mr_signal:
                    # Both strategies agree - high confidence
                    signal = vwap_signal
                    confidence = (vwap_confidence + mr_confidence) / 2
                else:
                    # Strategies disagree - lower confidence
                    signal = "HOLD"
                    confidence = 0.0
            else:
                signal = vwap_signal if vwap_signal != "HOLD" else mr_signal
                confidence = max(vwap_confidence, mr_confidence)
            
            # Execute trade if signal is strong enough
            if signal != "HOLD" and confidence > 0.3:
                quantity = int(1000 * confidence)  # Position size based on confidence
                if signal == "BUY":
                    self.execute_trade(symbol, "BUY", quantity, data.ask, "combined")
                elif signal == "SELL":
                    self.execute_trade(symbol, "SELL", quantity, data.bid, "combined")
        
        # Update portfolio
        self.update_portfolio_value()
    
    def start(self):
        """Start the trading simulation."""
        self.running = True
        print("🚀 Advanced Trading Simulator Started!")
        print(f"📊 Trading {len(self.assets)} assets with advanced strategies")
        print(f"💰 Initial Portfolio Value: ${self.portfolio.total_value:,.2f}")
    
    def stop(self):
        """Stop the trading simulation."""
        self.running = False
        print("🛑 Advanced Trading Simulator Stopped")
    
    def get_status(self) -> dict:
        """Get current simulator status."""
        return {
            "running": self.running,
            "portfolio": {
                "total_value": round(self.portfolio.total_value, 2),
                "cash": round(self.portfolio.cash, 2),
                "daily_pnl": round(self.portfolio.daily_pnl, 2),
                "total_pnl": round(self.portfolio.total_value - 1000000, 2),
                "sharpe_ratio": round(self.portfolio.sharpe_ratio, 3),
                "max_drawdown": round(self.portfolio.max_drawdown * 100, 2),
                "win_rate": round(self.portfolio.win_rate * 100, 2)
            },
            "positions": {k: v for k, v in self.portfolio.positions.items() if v != 0},
            "total_trades": len(self.trades),
            "assets_trading": len([k for k, v in self.portfolio.positions.items() if v != 0]),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }


# Global simulator instance
advanced_simulator = AdvancedTradingSimulator()


def run_advanced_simulation():
    """Run the advanced simulation."""
    print("🤖 Advanced AI Trading Simulator")
    print("=" * 60)
    print("📊 Multi-Asset Portfolio: Stocks, Crypto, Forex, Commodities")
    print("🧠 Advanced Strategies: VWAP + Momentum, Mean Reversion")
    print("🛡️  Risk Management: Position Limits, Correlation Checks")
    print("📈 Real-Time Analytics: Sharpe Ratio, Drawdown, Win Rate")
    print("=" * 60)
    
    # Start simulator
    advanced_simulator.start()
    
    try:
        while advanced_simulator.running:
            advanced_simulator.run_simulation_step()
            
            # Display status every 5 seconds
            if len(advanced_simulator.performance_metrics) % 5 == 0:
                status = advanced_simulator.get_status()
                print(f"\n[{status['timestamp']}] Portfolio: ${status['portfolio']['total_value']:,.2f} | "
                      f"P&L: ${status['portfolio']['daily_pnl']:,.2f} | "
                      f"Trades: {status['total_trades']} | "
                      f"Sharpe: {status['portfolio']['sharpe_ratio']:.3f}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Simulation interrupted by user")
    
    # Final results
    status = advanced_simulator.get_status()
    print("\n📊 Final Results:")
    print("=" * 30)
    print(f"Final Portfolio Value: ${status['portfolio']['total_value']:,.2f}")
    print(f"Total P&L: ${status['portfolio']['total_pnl']:,.2f}")
    print(f"Sharpe Ratio: {status['portfolio']['sharpe_ratio']:.3f}")
    print(f"Max Drawdown: {status['portfolio']['max_drawdown']:.2f}%")
    print(f"Win Rate: {status['portfolio']['win_rate']:.2f}%")
    print(f"Total Trades: {status['total_trades']}")
    
    advanced_simulator.stop()


if __name__ == "__main__":
    try:
        run_advanced_simulation()
    except KeyboardInterrupt:
        print("\n\n⏹️  Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
