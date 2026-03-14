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
from kivy.uix.floatlayout import FloatLayout
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
        
        # Create main layout (FloatLayout to allow overlaying)
        main_layout = FloatLayout()
        
        # Track which enemy index is focused in the detail overlay
        self.enemy_detail_index = 0
        
        # Content layout (The actual game contents)
        content_layout = BoxLayout(
            orientation='vertical',
            padding=5,
            spacing=5,
            size_hint=(1, 1)
        )
        self.callback_manager = callback_manager
        
        # Top HUD bar
        hud = BoxLayout(
            orientation='vertical',
            size_hint_y=0.16,
            spacing=4,
            padding=5
        )

        # First row: basic stats + enemy detail button (top-right)
        top_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.5,
            spacing=10
        )
        
        # Player stats labels (Removed HP from top)
        self.level_label = Label(
            text='Level: 1',
            font_size='18sp',
            size_hint_x=0.3
        )
        
        self.score_label = Label(
            text='Score: 0',
            font_size='16sp',
            size_hint_y=0.1
        )
        self.time_label = Label(
            text='Time: 00:00',
            font_size='16sp',
            size_hint_y=0.1
        )

        top_row.add_widget(self.level_label)
        top_row.add_widget(self.score_label)
        top_row.add_widget(self.time_label)

        # Second row: Boss HP bar centered
        boss_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.5,
            padding=[80, 0, 80, 0],  # left, top, right, bottom
            spacing=8
        )

        self.boss_hp_label = Label(
            text='Boss: None',
            font_size='16sp',
            size_hint_x=0.2
        )
        self.boss_hp_bar = ProgressBar(
            value=0,
            max=100,
            size_hint_x=0.8
        )

        boss_row.add_widget(self.boss_hp_label)
        boss_row.add_widget(self.boss_hp_bar)

        hud.add_widget(top_row)
        hud.add_widget(boss_row)

        content_layout.add_widget(hud)
        
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

        # Extra information/placeholder widgets to increase actual widget count
        # and provide future slots for displaying additional stats or perks.
        self.perk_slot_labels = []
        for i in range(1, 16):
            slot_label = Label(
                text=f'Perk Slot {i}: Empty',
                font_size='12sp',
                size_hint_y=None,
                height=18
            )
            self.perk_slot_labels.append(slot_label)
            self.stat_panel.add_widget(slot_label)

        enemy_section_title = Label(
            text='[b]ENEMIES[/b]',
            markup=True,
            font_size='14sp',
            size_hint_y=None,
            height=24
        )
        self.stat_panel.add_widget(enemy_section_title)

        enemy_scroll = ScrollView(size_hint_y=0.4)
        self.enemy_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=2,
            spacing=2
        )
        self.enemy_list.bind(minimum_height=self.enemy_list.setter('height'))
        enemy_scroll.add_widget(self.enemy_list)
        self.stat_panel.add_widget(enemy_scroll)
        
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
        
        content_layout.add_widget(content_area)
        main_layout.add_widget(content_layout)

        # Centered enemy codex overlay (controlled via keyboard Tab, not clickable)
        self.enemy_detail_overlay = EnemyDetailOverlay()
        self.enemy_detail_overlay.opacity = 0
        self.enemy_detail_overlay.disabled = True
        # size_hint (0, 0) when hidden so it does not block clicks
        self.enemy_detail_overlay.size_hint = (0, 0)
        self.enemy_detail_overlay.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        main_layout.add_widget(self.enemy_detail_overlay)
        
        # Add the Perk Selection Overlay on top (hidden initially)
        self.perk_overlay = PerkSelectionOverlay(
            callback_manager=self.callback_manager,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.perk_overlay.opacity = 0
        self.perk_overlay.disabled = True
        main_layout.add_widget(self.perk_overlay)
        
        self.add_widget(main_layout)

    def toggle_enemy_detail_overlay(self):
        """Toggle enemy detail overlay using Tab key, pause/unpause game like perk selection"""
        is_hidden = self.enemy_detail_overlay.opacity == 0
        if is_hidden:
            # Pause the game and show overlay
            if self.callback_manager:
                self.callback_manager.game_state['is_paused'] = True
            self.enemy_detail_index = 0
            self.enemy_detail_overlay.size_hint = (0.6, 0.7)
            self.enemy_detail_overlay.disabled = False
            self.enemy_detail_overlay.opacity = 1
        else:
            # Hide overlay and resume game
            self.enemy_detail_overlay.opacity = 0
            self.enemy_detail_overlay.disabled = True
            self.enemy_detail_overlay.size_hint = (0, 0)
            if self.callback_manager:
                self.callback_manager.game_state['is_paused'] = False

    def set_enemy_detail_index(self, index):
        """Select which enemy (by index) the detail overlay should show"""
        if index < 0:
            index = 0
        self.enemy_detail_index = index

    def update_enemy_widgets(self, enemies_stats):
        """Update the enemy widgets list based on current enemy stats"""
        if not hasattr(self, 'enemy_list'):
            return
        self.enemy_list.clear_widgets()
        for stats in enemies_stats or []:
            name = stats.get('name', 'Enemy')
            hp = stats.get('hp', 0)
            max_hp = stats.get('max_hp', 0)
            enemy_widget = EnemyDisplay(size_hint_y=None, height=40)
            enemy_widget.set_enemy(name, hp, max_hp)
            self.enemy_list.add_widget(enemy_widget)


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
        quit_btn.bind(on_press=self.callback_manager.on_return_to_menu)
        quit_btn.bind(on_press=self.dismiss)
        content.add_widget(quit_btn)
        
        self.content = content

class PerkSelectionOverlay(BoxLayout):
    """Hidden overlay for selecting a perk when an orb is collected"""
    def __init__(self, callback_manager, **kwargs):
        super(PerkSelectionOverlay, self).__init__(**kwargs)
        self.callback_manager = callback_manager
        self.orientation = 'vertical'
        self.padding = 50
        self.spacing = 20
        # Background color to dim the screen
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0, 0, 0, 0.8) # semi-transparent black
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Instruction
        info_label = Label(
            text='[b]You collected a Perk Orb![/b]\nChoose your upgrade:',
            font_size='32sp',
            markup=True,
            size_hint_y=0.4,
            halign='center'
        )
        self.add_widget(info_label)
        
        # Buttons layout
        btn_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.6)
        
        perks = [
            ('max_hp', '+10 Max HP', (0.2, 0.8, 0.2, 1)),
            ('speed', '+1 Speed', (0.2, 0.2, 0.8, 1)),
            ('attack', '+1 Attack', (0.8, 0.2, 0.2, 1)),
            ('defense', '+1 Defense', (0.2, 0.8, 0.8, 1))
        ]
        
        for perk_id, perk_label, color in perks:
            btn = Button(
                text=perk_label,
                background_color=color,
                font_size='24sp'
            )
            # Create closure for the callback
            btn.bind(on_press=lambda instance, p_id=perk_id: self.select_perk(p_id))
            btn_layout.add_widget(btn)
            
        self.add_widget(btn_layout)
        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def select_perk(self, perk_id):
        self.callback_manager.on_perk_selected(perk_id)



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


