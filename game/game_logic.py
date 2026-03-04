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
    
    def __init__(self):
        """Initialize game manager"""
        self.player = Player()
        self.current_enemy = None
        self.level = 1
        self.combat_log = []
        self.is_combat_active = False
        self.time_manager = TimeManager()
        self.active_perks = []
        self.last_perk_spawn_time = 0
    
    def start_new_game(self):
        """Start new game"""
        self.player = Player()
        self.level = 1
        self.combat_log = []
        self.active_perks = []
        self.last_perk_spawn_time = 0
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
        
        self.is_combat_active = True
        self.add_log(f"A wild {self.current_enemy.name} appeared!")
        
    def spawn_perk(self):
        """Spawn a perk at a random location"""
        # We will bound it roughly to the screen resolution 1200x600 safely
        x = random.randint(100, 1000)
        y = random.randint(100, 600)
        
        perk_type = random.choice(['max_hp', 'speed'])
        
        if perk_type == 'max_hp':
            perk = {
                'type': 'max_hp',
                'label': '+10 Max HP',
                'pos': [x, y],
                'size': [25, 25]
            }
            self.add_log("A Max HP Perk has appeared!")
        else:
            perk = {
                'type': 'speed',
                'label': '+1 Speed',
                'pos': [x, y],
                'size': [25, 25]
            }
            self.add_log("A Speed Perk has appeared!")
            
        self.active_perks.append(perk)
    
    def player_attack(self):
        """Handle player attack"""
        if not self.is_combat_active or not self.current_enemy:
            return None
        
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
        
        damage = self.current_enemy.attack_player()
        actual_damage = self.player.take_damage(damage)
        
        message = f"{self.current_enemy.name} dealt {actual_damage} damage to you!"
        self.add_log(message)
        
        if not self.player.is_alive:
            self.player_defeated()
        
        return actual_damage
    
    def defeat_enemy(self):
        """Handle enemy defeat"""
        rewards = self.current_enemy.defeat()
        self.player.gain_exp(rewards['exp'])
        self.player.add_gold(rewards['gold'])
        
        message = f"{self.current_enemy.name} defeated! Gained {rewards['exp']} EXP and {rewards['gold']} gold!"
        self.add_log(message)
        
        self.is_combat_active = False
        self.level += 1
    
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
            
        return {
            'player_stats': self.player.get_stats(),
            'enemy_stats': self.current_enemy.get_stats() if self.current_enemy else None,
            'level': self.level,
            'is_combat_active': self.is_combat_active,
            'combat_log': self.combat_log,
            'time_state': self.time_manager.get_game_state(),
            'active_perks': self.active_perks
        }
