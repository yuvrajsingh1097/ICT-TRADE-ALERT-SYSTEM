# ICT Trading Signal Alert System - Complete Guide

## 📋 Overview

The **ICT Trading Signal Alert System** is a professional-grade alert management platform for institutional trading pattern detection. It monitors multiple currency pairs, detects ICT signals, and sends real-time alerts through multiple channels.

### Key Features:
✅ **Real-time Signal Detection** - Monitors 10+ signal types  
✅ **Multi-Channel Alerts** - Console, Email, SMS, Webhook, File, JSON  
✅ **Severity Calculation** - Automatic risk assessment  
✅ **Web Dashboard** - Beautiful real-time monitoring interface  
✅ **Signal History** - Complete audit trail with JSON export  
✅ **Risk/Reward Analysis** - Automatic ratio calculation  
✅ **Confidence Scoring** - 0-100% confidence levels  

---

## 🎯 Signal Types Supported

### 1. **BUY / SELL Signals**
- Standard directional signals
- Based on price action and institutional clues
- Risk/Reward: 1:2 to 1:3

### 2. **STRONG_BUY / STRONG_SELL**
- High-confidence institutional signals
- Multiple indicator confluence
- Risk/Reward: 1:3 to 1:5

### 3. **ORDER_BLOCK**
- Zones where institutional orders clustered
- Price respects these levels
- Typical Risk/Reward: 1:2 to 1:2.5

### 4. **LIQUIDITY_HUNT / LIQUIDATION_HUNT**
- Stops being cleared before major moves
- Bullish: New low + close high
- Bearish: New high + close low

### 5. **SUPPORT_BOUNCE / RESISTANCE_BOUNCE**
- Price bouncing from key levels
- Institutional demand/supply zones
- Risk/Reward: 1:2 to 1:3

### 6. **BREAKOUT**
- Price breaking through key resistance/support
- High volume confirmation
- Risk/Reward: 1:2 to 1:4

### 7. **REVERSAL**
- Price reversing from major levels
- Market structure break
- Risk/Reward: 1:2.5 to 1:5

---



### Basic Usage

```python
from ict_alert_system import ICTAlertManager, AlertConfig, SignalType, TradingSignal
from datetime import datetime

# Setup configuration
config = AlertConfig(
    min_confidence=75.0,
    min_strength=6.0,
    enable_console=True,
    enable_file=True,
    enable_email=False
)

# Initialize manager
alert_manager = ICTAlertManager(config)

# Create a signal
signal = TradingSignal(
    timestamp=datetime.now(),
    pair="EURUSD",
    signal_type=SignalType.ORDER_BLOCK,
    entry_price=1.1050,
    stop_loss=1.0995,
    take_profit=1.1160,
    confidence=82.0,
    strength=8.5,
    description="Strong order block at institutional level",
    indicators={'volume_ratio': 2.17, 'order_density': 0.84}
)

# Send alert
alert_manager.detect_and_alert(signal)
```

---

## 📧 Alert Channels

### 1. **Console Alerts**
- Beautiful formatted output
- Color-coded by severity
- Real-time notifications
- Best for: Live trading, monitoring

```python
config.enable_console = True
```

**Output:**
```
╔══════════════════════════════════════════════════════╗
║                   TRADING ALERT SIGNAL               ║
╚══════════════════════════════════════════════════════╝
┌─ SIGNAL DETAILS ─────────────────────────────────────┐
│ Time:           2026-04-20 12:30:45
│ Pair:           EURUSD
│ Signal Type:    ORDER_BLOCK
│ Severity:       MEDIUM
├─ ENTRY INFORMATION ──────────────────────────────────┤
│ Entry Price:    1.10500
│ Stop Loss:      1.09947
│ Take Profit:    1.11605
│ Risk/Reward:    1:2.00
...
```

### 2. **Email Alerts**
- HTML-formatted emails
- Detailed signal information
- Risk/reward ratios
- Indicator data

