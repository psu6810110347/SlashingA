"""
Enemy Module
Contains enemy classes and mechanics
"""

import random


class Enemy:
    """Base enemy class"""
    
    def __init__(self, name="Enemy", level=1):
        """Initialize enemy"""
        self.name = name
        self.level = level
        self.hp = 30 + (level * 10)
        self.max_hp = self.hp
        self.attack = 5 + (level * 2)
        self.defense = 2 + level
        self.exp_reward = 50 * level
        self.gold_reward = 10 * level
        self.loot = []
        self.position = [0, 0]
        self.is_alive = True
        
        # Hitbox and Ranges (default)
        self.hitbox_radius = 50
        self.attack_range = 80
        
        # Action tracking
        self.action = "run"
        self.action_time = 0
    
    def take_damage(self, damage):
        """Take damage"""
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return actual_damage
    
    def attack_player(self):
        """Attack player"""
        # Base damage with some randomness
        damage = self.attack + random.randint(-3, 3)
        return max(1, damage)
    
    def defeat(self):
        """Handle enemy defeat"""
        return {
            'exp': self.exp_reward,
            'gold': self.gold_reward,
            'loot': self.loot
        }
    
    def get_stats(self):
        """Get enemy stats"""
        return {
            'name': self.name,
            'level': self.level,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'defense': self.defense,
            'speed': getattr(self, 'speed', 0),
            'pos': self.position,
            'hitbox_radius': self.hitbox_radius,
            'attack_range': self.attack_range,
            'action': self.action,
        }


class KnightEnemy(Enemy):
    """Knight enemy type (formerly Normal)"""
    def __init__(self, scaling_factor=0):
        super().__init__("Knight", 1)
        self.hp = 10 + (scaling_factor * 10)
        self.max_hp = self.hp
        self.attack = 10 + (scaling_factor * 5)
        self.speed = 4
        self.hitbox_radius = 50
        self.attack_range = 80


class LancerEnemy(Enemy):
    """Lancer enemy type (formerly Tank)"""
    def __init__(self, scaling_factor=0):
        super().__init__("Lancer", 1)
        self.hp = 20 + (scaling_factor * 10)
        self.max_hp = self.hp
        self.attack = 10 + (scaling_factor * 5)
        self.speed = 3
        self.hitbox_radius = 100 # Large tank
        self.attack_range = 90


class ArcherEnemy(Enemy):
    """Archer enemy type (formerly Shooter)"""
    def __init__(self, scaling_factor=0):
        super().__init__("Archer", 1)
        self.hp = 10 + (scaling_factor * 10)
        self.max_hp = self.hp
        self.attack = 10 + (scaling_factor * 5)
        self.speed = 4
        self.last_shot_time = 0
        self.hitbox_radius = 50
        self.attack_range = 300 # Archer range


class Boss(Enemy):
    """Boss enemy"""
    def __init__(self, scaling_factor=0):
        super().__init__("Boss", 1)
        self.hp = 100 + (scaling_factor * 50)
        self.max_hp = self.hp
        self.attack = 15 + (scaling_factor * 5)
        self.defense = 5 + (scaling_factor * 2)
        self.speed = 2
        self.exp_reward = 500 + (scaling_factor * 100)
        self.gold_reward = 100 + (scaling_factor * 50)
        self.hitbox_radius = 180 # Massive boss
        self.attack_range = 150
