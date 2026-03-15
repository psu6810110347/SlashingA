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
from ui.widgets import MainMenuScreen, GameScreen, PauseMenuPopup, GameOverScreen
from kivy.core.image import Image as CoreImage
import os
import time

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
        
    def get_tex_coords(self, frame_x, frame_y=0):
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
        self._current_frame = 0
    
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
                    
                    # Stop moving if close enough to player
                    if dist > 40:
                        dx /= dist
                        dy /= dist
                        move_speed = getattr(e, 'speed', 3) * 20
                        e.position[0] += dx * move_speed * dt
                        e.position[1] += dy * move_speed * dt
            
            # Update Projectiles
            dt_safe = dt if dt < 0.1 else 0.016
            surviving_projectiles = []
            for p in self.game_manager.active_projectiles:
                p['pos'][0] += p['dir'][0] * p['speed'] * dt_safe
                p['pos'][1] += p['dir'][1] * p['speed'] * dt_safe
                
                # Check collision with player
                px, py = self.game_manager.player.position
                dist = ((p['pos'][0] - px)**2 + (p['pos'][1] - py)**2)**0.5
                
                if dist < 20: # Hit player
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
            if 'active_perks' in state and state['active_perks']:
                perks_copy = state['active_perks'][:] # iterate over a copy so we can remove
                for perk in perks_copy:
                    px, py = perk['pos']
                    if perk['type'] == 'generic':
                        Color(1.0, 1.0, 1.0, 1)  # White Orb
                    elif perk['type'] == 'max_hp':
                        Color(0.2, 1.0, 0.2, 1)  # Green Orb for HP
                    elif perk['type'] == 'speed':
                        Color(0.2, 0.2, 1.0, 1)  # Blue Orb for Speed
                    elif perk['type'] == 'attack':
                        Color(1.0, 0.2, 0.2, 1)  # Red Orb for Attack
                    elif perk['type'] == 'defense':
                        Color(0.2, 1.0, 1.0, 1)  # Cyan Orb for Defense
                    else:
                        Color(1.0, 1.0, 1.0, 1)
                    Rectangle(pos=(px, py), size=(perk['size'][0], perk['size'][1]))
                    
                    # Collision check
                    player_x, player_y = self.game_manager.player.position
                    dist = ((player_x - px)**2 + (player_y - py)**2)**0.5
                    if dist < 25:
                        self.game_manager.active_perks.remove(perk)
                        self.callback_manager.game_state['is_paused'] = True
                        
                        # Show the hidden overlay
                        game_screen = self.root.get_screen('game')
                        game_screen.perk_overlay.opacity = 1
                        game_screen.perk_overlay.disabled = False
                    
            # Draw Tiled Background (Grid based for stability)
            grass_tile = "images/backgrounds/grass_tile.png"
            if os.path.exists(grass_tile):
                if grass_tile not in self.sprite_sheets:
                    tex = CoreImage(grass_tile).texture
                    tex.mag_filter = 'nearest'
                    self.sprite_sheets[grass_tile] = tex
                
                tex = self.sprite_sheets[grass_tile]
                Color(1, 1, 1, 1)
                # Manually tile the floor (20x12 grid)
                for x in range(0, Window.width, 64):
                    for y in range(0, Window.height, 64):
                        # Add a tiny overlap (+1) to prevent hairline gaps
                        Rectangle(texture=tex, pos=(x, y), size=(65, 65))
            else:
                Color(0.12, 0.28, 0.12, 1) # Fallback Ground grass color
                Rectangle(pos=(0, 0), size=(Window.width, Window.height))

            # Draw Decorations (Sliced scenery)
            if hasattr(self.game_manager, 'decorations'):
                Color(1, 1, 1, 1)
                for deco in self.game_manager.decorations:
                    dtype = deco['type']
                    if 'tree' in dtype:
                        path = "images/decorations/tree.png"
                    elif 'bush' in dtype:
                        idx = dtype[-1]
                        path = f"images/decorations/bush{idx}.png"
                    else: # rock
                        idx = dtype[-1]
                        path = f"images/decorations/rock{idx}.png"

                    if path not in self.sprite_sheets:
                        # Adaptive sizing: Most Tiny Swords deco are sheets where cell_size = height
                        try:
                            temp_tex = CoreImage(path).texture
                            if temp_tex:
                                h = temp_tex.height
                                self.sprite_sheets[path] = SpriteSheet(path, frame_size=h, cols=max(1, int(temp_tex.width/h)))
                        except:
                            self.sprite_sheets[path] = SpriteSheet(path, frame_size=64, cols=1)
                    
                    sheet = self.sprite_sheets.get(path)
                    if sheet and sheet.texture:
                        # Decorations usually single frame or first frame is fine
                        tex_coords = sheet.get_tex_coords(0) 
                        Rectangle(texture=sheet.texture, tex_coords=tex_coords,
                                  pos=deco['pos'], size=deco['size'])
                    else:
                        # Fallback colored squares
                        if 'bush' in dtype: Color(0.1, 0.4, 0.1, 1)
                        elif 'tree' in dtype: Color(0.05, 0.3, 0.05, 1)
                        else: Color(0.5, 0.5, 0.5, 1)
                        Rectangle(pos=deco['pos'], size=deco['size'])
                        Color(1, 1, 1, 1)

            # Draw Player
            if state['player_stats']:
                pos = self.game_manager.player.position
                # Tiny Swords Free Pack uses separate files per action
                action = "idle"
                if self.pressed_keys: action = "run"
                if len(self.active_attacks) > 0: action = "attack"
                
                player_anim_path = f"images/player/{action}.png"
                
                if player_anim_path not in self.sprite_sheets:
                    self.sprite_sheets[player_anim_path] = SpriteSheet(player_anim_path)
                
                sheet = self.sprite_sheets[player_anim_path]
                if sheet.texture:
                    tex_coords = sheet.get_tex_coords(self._current_frame)
                    Color(1, 1, 1, 1)
                    Rectangle(texture=sheet.texture, tex_coords=tex_coords, 
                              pos=(pos[0]-125, pos[1]-125), size=(250, 250)) # Massive player sprite
                else:
                    Color(0.2, 0.6, 1.0, 1)
                    Rectangle(pos=(pos[0], pos[1]), size=(20, 20))
                
            # Draw Enemies
            for enemy in self.game_manager.enemies:
                if enemy.is_alive:
                    e_pos = enemy.position
                    e_name = enemy.name
                    
                    if e_name == "Boss":
                        action = "run"
                        e_sheet_path = f"images/enemy/boss_{action}.png"
                    else:
                        e_sheet_path = f"images/enemy/{e_name.lower()}.png"
                        if not os.path.exists(e_sheet_path):
                            # Default all remaining normal enemies to use Orc sprite
                            e_sheet_path = "images/enemy/orc.png"

                    
                    if e_sheet_path not in self.sprite_sheets:
                        if "orc" in e_name.lower() or "orc" in e_sheet_path:
                            self.sprite_sheets[e_sheet_path] = SpriteSheet(e_sheet_path, frame_size=100, cols=6)
                        elif "boss" in e_name.lower():
                            self.sprite_sheets[e_sheet_path] = SpriteSheet(e_sheet_path, frame_size=128, cols=6)
                        else:
                            # Try to auto-detect frame size from height
                            try:
                                temp_tex = CoreImage(e_sheet_path).texture
                                if temp_tex:
                                    self.sprite_sheets[e_sheet_path] = SpriteSheet(e_sheet_path, frame_size=temp_tex.height)
                            except:
                                self.sprite_sheets[e_sheet_path] = SpriteSheet(e_sheet_path)
                    
                    sheet = self.sprite_sheets.get(e_sheet_path)
                    if sheet and sheet.texture:
                        tex_coords = sheet.get_tex_coords(self._current_frame)
                        Color(1, 1, 1, 1)
                        e_size = (220, 220) # Gigantic enemy sprites
                        if e_name == "Boss": e_size = (600, 600) # Gigantic skeleton boss
                        
                        Rectangle(texture=sheet.texture, tex_coords=tex_coords, 
                                  pos=(e_pos[0] - e_size[0]/2, e_pos[1] - e_size[1]/2), size=e_size)
                    else:
                        # Fallback shapes (larger and centered)
                        if e_name == "Tank": Color(0.8, 0.4, 0.0, 1)
                        elif e_name == "Shooter": Color(0.8, 0.0, 0.8, 1)
                        elif e_name == "Boss": Color(0.6, 0.0, 0.0, 1)
                        else: Color(0.8, 0.2, 0.2, 1)
                        Rectangle(pos=(e_pos[0]-25, e_pos[1]-25), size=(50, 50))

            
            # Draw Attacks
            current_time = Clock.get_time()
            self.active_attacks = [a for a in self.active_attacks if current_time - a[2] < 0.2]
            Color(1.0, 0.2, 0.2, 1)
            for attack_x, attack_y, _ in self.active_attacks:
                Rectangle(pos=(attack_x - 10, attack_y - 10), size=(20, 20))
                
            # Draw Projectiles
            proj_path = "images/projectiles/bullet.png"
            if os.path.exists(proj_path):
                Color(1, 1, 1, 1)
                if 'active_projectiles' in state:
                    for p in state['active_projectiles']:
                        Rectangle(source=proj_path, pos=(p['pos'][0] - 10, p['pos'][1] - 10), size=(20, 20))
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