```python
config.enable_email = True
config.email_sender = "your_email@gmail.com"
config.email_sender_password = "your_app_password"
config.email_recipients = ["recipient@gmail.com"]
```

### 3. **File Logging**
- Detailed text log file
- JSON signal database
- Complete audit trail
- Searchable and archivable

```python
config.enable_file = True
config.log_file_path = "./trading_alerts.log"
config.json_export_path = "./signals.json"
```

### 4. **Webhook Integration**
- POST requests to custom endpoints
- Integration with Discord, Slack, Telegram
- Custom application logic
- Real-time data pipeline

```python
config.enable_webhook = True
config.webhook_url = "https://your-webhook-endpoint.com/alerts"
```

### 5. **SMS Alerts** (Coming Soon)
- Twilio integration
- Critical signal notifications
- Mobile push notifications

### 6. **Telegram/Discord** (Customizable)
- Bot integration
- Channel-based alerts
- Group notifications
- Easy implementation

---

## ⚙️ Configuration

### AlertConfig Object

```python
config = AlertConfig(
    # Signal thresholds
    min_confidence=70.0,      # 0-100%
    min_strength=6.0,         # 0-10
    
    # Alert channels
    enable_console=True,
    enable_email=False,
    enable_sms=False,
    enable_webhook=False,
    enable_file=True,
    
    # Email settings
    email_smtp_server="smtp.gmail.com",
    email_smtp_port=587,
    email_sender="your_email@gmail.com",
    email_sender_password="your_app_password",
    email_recipients=["recipient1@gmail.com", "recipient2@gmail.com"],
    
    # Webhook settings
    webhook_url="https://your-server.com/webhook",
    
    # File settings
    log_file_path="./trading_alerts.log",
    json_export_path="./signals.json"
)
```

---

## 📊 Severity Levels

Alerts are automatically categorized by severity:

### CRITICAL (🔴)
- Confidence ≥ 90%
- Strength ≥ 9/10
- Risk/Reward ≥ 3:1
- Action: Immediate attention required

### HIGH (🟠)
- Confidence ≥ 80%
- Strength ≥ 7/10
- Risk/Reward ≥ 2.5:1
- Action: Review and consider entry

### MEDIUM (🟡)
- Confidence ≥ 70%
- Strength ≥ 6/10
- Risk/Reward ≥ 2:1
- Action: Monitor closely

### LOW (🔵)
- Confidence < 70%
- Strength < 6/10
- Risk/Reward < 2:1
- Action: Informational only

---

## 🎨 Web Dashboard

### Features
- Real-time signal monitoring
- Signal statistics (total, buy, sell)
- Activity feed
- Signal distribution chart
- Confidence visualization
- Responsive design

### Access
1. Open `ict_alert_dashboard.html` in browser
2. View live signal data
3. Filter by signal type
4. Auto-refreshes every 5 seconds

### Dashboard Sections
```
┌─ Header: System Status & Live Indicator ─┐
├─ Statistics Cards (Total, Buy, Sell, Avg Confidence) ─┤
├─ Signal Table (Filterable) ─┤
├─ Activity Feed ─┤
├─ Distribution Chart ─┤
└─ Footer: Last Updated Time ─┘
```

---

## 🔧 Advanced Usage

### Custom Callbacks

```python
def my_callback(signal: TradingSignal, severity: AlertSeverity):
    """Custom callback for signal processing"""
    if severity == AlertSeverity.CRITICAL:
        # Execute trade
        place_order(signal)
    elif severity == AlertSeverity.HIGH:
        # Send notification
        send_notification(signal)

alert_manager.register_signal_callback(my_callback)
```

### Integration with Trading Platform

