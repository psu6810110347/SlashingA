"""
Events and Callbacks Module
Contains all callback functions for the game
"""

from kivy.core.window import Window


class CallbackManager:
    """Manages all game callbacks and events"""
    
    def __init__(self, app_ref=None):
        """
        Initialize callback manager
        
        Args:
            app_ref: Reference to main app for screen switching
        """
        self.app = app_ref
        self.game_state = {
            'is_paused': False,
            'is_in_combat': False,
            'player_hp': 100,
            'player_max_hp': 100,
            'enemy_hp': 50,
            'enemy_max_hp': 50,
        }
    
    # Menu Callbacks
    def on_start_game(self, instance):
        """Callback for start game button"""
        print("Starting game...")
        if self.app:
            self.app.show_game_screen()
        self.game_state['is_paused'] = False
    
    def on_quit_game(self, instance):
        """Callback for quit game button"""
        print("Quitting game...")
        if self.app:
            self.app.stop()
    
    def on_return_to_menu(self, instance):
        """Callback for return to menu"""
        print("Returning to menu...")
        if self.app:
            self.app.show_menu_screen()
        self.game_state['is_paused'] = False
    
    def on_quit_to_menu(self, instance):
        """Callback for quit to menu from pause"""
        print("Quitting to menu...")
        if self.app:
            self.app.show_menu_screen()
        self.game_state['is_paused'] = False
    
    # Game Callbacks
    def on_attack(self, instance):
        """Callback for attack action"""
        print("Player attacking...")
        if not self.game_state['is_paused']:
            self.game_state['enemy_hp'] -= 10
            if self.game_state['enemy_hp'] < 0:
                self.game_state['enemy_hp'] = 0
            print(f"Enemy HP: {self.game_state['enemy_hp']}")
    
    def on_use_skill(self, instance):
        """Callback for using skill"""
        print("Using skill...")
        if not self.game_state['is_paused']:
            self.game_state['enemy_hp'] -= 25
            if self.game_state['enemy_hp'] < 0:
                self.game_state['enemy_hp'] = 0
            print(f"Enemy HP after skill: {self.game_state['enemy_hp']}")
    
    def on_pause(self, instance):
        """Callback for pause button"""
        print("Pausing game...")
        self.game_state['is_paused'] = not self.game_state['is_paused']
        if self.app:
            if self.game_state['is_paused']:
                if self.app.game_manager:
                    self.app.game_manager.time_manager.pause()
            self.app.toggle_pause_menu()
    
    def on_resume(self, instance):
        """Callback for resume game"""
        print("Resuming game...")
        self.game_state['is_paused'] = False
        if self.app and self.app.game_manager:
            self.app.game_manager.time_manager.resume()
    
    def on_settings(self, instance):
        """Callback for settings button"""
        print("Opening settings...")
    
    # Additional Callbacks
    def on_item_drop(self, item_id):
        """Callback for item drop event"""
        print(f"Item dropped: {item_id}")
    
    def on_level_up(self, player_level):
        """Callback for level up event"""
        print(f"Player leveled up to: {player_level}")
    
    def on_enemy_defeated(self, enemy_id):
        """Callback for enemy defeated event"""
        print(f"Enemy defeated: {enemy_id}")
    
    def get_game_state(self):
        """Get current game state"""
        return self.game_state
    
    def update_player_hp(self, amount):
        """Update player HP"""
        self.game_state['player_hp'] += amount
        if self.game_state['player_hp'] > self.game_state['player_max_hp']:
            self.game_state['player_hp'] = self.game_state['player_max_hp']
        if self.game_state['player_hp'] < 0:
            self.game_state['player_hp'] = 0
        return self.game_state['player_hp']
    
    def update_enemy_hp(self, amount):
        """Update enemy HP"""
        self.game_state['enemy_hp'] += amount
        if self.game_state['enemy_hp'] > self.game_state['enemy_max_hp']:
            self.game_state['enemy_hp'] = self.game_state['enemy_max_hp']
        if self.game_state['enemy_hp'] < 0:
            self.game_state['enemy_hp'] = 0
        return self.game_state['enemy_hp']
