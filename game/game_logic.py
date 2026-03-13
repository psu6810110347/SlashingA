"""
Game Logic Module
Contains core game mechanics and management
"""

from game.player import Player
from game.enemy import NormalEnemy, TankEnemy, ShooterEnemy
from game.time_manager import TimeManager
import random


class GameManager:
    """Main game manager"""
    
    def __init__(self, callback_manager=None):
        """Initialize game manager"""
        self.callback_manager = callback_manager
        self.player = Player()
        self.current_enemy = None
        self.level = 1
        self.combat_log = []
        self.is_combat_active = False
        self.time_manager = TimeManager()
        self.active_perks = []
        self.last_perk_spawn_time = 0
        self.last_regen_time = 0
        self.active_projectiles = []
        self.last_score_interval = 0
    
    def start_new_game(self):
        """Start new game"""
        self.player = Player()
        self.level = 1
        self.combat_log = []
        self.active_perks = []
        self.active_projectiles = []
        self.last_perk_spawn_time = 0
        self.last_regen_time = 0
        self.last_score_interval = 0
        self.time_manager.start_game_timer()
        self.spawn_enemy()
        print("New game started!")
    
    def spawn_enemy(self):
        """Spawn random enemy and scale based on time elapsed"""
        enemy_types = [NormalEnemy, TankEnemy, ShooterEnemy]
        enemy_class = random.choice(enemy_types)
        
        # Scale stats: 1 factor for every 5 minutes (300 seconds)
        scaling_factor = int(self.time_manager.elapsed_time // 300)
        self.current_enemy = enemy_class(scaling_factor)
        
        # Give enemy a random spawn position safely within 1200x600 boundaries
        spawn_x = random.randint(100, 1100)
        spawn_y = random.randint(100, 500)
        self.current_enemy.position = [spawn_x, spawn_y]
        
        self.is_combat_active = True
        self.add_log(f"A wild {self.current_enemy.name} appeared!")
        
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
    
    def player_attack(self):
        """Handle player attack"""
        if not self.is_combat_active or not self.current_enemy:
            return None
        
        # Check distance before allowing attack
        px, py = self.player.position
        ex, ey = self.current_enemy.position
        dist = ((px - ex)**2 + (py - ey)**2)**0.5
        
        if dist > 60:
            # Too far to hit
            return 0
            
        damage = self.player.attack + random.randint(-2, 5)
        actual_damage = self.current_enemy.take_damage(damage)
        
        message = f"You dealt {actual_damage} damage to {self.current_enemy.name}!"
        self.add_log(message)
        
        if not self.current_enemy.is_alive:
            self.defeat_enemy()
        else:
            self.enemy_attack()
        
        return actual_damage
    
    def player_skill(self, skill_name="power_slash"):
        """Handle player skill"""
        if not self.is_combat_active or not self.current_enemy:
            return None
        
        damage = 30
        actual_damage = self.current_enemy.take_damage(damage)
        
        message = f"You used {skill_name}! Dealt {actual_damage} damage!"
        self.add_log(message)
        
        if not self.current_enemy.is_alive:
            self.defeat_enemy()
        else:
            self.enemy_attack()
        
        return actual_damage
    
    def enemy_attack(self):
        """Handle enemy attack"""
        if not self.current_enemy or not self.is_combat_active:
            return None
        
        # If it's a Shooter, spawn a projectile instead of direct hit
        if isinstance(self.current_enemy, ShooterEnemy):
            # Check cooldown (every 2 seconds)
            current_time = self.time_manager.elapsed_time
            if current_time - getattr(self.current_enemy, 'last_shot_time', 0) >= 2.0:
                self.current_enemy.last_shot_time = current_time
                
                ex, ey = self.current_enemy.position
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
                    'damage': self.current_enemy.attack
                }
                self.active_projectiles.append(projectile)
                self.add_log(f"{self.current_enemy.name} fired a projectile!")
            return 0
            
        # Normal melee attack
        current_time = self.time_manager.elapsed_time
        if current_time - getattr(self.current_enemy, 'last_shot_time', 0) >= 1.5:
            ex, ey = self.current_enemy.position
            px, py = self.player.position
            dist = ((px - ex)**2 + (py - ey)**2)**0.5
            
            # Melee range is around 50 pixels
            if dist < 50:
                self.current_enemy.last_shot_time = current_time
                damage = self.current_enemy.attack_player()
                actual_damage = self.player.take_damage(damage)
                
                message = f"{self.current_enemy.name} dealt {actual_damage} damage to you!"
                self.add_log(message)
                
                if self.callback_manager:
                    self.callback_manager.on_enemy_attack(actual_damage, self.current_enemy.name)
                
                if not self.player.is_alive:
                    self.player_defeated()
                
                return actual_damage
        return 0


    
    def defeat_enemy(self):
        """Handle enemy defeat"""
        rewards = self.current_enemy.defeat()
        self.player.gain_exp(rewards['exp'])
        self.player.add_gold(rewards['gold'])
        
        message = f"{self.current_enemy.name} defeated! Gained {rewards['exp']} EXP and {rewards['gold']} gold!"
        self.add_log(message)
        
        self.is_combat_active = False
        self.level += 1
        
        if self.callback_manager:
            self.callback_manager.on_level_up(self.level)
            
        # Spawn a new enemy!
        self.spawn_enemy()

    
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
            
        # Passive HP Regeneration (1 HP every 3 seconds)
        if current_time - self.last_regen_time >= 3.0:
            if self.player.hp > 0 and self.player.hp < self.player.max_hp:
                self.player.heal(1)
            self.last_regen_time = current_time
            
        return {
            'player_stats': self.player.get_stats(),
            'enemy_stats': self.current_enemy.get_stats() if self.current_enemy else None,
            'level': self.level,
            'is_combat_active': self.is_combat_active,
            'combat_log': self.combat_log,
            'time_state': self.time_manager.get_game_state(),
            'active_perks': self.active_perks,
            'active_projectiles': self.active_projectiles
        }