```python
# MetaTrader 5 Integration
import MetaTrader5 as mt5

def mt5_callback(signal: TradingSignal, severity: AlertSeverity):
    if signal.signal_type == SignalType.BUY:
        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': signal.pair,
            'volume': calculate_lot_size(signal),
            'type': mt5.ORDER_TYPE_BUY,
            'price': signal.entry_price,
            'sl': signal.stop_loss,
            'tp': signal.take_profit,
        }
        result = mt5.order_send(request)

alert_manager.register_signal_callback(mt5_callback)
```

### Signal Filtering

```python
 Only high-confidence signals
if signal.confidence >= 85:
    alert_manager.detect_and_alert(signal)

# Only high risk/reward
ratio = (signal.take_profit - signal.entry_price) / (signal.entry_price - signal.stop_loss)
if ratio >= 3.0:
    alert_manager.detect_and_alert(signal)
```

---

## 📈 Signal Generator

### Generating Signals

```python
from ict_alert_system import ICTSignalGenerator

# Order block signal
signal = ICTSignalGenerator.generate_order_block_signal(
    pair="EURUSD",
    price=1.1050,
    block_strength=8.5,
    confidence=82.0
)

# Liquidity grab signal
signal = ICTSignalGenerator.generate_liquidity_grab_signal(
    pair="GBPUSD",
    price=1.3750,
    grab_type="bullish",
    confidence=85.0
)

# Support/Resistance signal
signal = ICTSignalGenerator.generate_support_resistance_signal(
    pair="AUDUSD",
    price=0.7200,
    level_type="support",
    confidence=80.0
)
```

---

## 📊 Data Export

### JSON Export

```python
# Automatic export on each signal
# File: signals.json

{
  "export_time": "2026-04-20T12:30:45.123456",
  "total_signals": 5,
  "signals": [
    {
      "signal": {
        "timestamp": "2026-04-20T12:30:45",
        "pair": "EURUSD",
        "signal_type": "ORDER_BLOCK",
        "entry_price": 1.1050,
        "stop_loss": 1.09947,
        "take_profit": 1.11605,
        "confidence": 82.0,
        "strength": 8.5
      },
      "severity": "MEDIUM"
    }
  ]
}
```

### Log File Format

```
[2026-04-20 12:30:45] [MEDIUM] EURUSD - ORDER_BLOCK @ 1.10500 (Confidence: 82.0%, Strength: 8.5/10)
[2026-04-20 12:31:12] [MEDIUM] GBPUSD - BUY @ 1.37500 (Confidence: 85.0%, Strength: 8.5/10)
[2026-04-20 12:32:00] [HIGH] USDJPY - STRONG_BUY @ 109.50000 (Confidence: 88.0%, Strength: 7.9/10)
```

---

## 🔍 Signal Summary & Analytics

```python
# Get signal summary
summary = alert_manager.get_signal_summary()

print(f"Total: {summary['total']}")
print(f"By Type: {summary['by_type']}")
print(f"By Severity: {summary['by_severity']}")

# Get recent signals
recent = alert_manager.get_recent_signals(limit=10)

# Export all signals
alert_manager.export_signals("my_signals.json")
```

---

## ⚠️ Best Practices

### 1. **Threshold Management**
- Set `min_confidence` to 75%+ for live trading
- Require `min_strength` of 6.0+
- Adjust based on your risk tolerance

### 2. **Alert Prioritization**
- Only act on CRITICAL and HIGH severity alerts
- Review MEDIUM alerts before trading
- Ignore LOW alerts unless confirming other signals

### 3. **Risk Management**
- Always use stop losses from signal
- Don't risk more than 1-2% per trade
- Use the provided Risk/Reward ratio
- Check confluence before entering

### 4. **Monitoring**
- Check dashboard every 15-30 minutes
- Keep email alerts on during trading hours
- Review log files daily
- Monitor signal accuracy

### 5. **Optimization**
- Track which signal types perform best
- Adjust thresholds based on backtests
- Test on paper trading first
- Keep detailed trading journal

