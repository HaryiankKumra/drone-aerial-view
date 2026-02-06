"""
Telegram Bot Integration for Security Alerts
"""
import os
import requests
from datetime import datetime

class TelegramBot:
    def __init__(self):
        # Get from environment or .env file
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if not self.enabled:
            print("⚠️  Telegram not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
    
    def send_alert(self, event_data):
        """
        Send security alert to Telegram
        
        Args:
            event_data: Event dictionary from database
        """
        if not self.enabled:
            print("ℹ️  Telegram disabled - skipping alert")
            return False
        
        try:
            # Format message
            message = self._format_alert_message(event_data)
            
            # Send message
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram alert sent for {event_data['event_id']}")
                
                # Send snapshot if available
                if event_data.get('snapshot_url'):
                    self._send_photo(event_data['snapshot_url'], event_data['event_id'])
                
                return True
            else:
                print(f"❌ Telegram send failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def _format_alert_message(self, event):
        """Format event as Telegram message"""
        severity_emoji = {
            'HIGH': '🚨',
            'MEDIUM': '⚠️',
            'LOW': 'ℹ️'
        }
        
        emoji = severity_emoji.get(event['severity'], '📍')
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(event['timestamp'])
            time_str = dt.strftime('%H:%M:%S')
        except:
            time_str = event['timestamp']
        
        # Build message
        message = f"{emoji} <b>SECURITY ALERT</b>\n\n"
        message += f"<b>Event ID:</b> {event['event_id']}\n"
        message += f"<b>Type:</b> {event['object_type'].upper()}\n"
        message += f"<b>Severity:</b> {event['severity']}\n"
        message += f"<b>Confidence:</b> {event['confidence']:.1%}\n"
        message += f"<b>Zone:</b> {event['zone']}\n"
        message += f"<b>Time:</b> {time_str}\n"
        
        # Add location if available
        if event.get('drone_lat') and event.get('drone_lon'):
            message += f"<b>Location:</b> {event['drone_lat']:.4f}°N, {event['drone_lon']:.4f}°E\n"
        
        message += f"\n📍 Campus Guardian Drone - Aerial Surveillance"
        
        return message
    
    def _send_photo(self, photo_url, caption):
        """Send snapshot photo"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
            payload = {
                'chat_id': self.chat_id,
                'photo': photo_url,
                'caption': f"📸 Evidence: {caption}"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Telegram photo error: {e}")
            return False
    
    def test_connection(self):
        """Test Telegram bot connection"""
        if not self.enabled:
            return False, "Bot not configured"
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                bot_info = response.json()
                return True, f"Connected to @{bot_info['result']['username']}"
            else:
                return False, f"API error: {response.text}"
                
        except Exception as e:
            return False, str(e)
