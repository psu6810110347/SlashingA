import time

class TimeManager:
    """Manages game time and events"""
    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0
        self.is_running = False
        
    def start_game_timer(self):
        """Start the timer"""
        self.start_time = time.time()
        self.elapsed_time = 0
        self.is_running = True
        
    def pause(self):
        """Pause the timer"""
        self.is_running = False
        
    def resume(self):
        """Resume the timer"""
        if not self.is_running:
            self.start_time = time.time() - self.elapsed_time
            self.is_running = True
            
    def update(self):
        """Update elapsed time"""
        if self.is_running:
            self.elapsed_time = time.time() - self.start_time
            
    def get_game_state(self):
        """Get formatted time"""
        self.update()
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        return {
            'elapsed_time': self.elapsed_time,
            'formatted_time': f"{minutes:02d}:{seconds:02d}"
        }
