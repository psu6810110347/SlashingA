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
        }


class NormalEnemy(Enemy):
    """Normal enemy type"""
    def __init__(self, scaling_factor=0):
        super().__init__("Normal", 1)
        self.hp = 10 + (scaling_factor * 10)
        self.max_hp = self.hp
        self.attack = 10 + (scaling_factor * 5)
        self.speed = 4
        self.hitbox_radius = 50
        self.attack_range = 80


class TankEnemy(Enemy):
    """Tank enemy type"""
    def __init__(self, scaling_factor=0):
        super().__init__("Tank", 1)
        self.hp = 20 + (scaling_factor * 10)
        self.max_hp = self.hp
        self.attack = 10 + (scaling_factor * 5)
        self.speed = 3
        self.hitbox_radius = 100 # Large tank
        self.attack_range = 90


class ShooterEnemy(Enemy):
    """Shooter enemy type"""
    def __init__(self, scaling_factor=0):
        super().__init__("Shooter", 1)
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
