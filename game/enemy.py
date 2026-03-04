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
        }


class NormalEnemy(Enemy):
    """Normal enemy type"""
    def __init__(self, scaling_factor=0):
        super().__init__("Normal", 1)
        self.hp = 10 + (scaling_factor * 10)
        self.max_hp = self.hp
        self.attack = 10 + (scaling_factor * 5)
        self.speed = 4


class TankEnemy(Enemy):
    """Tank enemy type"""
    def __init__(self, scaling_factor=0):
        super().__init__("Tank", 1)
        self.hp = 20 + (scaling_factor * 10)
        self.max_hp = self.hp
        self.attack = 10 + (scaling_factor * 5)
        self.speed = 3


class ShooterEnemy(Enemy):
    """Shooter enemy type"""
    def __init__(self, scaling_factor=0):
        super().__init__("Shooter", 1)
        self.hp = 10 + (scaling_factor * 10)
        self.max_hp = self.hp
        self.attack = 10 + (scaling_factor * 5)
        self.speed = 4

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
        }


class Goblin(Enemy):
    """Goblin enemy"""
    def __init__(self, level=1):
        super().__init__("Goblin", level)
        self.hp = 20 + (level * 5)
        self.max_hp = self.hp
        self.attack = 4 + level


class Orc(Enemy):
    """Orc enemy"""
    def __init__(self, level=1):
        super().__init__("Orc", level)
        self.hp = 40 + (level * 15)
        self.max_hp = self.hp
        self.attack = 8 + (level * 2)
        self.defense = 3 + level


class Skeleton(Enemy):
    """Skeleton enemy"""
    def __init__(self, level=1):
        super().__init__("Skeleton", level)
        self.hp = 25 + (level * 8)
        self.max_hp = self.hp
        self.attack = 6 + level
        self.defense = 1 + level


class Boss(Enemy):
    """Boss enemy"""
    def __init__(self, name="Boss", level=1):
        super().__init__(name, level)
        self.hp = 100 + (level * 50)
        self.max_hp = self.hp
        self.attack = 15 + (level * 3)
        self.defense = 5 + level
        self.exp_reward = 500 * level
        self.gold_reward = 100 * level
