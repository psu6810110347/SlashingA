"""
Hack and Slash Game - Main Entry Point
Built with Kivy Framework
"""

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, Rotate, PushMatrix, PopMatrix
import math

from ui.widgets import MainMenuScreen, GameScreen, PauseMenuPopup
from events.callbacks import CallbackManager
from game.game_logic import GameManager
from ui.widgets import MainMenuScreen, GameScreen, PauseMenuPopup, GameOverScreen
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
import os
import time
import math

# Default Constants for Tiny Swords Asset Pack
DEFAULT_FRAME_SIZE = 192
DEFAULT_SHEET_COLS = 6

class SpriteSheet:
    def __init__(self, source, frame_size=DEFAULT_FRAME_SIZE, cols=DEFAULT_SHEET_COLS):
        self.texture = None
        self.frame_size = frame_size
        self.cols = cols
        if os.path.exists(source):
            try:
                self.texture = CoreImage(source).texture
                self.texture.mag_filter = 'nearest' # Keep pixel art clean
            except Exception as e:
                print(f"Error loading sheet {source}: {e}")
        
    def get_tex_coords(self, frame_x, frame_y=0, flip_x=False):
        """Calculate UV coordinates for a frame in a sheet (defaults to row 0 for single-action sheets)"""
        if not self.texture:
            return None
        
        u_step = self.frame_size / self.texture.width
        v_step = self.frame_size / self.texture.height
        
        # Clamp frame_x to avoid overflow if sheet has fewer frames
        max_cols = self.texture.width // self.frame_size
        if max_cols > 0:
            frame_x = frame_x % max_cols
            
        u = frame_x * u_step
        
        # Kivy vertical flip fix: Swap top and bottom V to flip Sprite 180 degrees
        v_bottom = 1.0 - (frame_y + 1) * v_step
        v_top = 1.0 - frame_y * v_step
        
        # Horizontal flip logic
        if flip_x:
            return [u + u_step, v_top, u, v_top, u, v_bottom, u + u_step, v_bottom]
        return [u, v_top, u + u_step, v_top, u + u_step, v_bottom, u, v_bottom]


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
        self.sprite_sheets = {}
        self._last_anim_update = time.time()
        self._current_frame = 0 # Track frame for walk cycles
        self.player_facing_right = True # Track player direction
        self._last_attack_time = 0 # Track attack cooldown
        self.current_bgm = None
    
    def build(self):
        """Build the application"""
        # Initialize managers
        self.callback_manager = CallbackManager(self)
        self.game_manager = GameManager(callback_manager=self.callback_manager)
        
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
                # Create game over screen
        game_over_screen = GameOverScreen(
            callback_manager=self.callback_manager
        )
        game_over_screen.name = 'game_over'
        self.screen_manager.add_widget(game_over_screen)
        # Set default screen
        self.screen_manager.current = 'menu'
        self.play_bgm('audio/bgm/menu.mp3')
        
        # Bind keyboard and mouse events
        Window.bind(
            on_key_down=self.on_key_down,
            on_key_up=self.on_key_up,
            on_touch_down=self.on_touch_down
        )
        
        return self.screen_manager
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle key press"""
        if codepoint == 'a':
            self.player_facing_right = False
        elif codepoint == 'd':
            self.player_facing_right = True

        if codepoint in ['w', 'a', 's', 'd']:
            self.pressed_keys.add(codepoint)
            
        if key == 27:  # ESC key
            self.callback_manager.on_return_to_menu(None)
            return True
        elif codepoint == 'p':  # P key
            self.callback_manager.on_pause(None)
            return True
        # Use TAB key (keycode 9) to toggle enemy detail like a pause overlay
        elif key == 9:  # Tab key
            if self.screen_manager.current == 'game':
                game_screen = self.screen_manager.get_screen('game')
                if hasattr(game_screen, 'toggle_enemy_detail_overlay'):
                    game_screen.toggle_enemy_detail_overlay()
                    return True
        # Number keys 1-9: change which enemy is shown in detail overlay
        elif codepoint in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            if self.screen_manager.current == 'game':
                game_screen = self.screen_manager.get_screen('game')
                if hasattr(game_screen, 'enemy_detail_overlay') and game_screen.enemy_detail_overlay.opacity == 1:
                    index = int(codepoint) - 1  # 1 -> 0, 2 -> 1, ...
                    if hasattr(game_screen, 'set_enemy_detail_index'):
                        game_screen.set_enemy_detail_index(index)
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
                now = Clock.get_time()
                # 0.6s cooldown matches 6 frames at 0.1s/frame
                if now - self._last_attack_time < 0.6:
                    return True
                
                self._last_attack_time = now
                self._current_frame = 0 # Start attack animation from first frame
                
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
                
                self.active_attacks.append((attack_x, attack_y, now))
                self.callback_manager.on_attack(self.player_facing_right)
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
        # Start game music
        self.play_bgm('audio/bgm/game.mp3')
    
    def play_bgm(self, path):
        """Play background music looping. Gracefully handles missing files."""
        if self.current_bgm:
            self.current_bgm.stop()
            self.current_bgm = None
            
        if os.path.exists(path):
            self.current_bgm = SoundLoader.load(path)
            if self.current_bgm:
                self.current_bgm.loop = True
                self.current_bgm.volume = 0.5
                self.current_bgm.play()
                print(f"BGM Playing: {path}")
        else:
            print(f"BGM File not found (skipping): {path}")
    
    def update_game_display(self, dt):
        """Update game display and animations"""
        # Global frame counter for animations (approx 10 FPS for animations)
        now = time.time()
        if now - self._last_anim_update > 0.1: # 0.1s = 10 FPS
            self._current_frame = (self._current_frame + 1) % 6
            self._last_anim_update = now
            
        game_screen = self.screen_manager.get_screen('game')
        state = self.game_manager.get_game_state()
                # Check if player died
        if state['player_stats'] and state['player_stats']['hp'] <= 0:
            self.callback_manager.on_game_over(state)
            return

        if state['player_stats']:
            stats = state['player_stats']
            game_screen.level_label.text = f"Level: {stats['level']}"
            if hasattr(game_screen, 'score_label'):
                game_screen.score_label.text = f"Score: {stats['score']}"
            game_screen.side_hp_label.text = f"HP: {stats['hp']}/{stats['max_hp']}"
            game_screen.side_atk_label.text = f"Attack: {stats['attack']}"
            game_screen.side_def_label.text = f"Defense: {stats['defense']}"
            game_screen.side_spd_label.text = f"Speed: {stats['speed']}"

        enemies_stats = state.get('enemy_stats', [])
        if hasattr(game_screen, 'update_enemy_widgets'):
            game_screen.update_enemy_widgets(enemies_stats)

        # Update top-right enemy detail overlay (HP/damage/speed, no time label).
        # Uses GameScreen.enemy_detail_index so pressing 1-9 changes which enemy you see.
        if hasattr(game_screen, 'enemy_detail_overlay'):
            selected_index = getattr(game_screen, 'enemy_detail_index', 0)
            game_screen.enemy_detail_overlay.update_from_enemy(enemies_stats, selected_index)

        # Update boss HP widget (shows boss if present, otherwise hidden/empty)
        if hasattr(game_screen, 'boss_hp_bar') and hasattr(game_screen, 'boss_hp_label'):
            boss_stats = next((e for e in enemies_stats if e.get('name') == 'Boss'), None)
            if boss_stats:
                hp = boss_stats.get('hp', 0)
                max_hp = boss_stats.get('max_hp', 0) or 1
                game_screen.boss_hp_bar.max = max_hp
                game_screen.boss_hp_bar.value = hp
                game_screen.boss_hp_label.text = f"Boss: {hp}/{max_hp}"
                game_screen.boss_hp_bar.opacity = 1
                game_screen.boss_hp_label.opacity = 1
            else:
                game_screen.boss_hp_bar.value = 0
                game_screen.boss_hp_bar.opacity = 0
                game_screen.boss_hp_label.text = "Boss: None"
                game_screen.boss_hp_label.opacity = 0.6
        
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
            
            if dx != 0 or dy != 0:
                self.callback_manager.on_player_move(dx, dy)
            
            player.position = [new_x, new_y]
            if hasattr(player, 'update'):
                player.update(dt)
                # Update game state explicitly (since we need elapsed time for projectiles/spawns)
        self.game_manager.time_manager.update()
        
        # Enemy Attack Tick
        if not self.callback_manager.game_state['is_paused'] and state['is_combat_active']:
            self.game_manager.enemy_attack()
            
            # Enemy Movement
            for e in self.game_manager.enemies:
                if e.is_alive:
                    ex, ey = e.position
                    px, py = self.game_manager.player.position
                    dx, dy = px - ex, py - ey
                    dist = (dx**2 + dy**2)**0.5
                    
                    # Stop moving if close enough to player (at attack range)
                    if dist > e.attack_range * 0.8: # Close in slightly more than max attack range
                        dx /= dist
                        dy /= dist
                        move_speed = getattr(e, 'speed', 3) * 20
                        e.position[0] += dx * move_speed * dt
                        e.position[1] += dy * move_speed * dt
                        if e.action != "attack":
                            e.action = "run"
                    else:
                        if e.action != "attack":
                            e.action = "idle"
            
            # Update Projectiles
            dt_safe = dt if dt < 0.1 else 0.016
            surviving_projectiles = []
            for p in self.game_manager.active_projectiles:
                p['pos'][0] += p['dir'][0] * p['speed'] * dt_safe
                p['pos'][1] += p['dir'][1] * p['speed'] * dt_safe
                
                # Check collision with player
                px, py = self.game_manager.player.position
                dist = ((p['pos'][0] - px)**2 + (p['pos'][1] - py)**2)**0.5
                
                if dist < self.game_manager.player.hitbox_radius: # Hit player
                    actual_damage = self.game_manager.player.take_damage(p['damage'])
                    self.game_manager.add_log(f"Projectile hit you for {actual_damage} damage!")
                    self.callback_manager.on_enemy_attack(actual_damage, "Projectile")
                    
                    if not self.game_manager.player.is_alive:
                        self.game_manager.player_defeated()
                elif 0 <= p['pos'][0] <= Window.width and 0 <= p['pos'][1] <= Window.height:
                    surviving_projectiles.append(p)
                    
            self.game_manager.active_projectiles = surviving_projectiles

        # Draw game entities

        game_screen.game_canvas.canvas.clear()
        with game_screen.game_canvas.canvas:
            
            # Draw and Check Perks
            game_screen = self.screen_manager.get_screen('game')
            world_canvas = game_screen.game_world.canvas
            
            # Clear must be outside context to avoid pop_state IndexError
            world_canvas.clear()
            with world_canvas:
                # 1. Background (Grid loop with overlap to fix ghosting)
                grass_tile = "images/backgrounds/grass_tile.png"
                if os.path.exists(grass_tile):
                    if grass_tile not in self.sprite_sheets:
                        tex = CoreImage(grass_tile).texture
                        tex.mag_filter = 'nearest'
                        self.sprite_sheets[grass_tile] = tex
                    
                    tex = self.sprite_sheets[grass_tile]
                    Color(1, 1, 1, 1)
                    # Manually tile the floor (20x12 grid)
                    for tx in range(0, Window.width + 64, 64):
                        for ty in range(0, Window.height + 64, 64):
                            Rectangle(texture=tex, pos=(tx, ty), size=(65, 65))
                else:
                    Color(0.12, 0.28, 0.12, 1)
                    Rectangle(pos=(0, 0), size=(Window.width, Window.height))

                # 2. Decorations
                if hasattr(self.game_manager, 'decorations'):
                    for deco in self.game_manager.decorations:
                        dtype = deco['type']
                        if 'tree' in dtype: path = "images/decorations/tree.png"
                        elif 'bush' in dtype: path = f"images/decorations/bush{dtype[-1]}.png"
                        else: path = f"images/decorations/rock{dtype[-1]}.png"

                        if path not in self.sprite_sheets:
                            try:
                                t = CoreImage(path).texture
                                h = t.height
                                # Detect frame size based on standard Tiny Swords units (192, 256, 128)
                                frame_w = h
                                if t.width % 192 == 0 and t.height > 100: frame_w = 192
                                elif t.width % 256 == 0 and t.height > 100: frame_w = 256
                                
                                self.sprite_sheets[path] = SpriteSheet(path, frame_size=frame_w, cols=max(1, int(t.width/frame_w)))
                            except:
                                self.sprite_sheets[path] = SpriteSheet(path)
                        
                        sheet = self.sprite_sheets.get(path)
                        if sheet and sheet.texture:
                            Color(1, 1, 1, 1)
                            tex_coords = sheet.get_tex_coords(0)
                            Rectangle(texture=sheet.texture, tex_coords=tex_coords,
                                      pos=deco['pos'], size=deco['size'])
                        else:
                            Color(0.2, 0.3, 0.2, 0.6)
                            Rectangle(pos=deco['pos'], size=deco['size'])

                # 3. Perk Orbs (Golden & Detected)
                if 'active_perks' in state:
                    for perk in state['active_perks']:
                        # Suble Golden Glow
                        Color(1, 0.9, 0.1, 0.4)
                        Ellipse(pos=(perk['pos'][0]-15, perk['pos'][1]-15), size=(30, 30))
                        # Golden Center
                        Color(1, 0.9, 0.1, 1)
                        Ellipse(pos=(perk['pos'][0]-10, perk['pos'][1]-10), size=(20, 20))
                        
                        # TRIGGER detection: Proximity to player
                        ppos = self.game_manager.player.position
                        dist = ((ppos[0]-perk['pos'][0])**2 + (ppos[1]-perk['pos'][1])**2)**0.5
                        if dist < self.game_manager.player.collection_radius and not self.callback_manager.game_state['is_paused']:
                            # Handle collection
                            self.game_manager.active_perks.remove(perk)
                            game_screen.perk_overlay.opacity = 1
                            game_screen.perk_overlay.disabled = False
                            self.callback_manager.game_state['is_paused'] = True
                            self.game_manager.add_log("A Perk Orb has been collected!")

                # 4. Draw Player
                if state['player_stats']:
                    pos = self.game_manager.player.position
                    action = "idle"
                    if self.pressed_keys: action = "run"
                    if len(self.active_attacks) > 0: action = "attack"
                    player_anim_path = f"images/player/{action}.png"
                    if player_anim_path not in self.sprite_sheets:
                        self.sprite_sheets[player_anim_path] = SpriteSheet(player_anim_path)
                    sheet = self.sprite_sheets[player_anim_path]
                if sheet.texture:
                    tex_coords = sheet.get_tex_coords(self._current_frame, flip_x=not self.player_facing_right)
                    Color(1, 1, 1, 1)
                    Rectangle(texture=sheet.texture, tex_coords=tex_coords, 
                              pos=(pos[0]-125, pos[1]-125), size=(250, 250))
                else:
                    Color(0.2, 0.6, 1.0, 1)
                    Rectangle(pos=(pos[0], pos[1]), size=(20, 20))
                    
                # 5. Draw Enemies
                # Use game's elapsed time for synchronization with game_logic
                game_time = self.game_manager.time_manager.elapsed_time
                for enemy in self.game_manager.enemies:
                    if enemy.is_alive:
                        e_pos = enemy.position
                        e_name = enemy.name.lower()
                        
                        # Handle action transition (attack -> run/idle)
                        # We use 0.6s to match player attack duration for consistency
                        if enemy.action == "attack" and game_time - enemy.action_time > 0.6:
                            enemy.action = "run"
                            
                        # Select sheet based on action
                        # Actions: run, idle, attack
                        if e_name == "boss":
                            prefix = f"images/enemy/boss_{enemy.action}"
                        else:
                            # normal, tank, shooter
                            action_suffix = "" if enemy.action == "run" else f"_{enemy.action}"
                            prefix = f"images/enemy/{e_name}{action_suffix}"
                        
                        e_sheet_path = f"{prefix}.png"
                        if not os.path.exists(e_sheet_path): 
                            # Fallback to run if specific action doesn't exist
                            e_sheet_path = f"images/enemy/{e_name}.png"
                        if not os.path.exists(e_sheet_path): 
                            e_sheet_path = "images/enemy/orc.png"

                        if e_sheet_path not in self.sprite_sheets:
                            try:
                                # Get texture dimensions to detect frame size
                                t = CoreImage(e_sheet_path).texture
                                h = t.height
                                w = t.width
                                
                                # Tiny Swords standard: frame size = height
                                # Columns = width / frame size
                                frame_w = h
                                columns = max(1, int(w / h))
                                
                                # Special override for Boss (Skeleton) if needed
                                if "boss" in e_name.lower():
                                    frame_w = h
                                    columns = max(1, int(w / h))
                                elif "knight" in e_sheet_path:
                                    frame_w = 192
                                    columns = 6
                                
                                self.sprite_sheets[e_sheet_path] = SpriteSheet(e_sheet_path, frame_size=frame_w, cols=columns)
                            except:
                                self.sprite_sheets[e_sheet_path] = SpriteSheet(e_sheet_path)
                        
                        sheet = self.sprite_sheets.get(e_sheet_path)
                        if sheet and sheet.texture:
                            # Enemies face the player
                            px, py = self.game_manager.player.position
                            e_flip = (e_pos[0] < px)
                            # Determine animation frame
                            if enemy.action == "attack":
                                # Attack animation starts from frame 0 and plays based on time
                                anim_frame = int((game_time - enemy.action_time) / 0.1)
                            else:
                                # Normal animations use global frame
                                anim_frame = self._current_frame
                                
                            tex_coords = sheet.get_tex_coords(anim_frame, flip_x=not e_flip)
                            
                            Color(1, 1, 1, 1)
                            # Proportional scaling (Base: 192px -> 220px)
                            if e_name == "boss":
                                e_size = (600, 600)
                            else:
                                s = sheet.frame_size * (220/192)
                                e_size = (s, s)
                            
                            Rectangle(texture=sheet.texture, tex_coords=tex_coords, 
                                      pos=(e_pos[0] - e_size[0]/2, e_pos[1] - e_size[1]/2), size=e_size)
                        else:
                            if e_name == "lancer": Color(0.8, 0.4, 0.0, 1)
                            elif e_name == "archer": Color(0.8, 0.0, 0.8, 1)
                            elif e_name == "boss": Color(0.6, 0.0, 0.0, 1)
                            else: Color(0.8, 0.2, 0.2, 1)
                            
                            if e_name == "boss":
                                Rectangle(pos=(e_pos[0]-100, e_pos[1]-100), size=(200, 200))
                            else:
                                Rectangle(pos=(e_pos[0]-25, e_pos[1]-25), size=(50, 50))

                # 6. Draw Attacks (No visuals needed, just cooldown management)
                current_time = Clock.get_time()
                # Sync visibility duration with cooldown/animation length
                self.active_attacks = [a for a in self.active_attacks if current_time - a[2] < 0.6]
                    
                proj_path = "images/projectiles/bullet.png"
                if os.path.exists(proj_path):
                    if 'active_projectiles' in state:
                        for p in state['active_projectiles']:
                            # Calculate rotation angle based on direction
                            angle = math.degrees(math.atan2(p['dir'][1], p['dir'][0]))
                            
                            PushMatrix()
                            Rotate(angle=angle, origin=(p['pos'][0], p['pos'][1]))
                            Color(1, 1, 1, 1)
                            # Native size is 64x64, let's use 84x84 for better visibility
                            Rectangle(source=proj_path, pos=(p['pos'][0] - 42, p['pos'][1] - 42), size=(84, 84))
                            PopMatrix()
                else:
                    Color(1.0, 1.0, 0.0, 1)
                    if 'active_projectiles' in state:
                        for p in state['active_projectiles']:
                            Rectangle(pos=(p['pos'][0] - 5, p['pos'][1] - 5), size=(10, 10))

    
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
