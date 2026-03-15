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
        self.perk_counts = {
            'max_hp': 0,
            'speed': 0,
            'attack': 0,
            'defense': 0,
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
            self.app.play_bgm('audio/bgm/menu.mp3')
        self.game_state['is_paused'] = False
    

    
    # Game Callbacks
    def on_player_move(self, dx, dy):
        """Callback for player movement action"""
        # This can be used for logging, triggering movement-based events, 
        # or checking step-based mechanics in the future.
        pass

    def on_wave_start(self, wave_number, enemy_count):
        """Callback for wave start event"""
        print(f"Wave {wave_number} Started! {enemy_count} enemies approaching!")

    def on_attack(self, is_facing_right=True):
        """Callback for attack action with direction"""
        print("Player attacking...")
        if not self.game_state['is_paused']:
            if self.app and hasattr(self.app, 'game_manager') and self.app.game_manager:
                self.app.game_manager.player_attack(is_facing_right=is_facing_right)
    
    def on_pause(self, instance):
        """Callback for pause button"""
        print("Pausing game...")
        self.game_state['is_paused'] = not self.game_state['is_paused']
        if self.app:
            self.app.toggle_pause_menu()
    
    def on_resume(self, instance):
        """Callback for resume game"""
        print("Resuming game...")
        self.game_state['is_paused'] = False
        
    def on_level_up(self, player_level):
        """Callback for level up event"""
        print(f"Player leveled up to: {player_level}")
        if self.app and getattr(self.app, 'game_manager', None):
            if player_level <= 10:
                self.app.game_manager.player.score += 5
            else:
                self.app.game_manager.player.score += 10

    def on_game_over(self, state=None):
        print("Game Over!")
        if self.app:
            game_over_screen = self.app.screen_manager.get_screen('game_over')
            if state:
                game_over_screen.final_level_label.text = f"Level Reached: {state.get('level', 1)}"
                if 'time_state' in state and state['time_state']:
                    game_over_screen.final_time_label.text = f"Time Survived: {state['time_state']['formatted_time']}"
                if 'player_stats' in state and state['player_stats']:
                    gold = state['player_stats'].get('gold', 0)
                    score = state['player_stats'].get('score', 0)
                    game_over_screen.score_label.text = f"Final Score: {score}"
                    game_over_screen.gold_earned_label.text = f"Gold Earned: {gold}"
            self.app.screen_manager.current = 'game_over'
            self.app.play_bgm('audio/bgm/gameover.mp3')
            from kivy.clock import Clock
            Clock.unschedule(self.app.update_game_display)
        self.game_state['is_paused'] = True

    def on_enemy_attack(self, damage, enemy_name):
        """Callback triggered when an enemy successfully attacks the player"""
        print(f"{enemy_name} attacked for {damage} damage!")
        
    def on_boss_spawn(self, level):
        """Callback triggered when a boss spawns"""
        print(f"Boss Spawned at level {level}!")
        
    def on_settings(self, instance):
        """Callback for settings button in pause menu"""
        print("Settings menu opened")
    
    def get_game_state(self):
        """Get current game state"""
        return self.game_state
    
    def on_perk_selected(self, perk_id):
        """Callback for selecting a perk from the popup"""
        if self.app and self.app.game_manager:
            player = self.app.game_manager.player
            
            if perk_id == 'max_hp':
                player.max_hp += 10
                player.hp += 10
                self.app.game_manager.add_log("Gained +10 Max HP!")
            elif perk_id == 'attack':
                player.attack += 1
                self.app.game_manager.add_log("Gained +1 Attack Damage!")
            elif perk_id == 'speed':
                player.speed += 1
                self.app.game_manager.add_log("Gained +1 Movement Speed!")
            elif perk_id == 'defense':
                player.defense += 1
                self.app.game_manager.add_log("Gained +1 Defense!")
            
            # Update perk collection count
            if perk_id in self.perk_counts:
                self.perk_counts[perk_id] += 1
            
            # Update UI labels
            if hasattr(self.app, 'screen_manager'):
                game_screen = self.app.screen_manager.get_screen('game')
                if hasattr(game_screen, 'perk_slot_labels') and perk_id in game_screen.perk_slot_labels:
                    perk_names = {'max_hp': 'Max HP', 'speed': 'Speed', 'attack': 'Attack', 'defense': 'Defense'}
                    game_screen.perk_slot_labels[perk_id].text = f"{perk_names[perk_id]}: {self.perk_counts[perk_id]}"
                
        # Unpause the game and close the menu
        self.game_state['is_paused'] = False
        if self.app and hasattr(self.app, 'root'):
            game_screen = self.app.root.get_screen('game')
            if hasattr(game_screen, 'perk_overlay'):
                game_screen.perk_overlay.opacity = 0
                game_screen.perk_overlay.disabled = True

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

    def on_restart_game(self, instance):
        """Callback to restart the game from Game Over screen"""
        print("Restarting game...")
        if self.app:
            self.app.show_game_screen()
        self.game_state['is_paused'] = False
