#!/usr/bin/env python3
"""
AI Trading Simulator - Quick Demo Script

This script demonstrates the core capabilities of the AI Trading Simulator
without requiring the full web dashboard.
"""

import time
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from trading_dashboard import TradingSimulator
    SIMULATOR_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: Full simulator not available, running basic demo...")
    SIMULATOR_AVAILABLE = False


def run_basic_demo():
    """Run a basic demo with simple market data simulation."""
    print("🚀 AI Trading Simulator - Basic Demo")
    print("=" * 50)
    
    # Simulate basic market data
    assets = {
        'AAPL': {'price': 175.50, 'volume': 45000000},
        'MSFT': {'price': 338.20, 'volume': 22000000},
        'BTC': {'price': 43250.00, 'volume': 280000},
    }
    
    print("📊 Initial Market Data:")
    for symbol, data in assets.items():
        print(f"  {symbol}: ${data['price']:,.2f} | Volume: {data['volume']:,}")
    
    print("\n🔄 Simulating Market Movements...")
    
    # Simulate some price movements
    for i in range(5):
        print(f"\n⏰ Update {i+1}:")
        for symbol in assets:
            # Simple random price movement
            import random
            change = random.uniform(-0.02, 0.02)  # ±2% change
            old_price = assets[symbol]['price']
            new_price = old_price * (1 + change)
            assets[symbol]['price'] = new_price
            
            change_pct = (change * 100)
            change_symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            print(f"  {symbol}: ${old_price:,.2f} → ${new_price:,.2f} ({change_pct:+.2f}%) {change_symbol}")
        
        time.sleep(1)  # Pause between updates
    
    print("\n✅ Basic demo completed!")


def run_full_demo():
    """Run the full simulator demo."""
    print("🚀 AI Trading Simulator - Full Demo")
    print("=" * 50)
    
    # Create simulator instance
    simulator = TradingSimulator()
    
    print("📊 Initial Portfolio:")
    print(f"  Cash: ${simulator.portfolio['cash']:,.2f}")
    print(f"  Total Value: ${simulator.portfolio['total_value']:,.2f}")
    print(f"  Risk Level: {simulator.portfolio['risk_level']}")
    print(f"  Max Position Size: {simulator.portfolio['max_position_size']*100}%")
    print(f"  Daily Loss Limit: {simulator.portfolio['daily_loss_limit']*100}%")
    
    print("\n🎯 Assets Available:")
    for symbol, asset in simulator.assets.items():
        print(f"  {symbol}: ${asset['price']:,.2f} | {asset['type'].title()} | {asset['sector']}")
    
    print("\n🚀 Starting Simulator...")
    simulator.start()
    
    # Run simulation for a few cycles
    print("\n📈 Running Simulation (5 cycles)...")
    for i in range(5):
        simulator.update_market_data()
        status = simulator.get_status()
        
        print(f"\n⏰ Cycle {i+1} - {status['timestamp']}:")
        print(f"  Market Sentiment: {status['market_sentiment']}")
        print(f"  Portfolio Value: ${status['portfolio']['total_value']:,.2f}")
        print(f"  Daily P&L: ${status['portfolio']['daily_pnl']:,.2f}")
        
        # Show some asset price changes
        if i > 0:  # Skip first cycle
            for symbol in ['AAPL', 'MSFT', 'BTC']:
                if symbol in status['price_history'] and len(status['price_history'][symbol]) >= 2:
                    prices = status['price_history'][symbol]
                    if len(prices) >= 2:
                        old_price = prices[-2]
                        new_price = prices[-1]
                        change = new_price - old_price
                        change_pct = (change / old_price) * 100
                        change_symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                        print(f"    {symbol}: ${old_price:,.2f} → ${new_price:,.2f} ({change_pct:+.2f}%) {change_symbol}")
        
        time.sleep(1)
    
    print("\n🛑 Stopping Simulator...")
    simulator.stop()
    
    print("\n📊 Final Results:")
    final_status = simulator.get_status()
    print(f"  Final Portfolio Value: ${final_status['portfolio']['total_value']:,.2f}")
    print(f"  Total P&L: ${final_status['portfolio']['total_pnl']:,.2f}")
    print(f"  Win Rate: {final_status['portfolio']['win_rate']:.1f}%")
    print(f"  Max Drawdown: {final_status['portfolio']['max_drawdown']:.2f}%")
    
    print("\n✅ Full demo completed!")


def main():
    """Main demo function."""
    print("🎯 AI Trading Simulator - Demo Mode")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--basic":
        run_basic_demo()
    elif SIMULATOR_AVAILABLE:
        try:
            run_full_demo()
        except Exception as e:
            print(f"\n❌ Error running full demo: {e}")
            print("🔄 Falling back to basic demo...")
            run_basic_demo()
    else:
        run_basic_demo()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("\n💡 To run the full web dashboard:")
    print("   python3 trading_dashboard.py")
    print("\n💡 To run the simple terminal demo:")
    print("   python3 simple_demo.py")
    print("\n💡 To run tests:")
    print("   python3 tests/test_basic.py")
    print("\n🚀 Happy trading!")


if __name__ == "__main__":
    main()