---

## 🐛 Troubleshooting

### Email Alerts Not Sending
**Problem**: Emails not received
**Solution**: 
- Enable "Less secure apps" in Gmail
- Use App Password instead of account password
- Check SMTP settings (use 587, not 465)
- Verify recipient email address

### Dashboard Not Updating
**Problem**: Dashboard shows no signals
**Solution**:
- Check if `enable_file` is True
- Verify JSON file path is correct
- Clear browser cache (Ctrl+Shift+Del)
- Check browser console for errors

### Webhook Failures
**Problem**: Webhook alerts not received
**Solution**:
- Verify webhook URL is correct
- Check firewall/network connectivity
- Test with curl command
- Review webhook server logs

### Signals Not Detected
**Problem**: No alerts generated
**Solution**:
- Check confidence threshold (default 70%)
- Verify strength threshold (default 6.0)
- Ensure signal criteria are met
- Review signal quality

---

## 📝 Complete Example

```python
from ict_alert_system import (
    ICTAlertManager, AlertConfig, SignalType, TradingSignal,
    ICTSignalGenerator, AlertSeverity
)
from datetime import datetime
import time

# Configuration
config = AlertConfig(
    min_confidence=75.0,
    min_strength=6.5,
    enable_console=True,
    enable_file=True,
    enable_email=True,
    email_sender="your_email@gmail.com",
    email_sender_password="your_app_password",
    email_recipients=["trader@example.com"],
    log_file_path="./trading_alerts.log",
    json_export_path="./signals.json"
)

# Initialize
alert_manager = ICTAlertManager(config)

# Custom callback
def trading_callback(signal: TradingSignal, severity: AlertSeverity):
    print(f"\n🚀 TRADING ACTION: {signal.signal_type.value} {signal.pair}")
    print(f"   Entry: {signal.entry_price:.5f}")
    print(f"   SL: {signal.stop_loss:.5f} | TP: {signal.take_profit:.5f}")

alert_manager.register_signal_callback(trading_callback)

# Monitor multiple pairs
pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']

# Simulate signals
for i in range(3):
    for pair in pairs:
        # Generate random signal
        signal = ICTSignalGenerator.generate_order_block_signal(
            pair=pair,
            price=np.random.uniform(0.7, 1.5),
            block_strength=np.random.uniform(7, 10),
            confidence=np.random.uniform(75, 95)
        )
        
        # Process alert
        alert_manager.detect_and_alert(signal)
    
    # Wait between cycles
    time.sleep(1)

# Get summary
summary = alert_manager.get_signal_summary()
print(f"\nTotal signals: {summary['total']}")
print(f"By type: {summary['by_type']}")
```

---

## 🎓 Learning Path

**Beginner**: Run basic example, explore console alerts  
**Intermediate**: Setup email alerts, use dashboard  
**Advanced**: Custom callbacks, platform integration  
**Expert**: Deploy with real market data, optimize thresholds  

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review signal generation code
3. Check alert configuration
4. Review log files for errors
5. Test with manual signals

---

## 🎉 Summary

The ICT Trading Signal Alert System provides:
- ✅ Real-time institutional signal detection
- ✅ Multi-channel alert delivery
- ✅ Beautiful web dashboard
- ✅ Comprehensive signal history
- ✅ Risk/reward analysis
- ✅ Professional-grade monitoring

**Ready to receive your first trading alert!** 🚀



alert system can be modified and used as a siren 




Technology Stack
Backend:

Python 3.8+
Flask (API)
Pandas (Data)
SQLAlchemy (ORM)
Pytest (Testing)

Data:

JSON (Config & signals)
CSV (Historical data)
PostgreSQL (Optional)
Redis (Optional caching)

Deployment:

Docker ready
Cloud compatible
Scalable architecture





CTAlertManager class
10+ signal types
6 alert channel handlers
Auto severity calculation
Signal history management
