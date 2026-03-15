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
        
        # Add tiled background image
        from kivy.graphics import Color, Rectangle, RoundedRectangle
        from kivy.core.image import Image as CoreImage
        
        self.bg_texture = None
        try:
            # We use the isolated grass_tile.png so it isn't an entire squished spritesheet
            self.bg_texture = CoreImage('images/backgrounds/grass_tile.png').texture
            self.bg_texture.wrap = 'repeat'
            self.bg_texture.mag_filter = 'nearest' # Keep pixel art crisp
        except Exception:
            pass

        with self.canvas.before:
            Color(1, 1, 1, 1) # White so image shows naturally
            if self.bg_texture:
                self.bg_rect = Rectangle(texture=self.bg_texture, pos=self.pos, size=self.size)
            else:
                self.bg_rect = Rectangle(source='images/backgrounds/ground.png', pos=self.pos, size=self.size)
            
            # Add some decorative trees and rocks to the menu background
            import random
            from kivy.core.image import Image as CoreImage
            random.seed(42) # Fixed seed so they don't jump around on resize
            
            # Load tree texture and calculate a single frame's coordinates
            tree_tex = None
            try:
                tree_img = CoreImage('images/decorations/tree.png')
                # Grab just a static 192x256 region from the source image texture to prevent animation
                # The tree sprite sheet is 1536 width. It has 8 frames, so each frame is 192px wide.
                tree_tex = tree_img.texture.get_region(0, 0, 192, tree_img.height)
            except Exception:
                pass
            
            # Draw 15 random trees
            for _ in range(15):
                x = random.randint(-50, 1300)
                y = random.randint(-50, 750)
                size_variation = random.uniform(0.8, 1.2)
                tree_w = 192 * size_variation
                tree_h = 256 * size_variation
                if tree_tex:
                    Rectangle(texture=tree_tex, pos=(x, y), size=(tree_w, tree_h))
                else:
                    Rectangle(source='images/decorations/tree.png', pos=(x, y), size=(tree_w, tree_h))
                
            # Draw 10 random rocks (only rock1 and rock2 exist in folders)
            for _ in range(10):
                x = random.randint(0, 1280)
                y = random.randint(0, 720)
                rock_type = random.choice([1, 2])
                rsize = random.randint(30, 60)
                Rectangle(source=f'images/decorations/rock{rock_type}.png', pos=(x, y), size=(rsize, rsize))
            
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Create main layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding=50,
            spacing=30
        )
        
        # Title (with outline instead of dark plate)
        title_box = BoxLayout(size_hint_y=0.4, padding=10)
        title = Label(
            text='[b]SlashingA[/b]',
            font_size='100sp',
            markup=True,
            color=(1.0, 0.85, 0.2, 1), # Bright Gold
            outline_width=4,
            outline_color=(0.1, 0.1, 0.1, 1) # Dark outline
        )
        title_box.add_widget(title)
        main_layout.add_widget(title_box)
        
        # Controls Information (with outline)
        controls_box = BoxLayout(size_hint_y=0.2, padding=10)
        controls_label = Label(
            text='[b]CONTROLS[/b]\n[color=cccccc]W A S D[/color] to Move  |  [color=cccccc]Left Click[/color] to Slash\n[color=cccccc]P[/color] to Pause  |  [color=cccccc]ESC[/color] for Menu',
            font_size='22sp',
            markup=True,
            halign='center',
            color=(1, 1, 1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        controls_box.add_widget(controls_label)
        main_layout.add_widget(controls_box)
        
        # Buttons container
        button_container = BoxLayout(
            orientation='vertical',
            size_hint_y=0.4,
            spacing=25,
            padding=[300, 10, 300, 40] # Very squeezed horizontal for wide pill buttons
        )
        
        def _update_btn_rect(instance, value):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size

        # Start button
        start_btn = Button(
            text='[b]START ADVENTURE[/b]',
            font_size='26sp',
            markup=True,
            size_hint_y=0.5,
            background_normal='',
            background_color=(0, 0, 0, 0), # Transparent so we see the canvas below
            color=(1, 1, 1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        with start_btn.canvas.before:
            Color(0.15, 0.65, 0.25, 0.85) # Premium green
            start_btn.bg_rect = RoundedRectangle(pos=start_btn.pos, size=start_btn.size, radius=[25])
        start_btn.bind(pos=_update_btn_rect, size=_update_btn_rect)
        start_btn.bind(on_press=callback_manager.on_start_game)
        button_container.add_widget(start_btn)
        
        # Quit button
        quit_btn = Button(
            text='[b]EXIT REALM[/b]',
            font_size='26sp',
            markup=True,
            size_hint_y=0.5,
            background_normal='',
            background_color=(0, 0, 0, 0), # Transparent
            color=(1, 1, 1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        with quit_btn.canvas.before:
            Color(0.8, 0.15, 0.15, 0.85) # Premium red
            quit_btn.bg_rect = RoundedRectangle(pos=quit_btn.pos, size=quit_btn.size, radius=[25])
        quit_btn.bind(pos=_update_btn_rect, size=_update_btn_rect)
        quit_btn.bind(on_press=callback_manager.on_quit_game)
        button_container.add_widget(quit_btn)
        
        main_layout.add_widget(button_container)
        self.add_widget(main_layout)
        
        # Music Credit Label
        music_credit = Label(
            text='Music track: Ballad by Pufino\nSource: [u]https://freetouse.com/music[/u]\nRoyalty Free Music for Video (Safe)',
            font_size='12sp',
            markup=True,
            size_hint=(None, None),
            size=(300, 60),
            halign='right',
            valign='bottom',
            pos_hint={'right': 1, 'bottom': 1},
            color=(1, 1, 1, 0.9),
            outline_width=1,
            outline_color=(0,0,0,1)
        )
        music_credit.bind(size=music_credit.setter('text_size'))
        self.add_widget(music_credit)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        
        # Update tex_coords to repeat the texture based on screen size
        if hasattr(self, 'bg_texture') and self.bg_texture:
            tw = self.bg_texture.width
            th = self.bg_texture.height
            if tw > 0 and th > 0:
                # Scale by 2.0 to make the tiles slightly larger/prettier, similar to pixel art styling
                w = instance.width / (tw * 2.0)
                h = instance.height / (th * 2.0)
                self.bg_rect.tex_coords = (0, 0, w, 0, w, h, 0, h)

class GameScreen(Screen):
    """Main game play screen"""
    def __init__(self, callback_manager, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        
        # Create main layout (FloatLayout to allow overlaying)
        main_layout = FloatLayout()
        
        # Dedicated game world layer (Bottom-most)
        from kivy.uix.widget import Widget
        self.game_world = Widget(size_hint=(1, 1))
        main_layout.add_widget(self.game_world)
        
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
        
        # Add background to HUD
        from kivy.graphics import Color, Rectangle
        with hud.canvas.before:
            Color(0, 0, 0, 0.7) # Darker for better contrast
            hud.bg_rect = Rectangle(pos=hud.pos, size=hud.size)
        hud.bind(pos=self._update_hud_bg, size=self._update_hud_bg)

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
        
        # Add background to Stat Panel
        with self.stat_panel.canvas.before:
            Color(0, 0, 0, 0.6) # Darker for better contrast
            self.stat_panel.bg_rect = Rectangle(pos=self.stat_panel.pos, size=self.stat_panel.size)
        self.stat_panel.bind(pos=self._update_stat_bg, size=self._update_stat_bg)
        
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

        # Perk collection tracking slots (4 types)
        perk_section_title = Label(
            text='[b]PERKS COLLECTED[/b]',
            markup=True,
            font_size='14sp',
            size_hint_y=None,
            height=24
        )
        self.stat_panel.add_widget(perk_section_title)

        self.perk_slot_labels = {}
        perk_types = [
            ('max_hp', 'Max HP'),
            ('speed', 'Speed'),
            ('attack', 'Attack'),
            ('defense', 'Defense'),
        ]
        for perk_id, perk_name in perk_types:
            slot_label = Label(
                text=f'{perk_name}: 0',
                font_size='12sp',
                size_hint_y=None,
                height=18
            )
            self.perk_slot_labels[perk_id] = slot_label
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
        
        # Music Credit Label (Bottom Right)
        music_credit = Label(
            text='Music track: Guardian of the Former Seas by DM DOKURO',
            font_size='12sp',
            markup=True,
            size_hint=(None, None),
            size=(400, 30),
            halign='right',
            valign='bottom',
            pos_hint={'right': 1, 'bottom': 1},
            color=(1, 1, 1, 0.6) # Semi-transparent
        )
        music_credit.bind(size=music_credit.setter('text_size'))
        main_layout.add_widget(music_credit)
        
        self.add_widget(main_layout)

    def _update_hud_bg(self, instance, value):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size

    def _update_stat_bg(self, instance, value):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size

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
            self.bg_color = Color(0, 0, 0, 0.85) # Very dark semi-transparent black
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
        self.scroll_view = ScrollView(
            size_hint_y=0.9,
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=10
        )
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
        """Populate the codex with enemy types that actually appear in the game."""
        enemy_types = [
            {'name': 'Knight', 'hp': 10, 'attack': 10, 'speed': 4, 'type': 'Warrior',
             'desc': 'A brave soldier of the Red Kingdom. Aggressive and skilled in close-range sword combat.'},
            {'name': 'Lancer', 'hp': 20, 'attack': 10, 'speed': 3, 'type': 'Vanguard',
             'desc': 'A heavily armored lancer. Their long reach and high defense make them formidable front-line units.'},
            {'name': 'Archer', 'hp': 10, 'attack': 10, 'speed': 4, 'type': 'Ranged',
             'desc': 'A precision shooter who supports from afar. They fire deadly arrows with a balanced attack rate.'},
            {'name': 'Boss', 'hp': 150, 'attack': 18, 'speed': 3, 'type': 'Elite',
             'desc': 'A legendary commander of the Red Legion. Boasts massive HP and devastating special attacks.'}
        ]

        for enemy in enemy_types:
            entry = BoxLayout(orientation='vertical', size_hint_y=None, height=90, padding=5)
            
            # Background
            from kivy.graphics import Color, Rectangle
            with entry.canvas.before:
                Color(0.15, 0.15, 0.15, 1)
                entry.bg_rect = Rectangle(size=entry.size, pos=entry.pos)
            entry.bind(size=self._update_entry_bg, pos=self._update_entry_bg)

            name_lbl = Label(text=f"[b]{enemy['name']}[/b]  ({enemy['type']})", markup=True, font_size='18sp', size_hint_y=0.3, halign='left')
            name_lbl.bind(size=name_lbl.setter('text_size'))
            stats_lbl = Label(text=f"HP: {enemy['hp']}  |  Attack: {enemy['attack']}  |  Speed: {enemy['speed']}", font_size='14sp', size_hint_y=0.3, halign='left')
            stats_lbl.bind(size=stats_lbl.setter('text_size'))
            desc_lbl = Label(text=f"[i]{enemy['desc']}[/i]", markup=True, font_size='13sp', size_hint_y=0.4, halign='left')
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
        
        # Music Credit Label (Bottom Right)
        music_credit = Label(
            text='Music track: Fallen Kingdom by Epic Spectrum\nSource: [u]https://freetouse.com/music[/u]\nCopyright Free Music (Free Download)',
            font_size='12sp',
            markup=True,
            size_hint=(None, None),
            size=(300, 60),
            halign='right',
            valign='bottom',
            pos_hint={'right': 1, 'bottom': 1},
            color=(1, 1, 1, 0.6) # Semi-transparent
        )
        music_credit.bind(size=music_credit.setter('text_size'))
        self.add_widget(music_credit)

