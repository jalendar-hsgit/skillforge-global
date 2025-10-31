"""
Zoom Meeting Integration Service
"""
import requests
import jwt
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from app.core.config import settings

class ZoomService:
    """Service for creating and managing Zoom meetings"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'ZOOM_API_KEY', None)
        self.api_secret = getattr(settings, 'ZOOM_API_SECRET', None)
        self.base_url = "https://api.zoom.us/v2"
    
    def _generate_jwt_token(self) -> str:
        """Generate JWT token for Zoom API authentication"""
        if not self.api_key or not self.api_secret:
            raise ValueError("Zoom API credentials not configured")
        
        payload = {
            'iss': self.api_key,
            'exp': int(time.time() + 3600)  # Expires in 1 hour
        }
        
        token = jwt.encode(
            payload,
            self.api_secret,
            algorithm='HS256'
        )
        
        return token if isinstance(token, str) else token.decode('utf-8')
    
    def create_meeting(
        self,
        topic: str,
        start_time: datetime,
        duration_minutes: int,
        mentor_email: Optional[str] = None
    ) -> Dict:
        """
        Create a Zoom meeting
        
        Args:
            topic: Meeting topic/title
            start_time: When the meeting starts
            duration_minutes: Meeting duration in minutes
            mentor_email: Mentor's email (meeting host)
        
        Returns:
            Dict with meeting details: {
                'id': meeting_id,
                'join_url': student_join_url,
                'start_url': mentor_start_url,
                'password': meeting_password
            }
        """
        if not self.api_key or not self.api_secret:
            # Return placeholder if Zoom not configured
            return self._generate_placeholder_meeting(topic, start_time)
        
        try:
            token = self._generate_jwt_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Meeting settings
            meeting_data = {
                'topic': topic,
                'type': 2,  # Scheduled meeting
                'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'duration': duration_minutes,
                'timezone': 'UTC',
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'join_before_host': False,
                    'mute_upon_entry': True,
                    'waiting_room': True,
                    'audio': 'both',
                    'auto_recording': 'none'
                }
            }
            
            # Use mentor email as host if provided
            user_id = mentor_email if mentor_email else 'me'
            
            response = requests.post(
                f"{self.base_url}/users/{user_id}/meetings",
                headers=headers,
                json=meeting_data,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    'id': data['id'],
                    'join_url': data['join_url'],
                    'start_url': data.get('start_url', data['join_url']),
                    'password': data.get('password', '')
                }
            else:
                print(f"Zoom API error: {response.status_code} - {response.text}")
                return self._generate_placeholder_meeting(topic, start_time)
        
        except Exception as e:
            print(f"Error creating Zoom meeting: {e}")
            return self._generate_placeholder_meeting(topic, start_time)
    
    def _generate_placeholder_meeting(self, topic: str, start_time: datetime) -> Dict:
        """Generate placeholder meeting URL when Zoom is not configured"""
        meeting_id = int(start_time.timestamp())
        base_url = "https://meet.jit.si"  # Jitsi as fallback
        room_name = f"skillforge-{meeting_id}"
        
        return {
            'id': meeting_id,
            'join_url': f"{base_url}/{room_name}",
            'start_url': f"{base_url}/{room_name}",
            'password': '',
            'provider': 'jitsi'
        }
    
    def update_meeting(self, meeting_id: str, **kwargs) -> bool:
        """Update an existing meeting"""
        if not self.api_key or not self.api_secret:
            return False
        
        try:
            token = self._generate_jwt_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.patch(
                f"{self.base_url}/meetings/{meeting_id}",
                headers=headers,
                json=kwargs,
                timeout=10
            )
            
            return response.status_code == 204
        
        except Exception as e:
            print(f"Error updating Zoom meeting: {e}")
            return False
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete/cancel a meeting"""
        if not self.api_key or not self.api_secret:
            return False
        
        try:
            token = self._generate_jwt_token()
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.delete(
                f"{self.base_url}/meetings/{meeting_id}",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 204
        
        except Exception as e:
            print(f"Error deleting Zoom meeting: {e}")
            return False
    
    def get_meeting_details(self, meeting_id: str) -> Optional[Dict]:
        """Get meeting details"""
        if not self.api_key or not self.api_secret:
            return None
        
        try:
            token = self._generate_jwt_token()
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.get(
                f"{self.base_url}/meetings/{meeting_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
        
        except Exception as e:
            print(f"Error getting Zoom meeting: {e}")
            return None


# Singleton instance
zoom_service = ZoomService()
