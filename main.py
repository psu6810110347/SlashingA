"""
Hack and Slash Game - Main Entry Point
Built with Kivy Framework
"""

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock

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
        
        # Bind keyboard events
        Window.bind(on_keyboard=self.on_keyboard)
        
        return self.screen_manager
    
    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Handle keyboard events"""
        if key == 27:  # ESC key
            self.callback_manager.on_pause(None)
            return True
        elif key == 32:  # Space key
            self.callback_manager.on_attack(None)
            return True
        elif codepoint == 'q':  # Q key
            self.callback_manager.on_use_skill(None)
            return True
        elif codepoint == 'p':  # P key
            self.callback_manager.on_pause(None)
            return True
        return False
    
    def show_menu_screen(self):
        """Switch to menu screen"""
        self.screen_manager.current = 'menu'
    
    def show_game_screen(self):
        """Switch to game screen"""
        self.game_manager.start_new_game()
        self.screen_manager.current = 'game'
        # Update game display
        Clock.schedule_once(self.update_game_display, 0.1)
    
    def update_game_display(self, dt):
        """Update game display"""
        game_screen = self.screen_manager.get_screen('game')
        state = self.game_manager.get_game_state()
        
        if state['player_stats']:
            hp = state['player_stats']['hp']
            max_hp = state['player_stats']['max_hp']
            level = state['player_stats']['level']
            game_screen.hp_label.text = f'HP: {hp}/{max_hp}'
            game_screen.level_label.text = f'Level: {level}'
        
        if state['enemy_stats']:
            game_screen.game_canvas.clear_widgets()
            # Add enemy display or game canvas here
    
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
