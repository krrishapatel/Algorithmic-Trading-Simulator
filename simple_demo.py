#!/usr/bin/env python3
"""
Simple demo of the trading simulator core concepts.
This version works without external dependencies.
"""

import time
import random
from datetime import datetime


class SimpleMarketData:
    """Simplified market data for demo."""
    
    def __init__(self, symbol: str, initial_price: float = 100.0):
        self.symbol = symbol
        self.current_price = initial_price
        self.volume = 1000000
        self.timestamp = time.time()
    
    def generate_data(self):
        """Generate simulated market data."""
        # Simulate price movement
        price_change = random.uniform(-0.02, 0.02)  # ±2% change
        self.current_price *= (1 + price_change)
        self.current_price = max(self.current_price, 1.0)
        
        # Simulate volume
        volume_change = random.uniform(-0.1, 0.1)
        self.volume = max(int(self.volume * (1 + volume_change)), 100000)
        
        return {
            'symbol': self.symbol,
            'price': self.current_price,
            'volume': self.volume,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }


class SimpleVWAPStrategy:
    """Simplified VWAP strategy for demo."""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.position = 0
        self.vwap_values = []
        self.total_volume = 0
        self.total_price_volume = 0
        self.trades = 0
        self.pnl = 0.0
        
    def update_vwap(self, price: float, volume: int):
        """Update VWAP calculation."""
        self.total_volume += volume
        self.total_price_volume += price * volume
        
        if self.total_volume > 0:
            current_vwap = self.total_price_volume / self.total_volume
            self.vwap_values.append(current_vwap)
            
            # Keep only last 10 values
            if len(self.vwap_values) > 10:
                self.vwap_values.pop(0)
    
    def generate_signal(self, current_price: float, volume: int):
        """Generate trading signal."""
        self.update_vwap(current_price, volume)
        
        if len(self.vwap_values) < 5:
            return None
        
        current_vwap = self.vwap_values[-1]
        price_deviation = (current_price - current_vwap) / current_vwap
        
        # Simple signal logic
        if price_deviation < -0.01 and self.position <= 0:  # Buy signal
            return "BUY"
        elif price_deviation > 0.01 and self.position >= 0:  # Sell signal
            return "SELL"
        
        return None
    
    def execute_trade(self, signal: str, price: float):
        """Execute a trade."""
        if signal == "BUY" and self.position <= 0:
            quantity = 100
            self.position += quantity
            self.pnl -= price * quantity
            self.trades += 1
            return f"Bought {quantity} shares at ${price:.2f}"
        
        elif signal == "SELL" and self.position >= 0:
            quantity = 100
            self.position -= quantity
            self.pnl += price * quantity
            self.trades += 1
            return f"Sold {quantity} shares at ${price:.2f}"
        
        return None


def run_simple_demo():
    """Run the simple demo."""
    print("🤖 Simple Trading Simulator Demo")
    print("=" * 50)
    
    # Create strategy
    strategy = SimpleVWAPStrategy("AAPL")
    
    # Create market data
    market_data = SimpleMarketData("AAPL", initial_price=150.0)
    
    print("📊 Starting simulation...")
    print("📈 Real-time data will be displayed below:")
    print("-" * 80)
    
    start_time = time.time()
    data_points = 0
    
    try:
        while time.time() - start_time < 20:  # Run for 20 seconds
            # Generate market data
            data = market_data.generate_data()
            
            # Generate trading signal
            signal = strategy.generate_signal(data['price'], data['volume'])
            
            # Execute trade if signal exists
            trade_result = None
            if signal:
                trade_result = strategy.execute_trade(signal, data['price'])
            
            # Display current status
            current_vwap = strategy.vwap_values[-1] if strategy.vwap_values else 0
            print(f"[{data['timestamp']}] AAPL: ${data['price']:.2f} | "
                  f"Volume: {data['volume']:,} | "
                  f"VWAP: ${current_vwap:.2f} | "
                  f"Position: {strategy.position} | "
                  f"P&L: ${strategy.pnl:.2f}")
            
            if trade_result:
                print(f"   💰 {trade_result}")
            
            data_points += 1
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    
    # Display final results
    print("\n📊 Demo Results:")
    print("=" * 30)
    print(f"Data Points Processed: {data_points}")
    print(f"Total Trades: {strategy.trades}")
    print(f"Final Position: {strategy.position}")
    print(f"Total P&L: ${strategy.pnl:.2f}")
    
    if strategy.vwap_values:
        print(f"Final VWAP: ${strategy.vwap_values[-1]:.2f}")
    
    print("\n🎉 Simple demo completed!")
    print("\n💡 This demonstrates:")
    print("   - Real-time market data simulation")
    print("   - VWAP calculation and signal generation")
    print("   - Basic trading logic and position management")
    print("   - Performance tracking")


if __name__ == "__main__":
    try:
        run_simple_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
