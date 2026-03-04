"""
Hack and Slash Game - Main Entry Point
Built with Kivy Framework
"""

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

from ui.widgets import MainMenuScreen, GameScreen, PauseMenuPopup
from events.callbacks import CallbackManager
from game.game_logic import GameManager

# Set window size
Window.size = (1280, 720)
Window.title = "SlashingA"


class HackAndSlashApp(App):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = ScreenManager()
        self.callback_manager = None
        self.game_manager = None
        self.pause_menu = None
        self.pressed_keys = set()
        self.active_attacks = []
        self.perk_menu = None
    
    def build(self):
        """Build the application"""
        # Initialize managers
        self.callback_manager = CallbackManager(self)
        self.game_manager = GameManager()
        
        # Create main menu screen
        menu_screen = MainMenuScreen(
            callback_manager=self.callback_manager
        )
        menu_screen.name = 'menu'
        self.screen_manager.add_widget(menu_screen)
        
        # Create game screen
        game_screen = GameScreen(
            callback_manager=self.callback_manager
        )
        game_screen.name = 'game'
        self.screen_manager.add_widget(game_screen)
        
        # Set default screen
        self.screen_manager.current = 'menu'
        
        # Bind keyboard and mouse events
        Window.bind(
            on_key_down=self.on_key_down,
            on_key_up=self.on_key_up,
            on_touch_down=self.on_touch_down
        )
        
        return self.screen_manager
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle key press"""
        if codepoint in ['w', 'a', 's', 'd']:
            self.pressed_keys.add(codepoint)
            
        if key == 27:  # ESC key
            self.callback_manager.on_return_to_menu(None)
            return True
        elif codepoint == 'p':  # P key
            self.callback_manager.on_pause(None)
            return True
        return False
        
    def on_key_up(self, window, key, scancode):
        """Handle key release"""
        key_char_map = {119: 'w', 97: 'a', 115: 's', 100: 'd'}
        if key in key_char_map:
            char = key_char_map[key]
            if char in self.pressed_keys:
                self.pressed_keys.remove(char)
        return False

    def on_touch_down(self, window, touch):
        """Handle mouse clicks"""
        if self.screen_manager.current == 'game' and not self.callback_manager.game_state['is_paused']:
            if touch.button == 'left':
                px = self.game_manager.player.position[0] + 10
                py = self.game_manager.player.position[1] + 10
                dx = touch.x - px
                dy = touch.y - py
                dist = (dx**2 + dy**2)**0.5
                attack_range = 30
                if dist > 0:
                    dx /= dist
                    dy /= dist
                
                attack_x = px + (dx * attack_range)
                attack_y = py + (dy * attack_range)
                
                self.active_attacks.append((attack_x, attack_y, Clock.get_time()))
                self.callback_manager.on_attack(None)
            return True
        return False
    
    def show_menu_screen(self):
        """Switch to menu screen"""
        self.screen_manager.current = 'menu'
    
    def show_game_screen(self):
        """Switch to game screen"""
        self.game_manager.start_new_game()
        self.game_manager.player.position = [Window.width / 2, Window.height / 2]
        self.screen_manager.current = 'game'
        # Update game display frequently (60 FPS)
        Clock.schedule_interval(self.update_game_display, 1.0 / 60.0)
    
    def update_game_display(self, dt):
        """Update game display"""
        game_screen = self.screen_manager.get_screen('game')
        state = self.game_manager.get_game_state()
        
        if state['player_stats']:
            stats = state['player_stats']
            game_screen.level_label.text = f"Level: {stats['level']}"
            game_screen.side_hp_label.text = f"HP: {stats['hp']}/{stats['max_hp']}"
            game_screen.side_atk_label.text = f"Attack: {stats['attack']}"
            game_screen.side_def_label.text = f"Defense: {stats['defense']}"
            game_screen.side_spd_label.text = f"Speed: {stats['speed']}"
        
        if 'time_state' in state and state['time_state']:
            game_screen.time_label.text = f"Time: {state['time_state']['formatted_time']}"
        
        if not self.callback_manager.game_state['is_paused']:
            # Handle player movement
            dx, dy = 0, 0
            if 'w' in self.pressed_keys: dy += 1
            if 's' in self.pressed_keys: dy -= 1
            if 'a' in self.pressed_keys: dx -= 1
            if 'd' in self.pressed_keys: dx += 1
            
            if dx != 0 and dy != 0:
                length = (dx**2 + dy**2)**0.5
                dx /= length
                dy /= length
            
            player = self.game_manager.player
            move_speed = getattr(player, 'speed', 5) * 40
            
            new_x = player.position[0] + (dx * move_speed * dt)
            new_y = player.position[1] + (dy * move_speed * dt)
            
            new_x = max(0, min(new_x, Window.width - 20))
            new_y = max(game_screen.game_canvas.y, min(new_y, game_screen.game_canvas.y + game_screen.game_canvas.height - 20))
            
            player.position = [new_x, new_y]
            if hasattr(player, 'update'):
                player.update(dt)
        
        # Draw game entities
        game_screen.game_canvas.canvas.clear()
        with game_screen.game_canvas.canvas:
            
            # Draw and Check Perks
            if 'active_perks' in state and state['active_perks']:
                perks_copy = state['active_perks'][:] # iterate over a copy so we can remove
                for perk in perks_copy:
                    px, py = perk['pos']
                    if perk['type'] == 'max_hp':
                        Color(0.2, 1.0, 0.2, 1)  # Green Orb for HP
                    elif perk['type'] == 'speed':
                        Color(0.2, 0.2, 1.0, 1)  # Blue Orb for Speed
                    elif perk['type'] == 'attack':
                        Color(1.0, 0.2, 0.2, 1)  # Red Orb for Attack
                    elif perk['type'] == 'defense':
                        Color(0.2, 1.0, 1.0, 1)  # Cyan Orb for Defense
                    Rectangle(pos=(px, py), size=(perk['size'][0], perk['size'][1]))
                    
                    # Collision check
                    player_x, player_y = self.game_manager.player.position
                    dist = ((player_x - px)**2 + (player_y - py)**2)**0.5
                    if dist < 25:
                        if perk['type'] == 'max_hp':
                            self.game_manager.player.max_hp += 10
                            self.game_manager.player.hp += 10
                            self.game_manager.add_log("Collected +10 Max HP Perk!")
                        elif perk['type'] == 'speed':
                            self.game_manager.player.speed += 1
                            self.game_manager.add_log("Collected +1 Speed Perk!")
                        elif perk['type'] == 'attack':
                            self.game_manager.player.attack += 1
                            self.game_manager.add_log("Collected +1 Attack Perk!")
                        elif perk['type'] == 'defense':
                            self.game_manager.player.defense += 1
                            self.game_manager.add_log("Collected +1 Defense Perk!")
                        # Remove it immediately so it doesn't re-trigger
                        self.game_manager.active_perks.remove(perk)
                    
            # Draw Player
            if state['player_stats']:
                pos = self.game_manager.player.position
                Color(0.2, 0.6, 1.0, 1)
                Rectangle(pos=(pos[0], pos[1]), size=(20, 20))
            
            # Draw Attacks
            current_time = Clock.get_time()
            self.active_attacks = [a for a in self.active_attacks if current_time - a[2] < 0.2]
            Color(1.0, 0.2, 0.2, 1)
            for attack_x, attack_y, _ in self.active_attacks:
                Rectangle(pos=(attack_x - 10, attack_y - 10), size=(20, 20))
    
    def toggle_pause_menu(self):
        """Toggle pause menu"""
        game_screen = self.screen_manager.get_screen('game')
        
        if self.callback_manager.game_state['is_paused']:
            if not self.pause_menu:
                self.pause_menu = PauseMenuPopup(
                    callback_manager=self.callback_manager
                )
            self.pause_menu.open()
        else:
            if self.pause_menu:
                self.pause_menu.dismiss()
    
    def stop(self, **kwargs):
        """Stop the application"""
        super().stop(**kwargs)


if __name__ == '__main__':
    app = HackAndSlashApp()
    app.run()