class EnemyDetailOverlay(BoxLayout):
    """Centered overlay for showing an Enemy Codex (enemy types list)."""
    def __init__(self, **kwargs):
        super(EnemyDetailOverlay, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        self.size_hint = (0.6, 0.7)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Background color to dim the screen
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0, 0, 0, 0.9) # dark semi-transparent black
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        title = Label(
            text='[b]ENEMY CODEX[/b]',
            markup=True,
            font_size='24sp',
            size_hint_y=0.1
        )
        self.add_widget(title)

        # Scrollable list of enemy types
        self.scroll_view = ScrollView(size_hint_y=0.9)
        self.codex_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=10,
            spacing=10
        )
        self.codex_list.bind(minimum_height=self.codex_list.setter('height'))
        self.scroll_view.add_widget(self.codex_list)
        self.add_widget(self.scroll_view)

        # Initialize with known enemy types (Static list for Codex)
        self._populate_codex()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _populate_codex(self):
        """Populate the codex with known enemy types."""
        enemy_types = [
            {'name': 'Goblin', 'hp': 25, 'attack': 5, 'speed': 4, 'desc': 'A basic melee attacker.'},
            {'name': 'Orc', 'hp': 55, 'attack': 10, 'speed': 3, 'desc': 'A stronger, slower melee attacker.'},
            {'name': 'Skeleton', 'hp': 33, 'attack': 7, 'speed': 4, 'desc': 'A standard enemy type.'},
            {'name': 'Normal', 'hp': 10, 'attack': 10, 'speed': 4, 'desc': 'Standard red enemy.'},
            {'name': 'Tank', 'hp': 20, 'attack': 10, 'speed': 3, 'desc': 'Orange enemy with more HP.'},
            {'name': 'Shooter', 'hp': 10, 'attack': 10, 'speed': 4, 'desc': 'Purple enemy that fires projectiles.'},
            {'name': 'Boss', 'hp': 150, 'attack': 18, 'speed': 3, 'desc': 'A mighty Boss that spawns every 5 minutes.'}
        ]

        for enemy in enemy_types:
            entry = BoxLayout(orientation='vertical', size_hint_y=None, height=100, padding=5)
            
            # Simple border
            from kivy.graphics import Line
            with entry.canvas.before:
                Color(0.2, 0.2, 0.2, 1)
                entry.bg_rect = Rectangle(size=entry.size, pos=entry.pos)
            entry.bind(size=self._update_entry_bg, pos=self._update_entry_bg)

            name_lbl = Label(text=f"[b]{enemy['name']}[/b]", markup=True, font_size='18sp', size_hint_y=0.3, halign='left')
            name_lbl.bind(size=name_lbl.setter('text_size'))
            stats_lbl = Label(text=f"HP: {enemy['hp']} | Attack: {enemy['attack']} | Speed: {enemy['speed']}", font_size='14sp', size_hint_y=0.3, halign='left')
            stats_lbl.bind(size=stats_lbl.setter('text_size'))
            desc_lbl = Label(text=f"[i]{enemy['desc']}[/i]", markup=True, font_size='14sp', size_hint_y=0.4, halign='left')
            desc_lbl.bind(size=desc_lbl.setter('text_size'))

            entry.add_widget(name_lbl)
            entry.add_widget(stats_lbl)
            entry.add_widget(desc_lbl)
            self.codex_list.add_widget(entry)

    def _update_entry_bg(self, instance, value):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size

    def update_from_enemy(self, enemy_stats_list, selected_index=0):
        """No longer used for dynamic updates, purely static codex now."""
        pass


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
        self.score_label = Label(text='Final Score: 0', font_size='20sp')
        self.gold_earned_label = Label(text='Gold Earned: 0', font_size='20sp')
        
        stats_layout.add_widget(self.final_level_label)
        stats_layout.add_widget(self.final_time_label)
        stats_layout.add_widget(self.score_label)
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

