"""
ICT Trading Signal Alert System
Real-time alerts for institutional trading patterns with multiple notification channels
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import json
from enum import Enum
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass, asdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging


# ============= SIGNAL DEFINITIONS =============

class SignalType(Enum):
    """Types of ICT trading signals"""
    BUY = "BUY"
    SELL = "SELL"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"
    LIQUIDATION_HUNT = "LIQUIDATION_HUNT"
    ORDER_BLOCK = "ORDER_BLOCK"
    SUPPORT_BOUNCE = "SUPPORT_BOUNCE"
    RESISTANCE_BOUNCE = "RESISTANCE_BOUNCE"
    BREAKOUT = "BREAKOUT"
    REVERSAL = "REVERSAL"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AlertChannel(Enum):
    """Alert delivery channels"""
    CONSOLE = "console"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE = "file"
    TELEGRAM = "telegram"
    DISCORD = "discord"


@dataclass
class TradingSignal:
    """Data class for trading signals"""
    timestamp: datetime
    pair: str
    signal_type: SignalType
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float  # 0-100
    strength: float    # 0-10
    description: str
    indicators: Dict
    timeframe: str = "4H"
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'pair': self.pair,
            'signal_type': self.signal_type.value,
            'entry_price': float(self.entry_price),
            'stop_loss': float(self.stop_loss),
            'take_profit': float(self.take_profit),
            'confidence': float(self.confidence),
            'strength': float(self.strength),
            'description': self.description,
            'indicators': self.indicators,
            'timeframe': self.timeframe
        }


@dataclass
class AlertConfig:
    """Configuration for alert system"""
    min_confidence: float = 70.0
    min_strength: float = 6.0
    enable_console: bool = True
    enable_email: bool = False
    enable_sms: bool = False
    enable_webhook: bool = False
    enable_file: bool = True
    
    # Email configuration
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_sender: str = ""
    email_sender_password: str = ""
    email_recipients: List[str] = None
    
    # Webhook configuration
    webhook_url: str = ""
    
    # File configuration
    log_file_path: str = "./trading_alerts.log"
    json_export_path: str = "./trading_signals.json"


# ============= ALERT CHANNELS =============

class ConsoleAlertHandler:
    """Handle console alerts with formatting and colors"""
    
    @staticmethod
    def send_alert(signal: TradingSignal, severity: AlertSeverity):
        """Send alert to console"""
        colors = {
            AlertSeverity.LOW: '\033[36m',      # Cyan
            AlertSeverity.MEDIUM: '\033[33m',   # Yellow
            AlertSeverity.HIGH: '\033[91m',     # Red
            AlertSeverity.CRITICAL: '\033[95m'  # Magenta
        }
        reset = '\033[0m'
        
        color = colors.get(severity, '')
        
        timestamp = signal.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        alert_msg = f"""
{color}
╔══════════════════════════════════════════════════════╗
║                   TRADING ALERT SIGNAL               ║
╚══════════════════════════════════════════════════════╝
┌─ SIGNAL DETAILS ─────────────────────────────────────┐
│ Time:           {timestamp}
│ Pair:           {signal.pair}
│ Timeframe:      {signal.timeframe}
│ Signal Type:    {signal.signal_type.value}
│ Severity:       {severity.name}
├─ ENTRY INFORMATION ──────────────────────────────────┤
│ Entry Price:    {signal.entry_price:.5f}
│ Stop Loss:      {signal.stop_loss:.5f}
│ Take Profit:    {signal.take_profit:.5f}
│ Risk/Reward:    1:{(signal.take_profit - signal.entry_price) / (signal.entry_price - signal.stop_loss):.2f}
├─ SIGNAL QUALITY ──────────────────────────────────────┤
│ Confidence:     {signal.confidence:.1f}%
│ Strength:       {signal.strength:.1f}/10
│ Description:    {signal.description}
├─ KEY INDICATORS ──────────────────────────────────────┤
{ConsoleAlertHandler._format_indicators(signal.indicators)}
└───────────────────────────────────────────────────────┘
{reset}
"""
        print(alert_msg)
    
    @staticmethod
    def _format_indicators(indicators: Dict) -> str:
        """Format indicators for display"""
        lines = []
        for key, value in indicators.items():
            if isinstance(value, float):
                lines.append(f"│ {key:.<25} {value:.4f}")
            else:
                lines.append(f"│ {key:.<25} {value}")
        return "\n".join(lines)


class EmailAlertHandler:
    """Handle email alerts"""
    
    def __init__(self, config: AlertConfig):
        self.config = config
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for email alerts"""
        self.logger = logging.getLogger('email_alerts')
        handler = logging.FileHandler('email_alerts.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def send_alert(self, signal: TradingSignal, severity: AlertSeverity):
        """Send alert via email"""
        if not self.config.email_recipients:
            self.logger.warning("No email recipients configured")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.email_sender
            msg['To'] = ', '.join(self.config.email_recipients)
            msg['Subject'] = f"[{severity.name}] {signal.signal_type.value} Signal - {signal.pair}"
            
            # Create body
            body = self._create_email_body(signal, severity)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port) as server:
                server.starttls()
                server.login(self.config.email_sender, self.config.email_sender_password)
                server.send_message(msg)
            
            self.logger.info(f"Email alert sent for {signal.pair} {signal.signal_type.value}")
        
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def _create_email_body(self, signal: TradingSignal, severity: AlertSeverity) -> str:
        """Create HTML email body"""
        timestamp = signal.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        risk_reward = (signal.take_profit - signal.entry_price) / (signal.entry_price - signal.stop_loss)
        
        indicators_html = "".join([
            f"<tr><td>{key}</td><td>{value if not isinstance(value, float) else f'{value:.4f}'}</td></tr>"
            for key, value in signal.indicators.items()
        ])
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #2C3E50; color: white; padding: 20px; }}
                .content {{ padding: 20px; background-color: #ECF0F1; }}
                .section {{ margin-bottom: 20px; border: 1px solid #BDC3C7; padding: 15px; background-color: white; }}
                .section-title {{ font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #2C3E50; }}
                table {{ width: 100%; border-collapse: collapse; }}
                td {{ padding: 8px; border-bottom: 1px solid #BDC3C7; }}
                .signal-buy {{ color: #27AE60; font-weight: bold; }}
                .signal-sell {{ color: #E74C3C; font-weight: bold; }}
                .severity-critical {{ color: #8B0000; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔔 Trading Alert - ICT Signal</h2>
                    <p>Severity: <span class="severity-{severity.name.lower()}">{severity.name}</span></p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <div class="section-title">SIGNAL DETAILS</div>
                        <table>
                            <tr><td>Time</td><td>{timestamp}</td></tr>
                            <tr><td>Pair</td><td><strong>{signal.pair}</strong></td></tr>
                            <tr><td>Timeframe</td><td>{signal.timeframe}</td></tr>
                            <tr><td>Signal Type</td><td><strong class="signal-{signal.signal_type.value.lower()}">{signal.signal_type.value}</strong></td></tr>
                        </table>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">ENTRY INFORMATION</div>
                        <table>
                            <tr><td>Entry Price</td><td><strong>{signal.entry_price:.5f}</strong></td></tr>
                            <tr><td>Stop Loss</td><td>{signal.stop_loss:.5f}</td></tr>
                            <tr><td>Take Profit</td><td>{signal.take_profit:.5f}</td></tr>
                            <tr><td>Risk/Reward Ratio</td><td>1:{risk_reward:.2f}</td></tr>
                        </table>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">SIGNAL QUALITY</div>
                        <table>
                            <tr><td>Confidence</td><td>{signal.confidence:.1f}%</td></tr>
                            <tr><td>Strength</td><td>{signal.strength:.1f}/10</td></tr>
                            <tr><td>Description</td><td>{signal.description}</td></tr>
                        </table>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">KEY INDICATORS</div>
                        <table>
                            {indicators_html}
                        </table>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


class FileAlertHandler:
    """Handle file-based alerts"""
    
    def __init__(self, config: AlertConfig):
        self.config = config
    
    def send_alert(self, signal: TradingSignal, severity: AlertSeverity):
        """Save alert to file"""
        try:
            # Append to log file
            with open(self.config.log_file_path, 'a') as f:
                timestamp = signal.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                log_line = (
                    f"[{timestamp}] [{severity.name}] {signal.pair} - "
                    f"{signal.signal_type.value} @ {signal.entry_price:.5f} "
                    f"(Confidence: {signal.confidence:.1f}%, Strength: {signal.strength:.1f}/10)\n"
                )
                f.write(log_line)
            
            # Append to JSON file
            self._append_json_signal(signal, severity)
        
        except Exception as e:
            print(f"Error writing alert to file: {e}")
    
    def _append_json_signal(self, signal: TradingSignal, severity: AlertSeverity):
        """Append signal to JSON file"""
        try:
            # Load existing data
            try:
                with open(self.config.json_export_path, 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {'signals': []}
            
            # Add new signal
            signal_dict = signal.to_dict()
            signal_dict['severity'] = severity.name
            data['signals'].append(signal_dict)
            data['last_updated'] = datetime.now().isoformat()
            data['total_signals'] = len(data['signals'])
            
            # Save
            with open(self.config.json_export_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"Error writing to JSON: {e}")


class WebhookAlertHandler:
    """Handle webhook alerts"""
    
    def __init__(self, config: AlertConfig):
        self.config = config
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for webhook alerts"""
        self.logger = logging.getLogger('webhook_alerts')
        handler = logging.FileHandler('webhook_alerts.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def send_alert(self, signal: TradingSignal, severity: AlertSeverity):
        """Send alert via webhook"""
        if not self.config.webhook_url:
            self.logger.warning("No webhook URL configured")
            return
        
        try:
            import requests
            
            payload = {
                'timestamp': signal.timestamp.isoformat(),
                'pair': signal.pair,
                'signal_type': signal.signal_type.value,
                'entry_price': float(signal.entry_price),
                'stop_loss': float(signal.stop_loss),
                'take_profit': float(signal.take_profit),
                'confidence': float(signal.confidence),
                'strength': float(signal.strength),
                'severity': severity.name,
                'description': signal.description,
                'indicators': signal.indicators
            }
            
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.info(f"Webhook alert sent successfully for {signal.pair}")
            else:
                self.logger.warning(f"Webhook returned status {response.status_code}")
        
        except ImportError:
            self.logger.error("requests library not installed for webhook")
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {e}")


# ============= ALERT MANAGER =============

class ICTAlertManager:
    """
    Main alert manager for ICT trading signals
    Handles multiple alert channels and signal detection
    """
    
    def __init__(self, config: AlertConfig = None):
        self.config = config or AlertConfig()
        self.signal_history = []
        self.handlers = {}
        self.signal_callbacks = []
        self.is_monitoring = False
        
        self._initialize_handlers()
        self.setup_logging()
    
    def _initialize_handlers(self):
        """Initialize alert handlers based on config"""
        if self.config.enable_console:
            self.handlers[AlertChannel.CONSOLE] = ConsoleAlertHandler()
        
        if self.config.enable_email:
            self.handlers[AlertChannel.EMAIL] = EmailAlertHandler(self.config)
        
        if self.config.enable_file:
            self.handlers[AlertChannel.FILE] = FileAlertHandler(self.config)
        
        if self.config.enable_webhook:
            self.handlers[AlertChannel.WEBHOOK] = WebhookAlertHandler(self.config)
    
    def setup_logging(self):
        """Setup logging"""
        self.logger = logging.getLogger('alert_manager')
        if not self.logger.handlers:
            handler = logging.FileHandler('alert_manager.log')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def register_signal_callback(self, callback: Callable):
        """Register callback for signal detection"""
        self.signal_callbacks.append(callback)
    
    def detect_and_alert(self, signal: TradingSignal) -> bool:
        """
        Detect signal and send alerts
        
        Returns:
            bool: True if alert was sent, False otherwise
        """
        # Check confidence and strength thresholds
        if signal.confidence < self.config.min_confidence:
            self.logger.debug(f"Signal confidence {signal.confidence} below threshold")
            return False
        
        if signal.strength < self.config.min_strength:
            self.logger.debug(f"Signal strength {signal.strength} below threshold")
            return False
        
        # Determine severity
        severity = self._calculate_severity(signal)
        
        # Store in history
        self.signal_history.append({
            'signal': signal,
            'severity': severity,
            'timestamp': datetime.now()
        })
        
        # Send alerts through all enabled handlers
        self._send_alerts(signal, severity)
        
        # Trigger callbacks
        for callback in self.signal_callbacks:
            try:
                callback(signal, severity)
            except Exception as e:
                self.logger.error(f"Error in signal callback: {e}")
        
        return True
    
    def _calculate_severity(self, signal: TradingSignal) -> AlertSeverity:
        """Calculate alert severity based on signal properties"""
        score = 0
        
        # Confidence score
        if signal.confidence >= 90:
            score += 2
        elif signal.confidence >= 80:
            score += 1
        
        # Strength score
        if signal.strength >= 9:
            score += 2
        elif signal.strength >= 7:
            score += 1
        
        # Signal type score
        if signal.signal_type in [SignalType.STRONG_BUY, SignalType.STRONG_SELL]:
            score += 1
        
        # Risk/Reward ratio
        if signal.entry_price != signal.stop_loss:
            ratio = abs(signal.take_profit - signal.entry_price) / abs(signal.entry_price - signal.stop_loss)
            if ratio >= 3:
                score += 1
        
        # Map score to severity
        if score >= 5:
            return AlertSeverity.CRITICAL
        elif score >= 4:
            return AlertSeverity.HIGH
        elif score >= 2:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _send_alerts(self, signal: TradingSignal, severity: AlertSeverity):
        """Send alerts through enabled handlers"""
        for channel, handler in self.handlers.items():
            try:
                handler.send_alert(signal, severity)
            except Exception as e:
                self.logger.error(f"Error sending {channel.value} alert: {e}")
    
    def get_signal_summary(self) -> Dict:
        """Get summary of signals"""
        if not self.signal_history:
            return {'total': 0, 'by_type': {}, 'by_severity': {}}
        
        by_type = {}
        by_severity = {}
        
        for item in self.signal_history:
            signal = item['signal']
            severity = item['severity']
            
            signal_type = signal.signal_type.value
            by_type[signal_type] = by_type.get(signal_type, 0) + 1
            
            severity_name = severity.name
            by_severity[severity_name] = by_severity.get(severity_name, 0) + 1
        
        return {
            'total': len(self.signal_history),
            'by_type': by_type,
            'by_severity': by_severity,
            'last_signal': self.signal_history[-1] if self.signal_history else None
        }
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals"""
        recent = []
        for item in self.signal_history[-limit:]:
            signal = item['signal']
            recent.append({
                'timestamp': signal.timestamp.isoformat(),
                'pair': signal.pair,
                'signal_type': signal.signal_type.value,
                'confidence': signal.confidence,
                'strength': signal.strength,
                'severity': item['severity'].name
            })
        return recent
    
    def export_signals(self, filepath: str):
        """Export all signals to JSON file"""
        try:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'total_signals': len(self.signal_history),
                'signals': []
            }
            
            for item in self.signal_history:
                signal = item['signal']
                export_data['signals'].append({
                    'signal': signal.to_dict(),
                    'severity': item['severity'].name
                })
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Signals exported to {filepath}")
        
        except Exception as e:
            self.logger.error(f"Error exporting signals: {e}")


# ============= SIGNAL GENERATOR =============

class ICTSignalGenerator:
    """Generate ICT trading signals"""
    
    @staticmethod
    def generate_order_block_signal(
        pair: str,
        price: float,
        block_strength: float,
        confidence: float
    ) -> TradingSignal:
        """Generate order block signal"""
        entry = price
        stop_loss = price - (price * 0.005)  # 50 pips below
        take_profit = price + (price * 0.010)  # 100 pips above
        
        return TradingSignal(
            timestamp=datetime.now(),
            pair=pair,
            signal_type=SignalType.ORDER_BLOCK,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            strength=block_strength,
            description="Strong institutional order block detected",
            indicators={
                'block_strength': block_strength,
                'order_density': np.random.uniform(0.7, 0.95),
                'volume_ratio': np.random.uniform(1.2, 2.5)
            }
        )
    
    @staticmethod
    def generate_liquidity_grab_signal(
        pair: str,
        price: float,
        grab_type: str,
        confidence: float
    ) -> TradingSignal:
        """Generate liquidity grab signal"""
        is_bullish = grab_type == "bullish"
        
        entry = price
        stop_loss = price - (price * 0.003) if is_bullish else price + (price * 0.003)
        take_profit = price + (price * 0.010) if is_bullish else price - (price * 0.010)
        
        signal_type = SignalType.BUY if is_bullish else SignalType.SELL
        
        return TradingSignal(
            timestamp=datetime.now(),
            pair=pair,
            signal_type=signal_type,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            strength=8.5,
            description=f"{grab_type.capitalize()} liquidity grab detected - stops cleared",
            indicators={
                'grab_type': grab_type,
                'wick_ratio': np.random.uniform(1.5, 3.0),
                'close_direction': 'up' if is_bullish else 'down',
                'volume_spike': np.random.uniform(1.3, 2.0)
            }
        )
    
    @staticmethod
    def generate_confluence_signal(
        pair: str,
        price: float,
        indicators: Dict,
        confidence: float
    ) -> TradingSignal:
        """Generate confluence zone signal"""
        confluence_count = sum(1 for v in indicators.values() if v)
        
        if confidence >= 80:
            signal_type = SignalType.STRONG_BUY if price > 1 else SignalType.STRONG_SELL
        else:
            signal_type = SignalType.BUY if price > 1 else SignalType.SELL
        
        entry = price
        stop_loss = price - (price * 0.004)
        take_profit = price + (price * 0.012)
        
        return TradingSignal(
            timestamp=datetime.now(),
            pair=pair,
            signal_type=signal_type,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            strength=min(7 + (confluence_count * 0.3), 10),
            description=f"Confluence zone detected with {confluence_count} confluent indicators",
            indicators=indicators
        )
    
    @staticmethod
    def generate_support_resistance_signal(
        pair: str,
        price: float,
        level_type: str,
        confidence: float
    ) -> TradingSignal:
        """Generate support/resistance signal"""
        is_support = level_type == "support"
        
        entry = price
        stop_loss = price - (price * 0.006) if is_support else price + (price * 0.006)
        take_profit = price + (price * 0.015) if is_support else price - (price * 0.015)
        
        signal_type = SignalType.SUPPORT_BOUNCE if is_support else SignalType.RESISTANCE_BOUNCE
        
        return TradingSignal(
            timestamp=datetime.now(),
            pair=pair,
            signal_type=signal_type,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            strength=7.0,
            description=f"Price bouncing from {level_type} level with institutional demand",
            indicators={
                'level_type': level_type,
                'bounces': np.random.randint(2, 5),
                'volume_profile': 'high',
                'holding_strength': np.random.uniform(0.7, 0.9)
            }
        )


# ============= EXAMPLE USAGE =============

def main():
    """Main function demonstrating alert system"""
    print("="*70)
    print("ICT TRADING SIGNAL ALERT SYSTEM - DEMONSTRATION")
    print("="*70)
    print()
    
    # Setup configuration
    config = AlertConfig(
        min_confidence=75.0,
        min_strength=6.0,
        enable_console=True,
        enable_file=True,
        enable_email=False,  # Set to True with valid credentials
        email_sender="your_email@gmail.com",
        email_sender_password="your_password",
        email_recipients=["recipient@gmail.com"],
        log_file_path="./ict_trading_alerts.log",
        json_export_path="./ict_signals.json"
    )
    
    # Initialize alert manager
    print("1. Initializing Alert Manager...")
    alert_manager = ICTAlertManager(config)
    print("   ✓ Alert manager initialized\n")
    
    # Register callbacks
    print("2. Registering signal callbacks...")
    def custom_callback(signal: TradingSignal, severity):
        risk_reward = (signal.take_profit - signal.entry_price) / (signal.entry_price - signal.stop_loss)
        print(f"   [CALLBACK] Signal received: {signal.pair} - {signal.signal_type.value} - R/R: 1:{risk_reward:.2f}")
    
    alert_manager.register_signal_callback(custom_callback)
    print("   ✓ Callback registered\n")
    
    # Generate and alert on various signals
    print("3. Generating and processing trading signals...\n")
    
    signals_to_test = [
        ("Order Block Signal", ICTSignalGenerator.generate_order_block_signal(
            "EURUSD", 1.1050, 8.5, 82.0
        )),
        ("Bullish Liquidity Grab", ICTSignalGenerator.generate_liquidity_grab_signal(
            "GBPUSD", 1.3750, "bullish", 85.0
        )),
        ("Confluence Zone", ICTSignalGenerator.generate_confluence_signal(
            "USDJPY", 109.50,
            {'RSI_Oversold': True, 'Support_Level': True, 'Volume_Spike': True},
            88.0
        )),
        ("Support Bounce", ICTSignalGenerator.generate_support_resistance_signal(
            "AUDUSD", 0.7200, "support", 80.0
        )),
        ("Resistance Bounce", ICTSignalGenerator.generate_support_resistance_signal(
            "USDCAD", 1.2500, "resistance", 78.0
        )),
    ]
    
    for signal_name, signal in signals_to_test:
        print(f"\n>>> Processing: {signal_name}")
        alert_manager.detect_and_alert(signal)
        time.sleep(0.5)
    
    # Display summary
    print("\n" + "="*70)
    print("4. ALERT SYSTEM SUMMARY")
    print("="*70)
    
    summary = alert_manager.get_signal_summary()
    print(f"Total Signals Processed: {summary['total']}")
    
    if summary['by_type']:
        print("\nSignals by Type:")
        for sig_type, count in summary['by_type'].items():
            print(f"  • {sig_type}: {count}")
    
    if summary['by_severity']:
        print("\nSignals by Severity:")
        for severity, count in summary['by_severity'].items():
            print(f"  • {severity}: {count}")
    
    # Recent signals
    print("\n5. RECENT SIGNALS:")
    print("-"*70)
    recent = alert_manager.get_recent_signals(5)
    for signal in recent:
        print(f"  [{signal['timestamp']}] {signal['pair']} - {signal['signal_type']}")
        print(f"     Confidence: {signal['confidence']:.1f}% | Strength: {signal['strength']:.1f}/10")
    
    # Export signals
    print("\n6. EXPORTING SIGNALS...")
    export_path = "/mnt/user-data/outputs/ict_alert_signals_export.json"
    alert_manager.export_signals(export_path)
    print(f"   ✓ Signals exported to: {export_path}\n")
    
    # File logs
    print("7. ALERT FILES CREATED:")
    print("   ✓ ict_trading_alerts.log - Detailed alert log")
    print("   ✓ ict_signals.json - JSON signal database")
    print("   ✓ alert_manager.log - System log")
    
    print("\n" + "="*70)
    print("ALERT SYSTEM DEMONSTRATION COMPLETE")
    print("="*70)
    
    return alert_manager


if __name__ == "__main__":
    alert_manager = main()