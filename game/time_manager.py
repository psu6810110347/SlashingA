"""
Time Manager Module
Tracks and manages game time
"""

from kivy.clock import Clock

class TimeManager:
    """Manages game time and duration"""
    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0
        self.is_running = False
        
    def start_game_timer(self):
        """Reset and start the timer"""
        self.start_time = Clock.get_time()
        self.elapsed_time = 0
        self.is_running = True
        
    def pause_timer(self):
        """Pause the timer"""
        self.is_running = False
        
    def resume_timer(self):
        """Resume the timer, adjusting start_time"""
        if not self.is_running:
            self.start_time = Clock.get_time() - self.elapsed_time
            self.is_running = True
            
    def update(self):
        """Update elapsed time if running"""
        if self.is_running:
            self.elapsed_time = Clock.get_time() - self.start_time
            
    def get_game_state(self):
        """Return the current time state"""
        self.update() 
        minutes = int(self.elapsed_time) // 60
        seconds = int(self.elapsed_time) % 60
        return {
            'elapsed_time': self.elapsed_time,
            'formatted_time': f"{minutes:02d}:{seconds:02d}"
        }
