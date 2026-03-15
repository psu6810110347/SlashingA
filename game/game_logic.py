"""
Game Logic Module
Contains core game mechanics and management
"""

from game.player import Player
from game.enemy import NormalEnemy, TankEnemy, ShooterEnemy, Boss
from game.time_manager import TimeManager
import random


class GameManager:
    """Main game manager"""
    
    def __init__(self, callback_manager=None):
        """Initialize game manager"""
        self.callback_manager = callback_manager
        self.player = Player()
        self.enemies = []
        self.level = 1
        self.combat_log = []
        self.is_combat_active = False
        self.time_manager = TimeManager()
        self.active_perks = []
        self.last_perk_spawn_time = 0
        self.last_regen_time = 0
        self.active_projectiles = []
        self.last_score_interval = 0
        self.last_boss_spawn_time = 0
        self.wave_number = 0
    
    def start_new_game(self):
        """Start new game"""
        self.player = Player()
        self.level = 1
        self.combat_log = []
        self.active_perks = []
        self.active_projectiles = []
        self.enemies = []
        self.last_perk_spawn_time = 0
        self.last_regen_time = 0
        self.last_score_interval = 0
        self.last_boss_spawn_time = 0
        self.wave_number = 0
        self.enemies_to_spawn = 0
        self.last_spawn_time = 0
        
        # Generate random decorations with No-Overlap check
        self.decorations = []
        deco_types = ['bush1', 'bush2', 'rock1', 'rock2', 'tree']
        # Reduced count slightly for cleaner look (10-15)
        for _ in range(random.randint(10, 15)):
            dtype = random.choice(deco_types)
            
            # Size varies by type for collision/spacing check
            if 'rock' in dtype:
                size = (random.randint(80, 120), random.randint(80, 120))
            elif 'bush' in dtype:
                size = (random.randint(150, 220), random.randint(150, 220))
            else: # tree
                size = (random.randint(250, 350), random.randint(250, 350))

            # Attempt to find a non-overlapping spot (max 10 tries)
            for _ in range(10):
                dx = random.randint(50, 1200)
                dy = random.randint(50, 650)
                
                # Check distance to existing decorations
                too_close = False
                for existing in self.decorations:
                    ex, ey = existing['pos']
                    dist = ((dx - ex)**2 + (dy - ey)**2)**0.5
                    # Dynamic spacing based on size
                    min_dist = (size[0] + existing['size'][0]) * 0.4
                    if dist < min_dist:
                        too_close = True
                        break
                
                if not too_close:
                    self.decorations.append({'type': dtype, 'pos': (dx, dy), 'size': size})
                    break

        self.time_manager.start_game_timer()
        print("New game started!")
        self.start_next_wave()
    
    def start_next_wave(self):
        """Calculate and queue the next wave of enemies"""
        self.wave_number += 1
        self._boss_spawned_this_wave = False
        
        # Base wave is 5. Increase by 2 for every 2 minutes (120 seconds)
        time_elapsed = self.time_manager.elapsed_time
        extra_enemies = int(time_elapsed // 120) * 2
        enemy_count = 5 + extra_enemies
        
        self.enemies_to_spawn = enemy_count
        self.last_spawn_time = self.time_manager.elapsed_time
        
        if self.callback_manager:
            self.callback_manager.on_wave_start(self.wave_number, enemy_count)
            
        self.is_combat_active = True

    def count_total_widgets(self, root_widget):
        """Recursively count all widgets starting from root"""
        count = 1  # count the root_widget itself
        if hasattr(root_widget, 'children'):
            for child in root_widget.children:
                count += self.count_total_widgets(child)
        return count

    def count_callbacks(self):
        """Count methods in callback_manager that start with 'on_'"""
        if not self.callback_manager:
            return 0
        count = 0
        for attr_name in dir(self.callback_manager):
            if attr_name.startswith('on_') and callable(getattr(self.callback_manager, attr_name)):
                count += 1
        return count

    def spawn_boss(self):
        """Spawn the Boss enemy with scaling based on elapsed time"""
        scaling_factor = int(self.time_manager.elapsed_time // 300)
        boss = Boss(scaling_factor)
        # Spawn off-screen
        spawn_x = random.randint(0, 1280)
        spawn_y = random.randint(750, 900)
        boss.position = [spawn_x, spawn_y]
        self.enemies.append(boss)
        self.add_log(f"WARNING: A mighty Boss has appeared! (Scale: {scaling_factor})")
        if self.callback_manager and hasattr(self.callback_manager, 'on_boss_spawn'):
            self.callback_manager.on_boss_spawn(self.wave_number)

    def spawn_enemy(self):
        """Spawn random enemy off-screen and scale based on time elapsed"""
        enemy_types = [NormalEnemy, TankEnemy, ShooterEnemy]
        enemy_class = random.choice(enemy_types)
        
        # Scale stats: 1 factor for every 5 minutes (300 seconds)
        scaling_factor = int(self.time_manager.elapsed_time // 300)
        new_enemy = enemy_class(scaling_factor)
        
        # Spawn off-screen safely outside the Window borders (1280x720 + margins)
        # Randomly choose one of the 4 edges to spawn just outside of
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        
        if edge == 'top':
            spawn_x = random.randint(0, 1280)
            spawn_y = random.randint(750, 900)
        elif edge == 'bottom':
            spawn_x = random.randint(0, 1280)
            spawn_y = random.randint(-150, -50)
        elif edge == 'left':
            spawn_x = random.randint(-200, -50)
            spawn_y = random.randint(0, 720)
        else: # right
            spawn_x = random.randint(1330, 1500)
            spawn_y = random.randint(0, 720)
            
        new_enemy.position = [spawn_x, spawn_y]
        
        self.enemies.append(new_enemy)
        self.add_log(f"A wild {new_enemy.name} appeared from the {edge}!")
        
    def spawn_perk(self):
        """Spawn a generic perk at a random location"""
        # We will bound it roughly to the screen resolution 1200x600 safely
        x = random.randint(100, 1000)
        y = random.randint(100, 600)
        
        perk = {
            'type': 'generic',
            'label': 'Perk Orb',
            'pos': [x, y],
            'size': [25, 25]
        }
        self.add_log("A Perk Orb has appeared!")
        self.active_perks.append(perk)
    
    def player_attack(self, is_facing_right=True):
        """Handle player attack with directional check"""
        if not self.is_combat_active or not self.enemies:
            return None
        
        px, py = self.player.position
        
        # Find the closest enemy within range AND in front of player
        closest_enemy = None
        min_dist = float('inf')
        
        for enemy in self.enemies:
            ex, ey = enemy.position
            dx = ex - px
            dist = (dx**2 + (py - ey)**2)**0.5
            
            # Distance check
            if dist <= self.player.attack_range:
                # Directional check: enemy must be on the side the player is facing
                # If facing right, dx should be positive. If facing left, dx should be negative.
                # We allow a small margin (e.g. 5px) to avoid being too strict on vertical overlap
                is_in_front = (is_facing_right and dx > -10) or (not is_facing_right and dx < 10)
                
                if is_in_front and dist < min_dist:
                    min_dist = dist
                    closest_enemy = enemy
                
        if not closest_enemy:
            return 0 # Too far or wrong direction
            
        damage = self.player.attack + random.randint(-2, 5)
        actual_damage = closest_enemy.take_damage(damage)
        
        message = f"You dealt {actual_damage} damage to {closest_enemy.name}!"
        self.add_log(message)
        
        if not closest_enemy.is_alive:
            self.defeat_enemy(closest_enemy)
        else:
            self.enemy_attack()
        
        return actual_damage
    
    def player_skill(self, skill_name="power_slash"):
        """Handle player skill (AOE hit on all nearby enemies)"""
        if not self.is_combat_active or not self.enemies:
            return None
            
        px, py = self.player.position
        total_damage = 0
        enemies_hit = 0
        
        # Need to capture list beforehand as defeat_enemy modifies self.enemies
        hit_enemies = []
        for enemy in self.enemies:
            ex, ey = enemy.position
            dist = ((px - ex)**2 + (py - ey)**2)**0.5
            if dist <= self.player.attack_range * 1.5: # Wider AOE range
                hit_enemies.append(enemy)
                
        for enemy in hit_enemies:
            damage = 30
            actual_damage = enemy.take_damage(damage)
            total_damage += actual_damage
            enemies_hit += 1
            
            if not enemy.is_alive:
                self.defeat_enemy(enemy)
                
        if enemies_hit > 0:
            message = f"You used {skill_name}! Dealt {total_damage} damage across {enemies_hit} enemies!"
            self.add_log(message)
            self.enemy_attack()
            
        return total_damage
    
    def enemy_attack(self):
        """Handle enemy attack"""
        if not self.enemies or not self.is_combat_active:
            return None
            
        total_damage_taken = 0
            
        for enemy in self.enemies:
            # If it's a Shooter, spawn a projectile instead of direct hit
            if isinstance(enemy, ShooterEnemy):
                # Check cooldown (every 2 seconds)
                current_time = self.time_manager.elapsed_time
                if current_time - getattr(enemy, 'last_shot_time', 0) >= 2.0:
                    enemy.last_shot_time = current_time
                    
                    ex, ey = enemy.position
                    px, py = self.player.position
                    
                    # Calculate direction vector
                    dx, dy = px - ex, py - ey
                    dist = (dx**2 + dy**2)**0.5
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                    
                    # Projectile payload
                    projectile = {
                        'pos': [ex, ey],
                        'dir': [dx, dy],
                        'speed': 150,  # pixels per second
                        'damage': enemy.attack
                    }
                    self.active_projectiles.append(projectile)
                    self.add_log(f"{enemy.name} fired a projectile!")
                continue
                
            # Normal melee attack
            current_time = self.time_manager.elapsed_time
            if current_time - getattr(enemy, 'last_shot_time', 0) >= 1.5:
                ex, ey = enemy.position
                px, py = self.player.position
                dist = ((px - ex)**2 + (py - ey)**2)**0.5
                
                # Melee range is specific to enemy type
                if dist < enemy.attack_range:
                    enemy.last_shot_time = current_time
                    damage = enemy.attack_player()
                    actual_damage = self.player.take_damage(damage)
                    total_damage_taken += actual_damage
                    
                    message = f"{enemy.name} dealt {actual_damage} damage to you!"
                    self.add_log(message)
                    
                    if self.callback_manager:
                        self.callback_manager.on_enemy_attack(actual_damage, enemy.name)
                    
                    if not self.player.is_alive:
                        self.player_defeated()
                        return total_damage_taken
                        
        return total_damage_taken


    
    def defeat_enemy(self, enemy):
        """Handle specific enemy defeat"""
        rewards = enemy.defeat()
        self.player.gain_exp(rewards['exp'])
        self.player.add_gold(rewards['gold'])
        
        message = f"{enemy.name} defeated! Gained {rewards['exp']} EXP and {rewards['gold']} gold!"
        self.add_log(message)
        
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            
        # Check if wave is cleared
        if len(self.enemies) == 0 and self.enemies_to_spawn <= 0:
            self.is_combat_active = False
            self.level += 1
            
            if self.callback_manager:
                self.callback_manager.on_level_up(self.level)
                
            # Start the next wave!
            self.start_next_wave()

    
    def player_defeated(self):
        """Handle player defeat"""
        message = "You were defeated! Game Over."
        self.add_log(message)
        self.is_combat_active = False
    
    def add_log(self, message):
        """Add message to combat log"""
        self.combat_log.append(message)
        print(message)
    
    def get_game_state(self):
        """Get current game state"""
        self.time_manager.update()
        
        # Check if we should spawn a perk (every 5 seconds for testing)
        current_time = self.time_manager.elapsed_time
        if current_time - self.last_perk_spawn_time >= 5.0:
            self.spawn_perk()
            self.last_perk_spawn_time = current_time
            
        # Check for 5-minute score bonus
        score_intervals = int(current_time // 300)
        if score_intervals > self.last_score_interval:
            self.player.score += 100
            self.add_log("Survived 5 minutes! +100 Score!")
            self.last_score_interval = score_intervals
            
        # Check for Boss Spawn (Every 10 waves)
        if self.wave_number > 0 and self.wave_number % 10 == 0:
            # Only spawn boss once per wave milestone
            if not getattr(self, '_boss_spawned_this_wave', False):
                if self.callback_manager and self.callback_manager.app and self.callback_manager.app.root:
                    widget_count = self.count_total_widgets(self.callback_manager.app.root)
                    callback_count = self.count_callbacks()
                    self.add_log(f"Verification Check: Widgets={widget_count}/30, Callbacks={callback_count}/10")
                    if widget_count >= 30 and callback_count >= 10:
                        self.spawn_boss()
                        self._boss_spawned_this_wave = True
            
        # Enemy Staggered Spawning logic
        # Spawn an enemy every 1.5 seconds if there are enemies left in the queue
        if self.enemies_to_spawn > 0:
            if current_time - self.last_spawn_time >= 1.5:
                self.spawn_enemy()
                self.enemies_to_spawn -= 1
                self.last_spawn_time = current_time

        # Passive HP Regeneration (1 HP every 3 seconds)
        if current_time - self.last_regen_time >= 3.0:
            if self.player.hp > 0 and self.player.hp < self.player.max_hp:
                self.player.heal(1)
            self.last_regen_time = current_time
            
        return {
            'player_stats': self.player.get_stats(),
            'enemy_stats': [e.get_stats() for e in self.enemies], # Now returns a list
            'level': self.level,
            'wave': self.wave_number,
            'is_combat_active': self.is_combat_active,
            'combat_log': self.combat_log,
            'time_state': self.time_manager.get_game_state(),
            'active_perks': self.active_perks,
            'active_projectiles': self.active_projectiles
        }
