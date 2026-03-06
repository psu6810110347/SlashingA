"""
UI Widgets Module
Contains all custom widget definitions for the game
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock


class MainMenuScreen(Screen):
    """Main menu screen with start and quit buttons"""
    def __init__(self, callback_manager, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        
        # Create main layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=20
        )
        
        # Title
        title = Label(
            text='[b]SlashingA[/b]',
            font_size='48sp',
            markup=True,
            size_hint_y=0.3
        )
        main_layout.add_widget(title)
        
        # Controls Information
        controls_label = Label(
            text='[b]How to Play:[/b]\nW, A, S, D - Move\nLeft Mouse Click - Attack\nP - Pause Game\nESC - Main Menu',
            font_size='18sp',
            markup=True,
            halign='center',
            size_hint_y=0.2
        )
        main_layout.add_widget(controls_label)
        
        # Buttons container
        button_container = BoxLayout(
            orientation='vertical',
            size_hint_y=0.5,
            spacing=15,
            padding=20
        )
        
        # Start button
        start_btn = Button(
            text='START GAME',
            font_size='24sp',
            size_hint_y=0.4,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        start_btn.bind(on_press=callback_manager.on_start_game)
        button_container.add_widget(start_btn)
        
        # Quit button
        quit_btn = Button(
            text='QUIT',
            font_size='24sp',
            size_hint_y=0.4,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        quit_btn.bind(on_press=callback_manager.on_quit_game)
        button_container.add_widget(quit_btn)
        
        main_layout.add_widget(button_container)
        self.add_widget(main_layout)


class GameScreen(Screen):
    """Main game play screen"""
    def __init__(self, callback_manager, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        
        # Create main layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding=5,
            spacing=5
        )
        self.callback_manager = callback_manager
        
        # Top HUD bar
        hud = BoxLayout(
            size_hint_y=0.1,
            spacing=10,
            padding=5
        )
        
        # Player stats labels (Removed HP from top)
        self.level_label = Label(
            text='Level: 1',
            font_size='18sp',
            size_hint_x=0.33
        )
        
        score_label = Label(
            text='Score: 0',
            font_size='18sp',
            size_hint_x=0.33
        )

        self.time_label = Label(
            text='Time: 00:00',
            font_size='18sp',
            size_hint_x=0.33
        )
        
        hud.add_widget(self.level_label)
        hud.add_widget(score_label)
        hud.add_widget(self.time_label)
        
        main_layout.add_widget(hud)
        
        # Lower Content Area (Left Stats + Right Game/Controls)
        content_area = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.9
        )
        
        # Left Side: Stat Panel
        self.stat_panel = BoxLayout(
            orientation='vertical',
            size_hint_x=0.15,
            padding=10,
            spacing=2
        )
        
        stat_title = Label(text='[b]PLAYER STATS[/b]', markup=True, font_size='16sp', size_hint_y=None, height=40)
        self.side_hp_label = Label(text='HP: 100/100', font_size='14sp', size_hint_y=None, height=20)
        self.side_atk_label = Label(text='Attack: 10', font_size='14sp', size_hint_y=None, height=20)
        self.side_def_label = Label(text='Defense: 0', font_size='14sp', size_hint_y=None, height=20)
        self.side_spd_label = Label(text='Speed: 5', font_size='14sp', size_hint_y=None, height=20)
        
        self.stat_panel.add_widget(stat_title)
        self.stat_panel.add_widget(self.side_hp_label)
        self.stat_panel.add_widget(self.side_atk_label)
        self.stat_panel.add_widget(self.side_def_label)
        self.stat_panel.add_widget(self.side_spd_label)
        
        # Push stats to the top of the left column
        self.stat_panel.add_widget(Label(size_hint_y=1))
        
        # Right Side: Game Canvas and Controls
        right_area = BoxLayout(
            orientation='vertical',
            size_hint_x=0.85
        )
        
        # Game canvas area
        self.game_canvas = BoxLayout(
            orientation='vertical',
            size_hint_y=0.8
        )
        right_area.add_widget(self.game_canvas)
        
        # Control buttons
        controls = GridLayout(
            cols=4,
            size_hint_y=0.2,
            spacing=5,
            padding=5
        )
        
        # Add Left and Right areas to content layout
        content_area.add_widget(self.stat_panel)
        content_area.add_widget(right_area)
        
        main_layout.add_widget(content_area)
        self.add_widget(main_layout)


class PauseMenuPopup(Popup):
    """Pause menu popup"""
    def __init__(self, callback_manager, **kwargs):
        super(PauseMenuPopup, self).__init__(**kwargs)
        self.title = 'PAUSED'
        self.size_hint = (0.8, 0.6)
        self.callback_manager = callback_manager
        
        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10
        )
        
        resume_btn = Button(
            text='Resume',
            font_size='18sp',
            size_hint_y=0.3
        )
        resume_btn.bind(on_press=self.callback_manager.on_resume)
        resume_btn.bind(on_press=self.dismiss)
        content.add_widget(resume_btn)
        
        settings_btn = Button(
            text='Settings',
            font_size='18sp',
            size_hint_y=0.3
        )
        settings_btn.bind(on_press=self.callback_manager.on_settings)
        content.add_widget(settings_btn)
        
        quit_btn = Button(
            text='Quit to Menu',
            font_size='18sp',
            size_hint_y=0.3
        )
        quit_btn.bind(on_press=self.callback_manager.on_quit_to_menu)
        quit_btn.bind(on_press=self.dismiss)
        content.add_widget(quit_btn)
        
        self.content = content


class PlayerStatsDisplay(BoxLayout):
    """Player statistics display widget"""
    def __init__(self, player_data=None, **kwargs):
        super(PlayerStatsDisplay, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 5
        self.spacing = 3
        self.player_data = player_data or {}
        
        self.name_label = Label(text='Player: Hero')
        self.hp_bar = ProgressBar(value=100, max=100)
        self.exp_bar = ProgressBar(value=0, max=100)
        
        self.add_widget(self.name_label)
        self.add_widget(Label(text='HP:', size_hint_y=0.2))
        self.add_widget(self.hp_bar)
        self.add_widget(Label(text='EXP:', size_hint_y=0.2))
        self.add_widget(self.exp_bar)
    
    def update_hp(self, current, maximum):
        """Update HP bar"""
        self.hp_bar.value = current
        self.hp_bar.max = maximum
        self.name_label.text = f'Player: Hero | HP: {current}/{maximum}'
    
    def update_exp(self, current, maximum):
        """Update EXP bar"""
        self.exp_bar.value = current
        self.exp_bar.max = maximum


class EnemyDisplay(BoxLayout):
    """Enemy display widget"""
    def __init__(self, **kwargs):
        super(EnemyDisplay, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 5
        self.spacing = 3
        
        self.enemy_name = Label(text='Enemy: Goblin')
        self.enemy_hp_bar = ProgressBar(value=50, max=100)
        
        self.add_widget(self.enemy_name)
        self.add_widget(self.enemy_hp_bar)
    
    def set_enemy(self, name, hp, max_hp):
        """Set enemy information"""
        self.enemy_name.text = f'Enemy: {name}'
        self.enemy_hp_bar.value = hp
        self.enemy_hp_bar.max = max_hp


class CombatLog(ScrollView):
    """Combat log display"""
    def __init__(self, **kwargs):
        super(CombatLog, self).__init__(**kwargs)
        self.layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=5,
            spacing=2
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
    
    def add_log_entry(self, message):
        """Add message to combat log"""
        log_label = Label(
            text=message,
            size_hint_y=None,
            height=30,
            markup=True
        )
        self.layout.add_widget(log_label)


class InventoryScreen(BoxLayout):
    """Inventory screen"""
    def __init__(self, **kwargs):
        super(InventoryScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 5
        
        title = Label(text='INVENTORY', font_size='24sp', size_hint_y=0.1)
        self.add_widget(title)
        
        # Inventory grid
        self.inventory_grid = GridLayout(
            cols=5,
            spacing=5,
            size_hint_y=0.7,
            padding=5
        )
        self.add_widget(self.inventory_grid)
        
        # Close button
        close_btn = Button(
            text='Close',
            size_hint_y=0.2,
            font_size='18sp'
        )
        self.add_widget(close_btn)


class SkillTree(BoxLayout):
    """Skill tree screen"""
    def __init__(self, **kwargs):
        super(SkillTree, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 5
        
        title = Label(text='SKILL TREE', font_size='24sp', size_hint_y=0.1)
        self.add_widget(title)
        
        # Skills grid
        self.skills_grid = GridLayout(
            cols=3,
            spacing=10,
            size_hint_y=0.8,
            padding=5
        )
        self.add_widget(self.skills_grid)
        
        # Close button
        close_btn = Button(
            text='Close',
            size_hint_y=0.1,
            font_size='18sp'
        )
        self.add_widget(close_btn)

class GameOverScreen(Screen):
    """Game over screen showing final stats"""
    def __init__(self, callback_manager, **kwargs):
        super(GameOverScreen, self).__init__(**kwargs)
        self.callback_manager = callback_manager
        
        main_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=10
        )
        
        # Game Over Title
        title = Label(
            text='[color=ff0000][b]GAME OVER[/b][/color]',
            font_size='48sp',
            markup=True,
            size_hint_y=0.2
        )
        main_layout.add_widget(title)
        
        # Stats container
        stats_layout = GridLayout(
            cols=2,
            spacing=10,
            size_hint_y=0.4,
            padding=20
        )
        
        self.final_level_label = Label(text='Level Reached: 1', font_size='20sp')
        self.final_time_label = Label(text='Time Survived: 00:00', font_size='20sp')
        self.enemies_killed_label = Label(text='Enemies Defeated: 0', font_size='20sp')
        self.gold_earned_label = Label(text='Gold Earned: 0', font_size='20sp')
        
        stats_layout.add_widget(self.final_level_label)
        stats_layout.add_widget(self.final_time_label)
        stats_layout.add_widget(self.enemies_killed_label)
        stats_layout.add_widget(self.gold_earned_label)
        
        main_layout.add_widget(stats_layout)
        
        # Buttons container
        buttons_layout = BoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint_y=0.2,
            padding=10
        )
        
        restart_btn = Button(
            text='TRY AGAIN',
            font_size='24sp',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        restart_btn.bind(on_press=self.callback_manager.on_restart_game)
        
        menu_btn = Button(
            text='MAIN MENU',
            font_size='24sp',
            background_color=(0.3, 0.3, 0.8, 1)
        )
        menu_btn.bind(on_press=self.callback_manager.on_return_to_menu)
        
        buttons_layout.add_widget(restart_btn)
        buttons_layout.add_widget(menu_btn)
        
        main_layout.add_widget(buttons_layout)
        self.add_widget(main_layout)

