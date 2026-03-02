"""
Time Management Module
Handles game time, timers, and time-based events
"""

import time
from datetime import datetime, timedelta


class TimeManager:
    """Manages game time and timers"""
    
    def __init__(self):
        """Initialize time manager"""
        self.game_start_time = None
        self.game_elapsed_time = 0
        self.is_paused = False
        self.pause_time = 0
        self.timers = {}  # Dictionary to store active timers
        self.time_scale = 1.0  # For slow-motion or speed-up effects
    
    def start_game_timer(self):
        """Start the game timer"""
        self.game_start_time = time.time()
        self.game_elapsed_time = 0
        self.is_paused = False
        print("Game timer started")
    
    def update(self):
        """Update time manager (call every frame)"""
        if self.game_start_time and not self.is_paused:
            current_time = time.time()
            self.game_elapsed_time = (current_time - self.game_start_time) * self.time_scale
        
        # Update all active timers
        self._update_timers()
    
    def pause(self):
        """Pause the game timer"""
        if not self.is_paused:
            self.is_paused = True
            self.pause_time = time.time()
            print("Game timer paused")
    
    def resume(self):
        """Resume the game timer"""
        if self.is_paused:
            pause_duration = time.time() - self.pause_time
            self.game_start_time += pause_duration
            self.is_paused = False
            print("Game timer resumed")
    
    def get_elapsed_time(self):
        """Get elapsed time in seconds"""
        return self.game_elapsed_time
    
    def get_formatted_time(self):
        """Get formatted time as MM:SS"""
        total_seconds = int(self.game_elapsed_time)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_formatted_time_hms(self):
        """Get formatted time as HH:MM:SS"""
        total_seconds = int(self.game_elapsed_time)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def create_timer(self, timer_id, duration, callback=None):
        """
        Create a timer
        
        Args:
            timer_id: Unique timer identifier
            duration: Duration in seconds
            callback: Optional callback function when timer finishes
        """
        self.timers[timer_id] = {
            'start_time': time.time(),
            'duration': duration,
            'callback': callback,
            'is_finished': False
        }
        print(f"Timer '{timer_id}' created for {duration} seconds")
    
    def _update_timers(self):
        """Update all active timers"""
        current_time = time.time()
        
        for timer_id, timer_data in self.timers.items():
            if not timer_data['is_finished']:
                elapsed = current_time - timer_data['start_time']
                
                if elapsed >= timer_data['duration']:
                    timer_data['is_finished'] = True
                    
                    # Call callback if provided
                    if timer_data['callback']:
                        timer_data['callback'](timer_id)
                    
                    print(f"Timer '{timer_id}' finished")
    
    def get_timer_remaining(self, timer_id):
        """Get remaining time for a specific timer"""
        if timer_id not in self.timers:
            return 0
        
        timer_data = self.timers[timer_id]
        if timer_data['is_finished']:
            return 0
        
        elapsed = time.time() - timer_data['start_time']
        remaining = timer_data['duration'] - elapsed
        return max(0, remaining)
    
    def is_timer_finished(self, timer_id):
        """Check if a timer is finished"""
        return timer_id in self.timers and self.timers[timer_id]['is_finished']
    
    def reset_timer(self, timer_id):
        """Reset a timer"""
        if timer_id in self.timers:
            self.timers[timer_id]['start_time'] = time.time()
            self.timers[timer_id]['is_finished'] = False
            print(f"Timer '{timer_id}' reset")
    
    def remove_timer(self, timer_id):
        """Remove a timer"""
        if timer_id in self.timers:
            del self.timers[timer_id]
            print(f"Timer '{timer_id}' removed")
    
    def clear_all_timers(self):
        """Clear all timers"""
        self.timers.clear()
        print("All timers cleared")
    
    def set_time_scale(self, scale):
        """
        Set time scale (for slow-motion or speed-up effects)
        
        Args:
            scale: Time scale multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double speed)
        """
        self.time_scale = scale
        print(f"Time scale set to {scale}x")
    
    def get_game_state(self):
        """Get time manager state"""
        return {
            'elapsed_time': self.game_elapsed_time,
            'formatted_time': self.get_formatted_time(),
            'formatted_time_hms': self.get_formatted_time_hms(),
            'is_paused': self.is_paused,
            'time_scale': self.time_scale,
            'active_timers': len([t for t in self.timers.values() if not t['is_finished']]),
        }
