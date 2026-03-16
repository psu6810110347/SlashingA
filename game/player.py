"""
Player Module
Contains player character class and mechanics
"""


class Player:
    """Player character class"""
    
    def __init__(self, name="Hero"):
        """Initialize player"""
        self.name = name
        self.level = 1
        self.exp = 0
        self.exp_to_level = 100
        self.hp = 100
        self.max_hp = 100
        self.mp = 50
        self.max_mp = 50
        self.attack = 10
        self.defense = 0
        self.speed = 5
        self.gold = 0
        self.score = 0
        self.inventory = []
        self.skills = []
        self.position = [0, 0]
        self.is_alive = True
        
        # Hitbox and Ranges
        self.hitbox_radius = 45
        self.attack_range = 100
        self.collection_radius = 60
    
    def take_damage(self, damage):
        """Take damage"""
        actual_damage = max(1, damage - self.defense)
        if damage - actual_damage > 0:
            print(f"Defense blocked {damage - actual_damage} damage!")
            
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return actual_damage
    
    def heal(self, amount):
        """Heal player"""
        self.hp = min(self.hp + amount, self.max_hp)
        return self.hp
    
    def gain_exp(self, amount):
        """Gain experience"""
        self.exp += amount
        if self.exp >= self.exp_to_level:
            self.level_up()
            self.exp -= self.exp_to_level
    
    def level_up(self):
        """Level up"""
        self.level += 1
        self.max_hp += 7
        self.hp += 7 # slightly buffed from 5 to 7 for better survival
        self.attack += 2
        # Defense increases every 2 levels to prevent invulnerability
        if self.level % 2 == 0:
            self.defense += 1
        self.exp_to_level = int(self.exp_to_level * 1.3) # Faster scaling of EXP requirements
        print(f"{self.name} leveled up to {self.level}!")
    
    def add_gold(self, amount):
        """Add gold"""
        self.gold += amount
    
    def move(self, x, y):
        """Move player"""
        self.position = [x, y]
    
    def get_stats(self):
        """Get player stats"""
        return {
            'name': self.name,
            'level': self.level,
            'exp': self.exp,
            'hp': self.hp,
            'max_hp': self.max_hp,          
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'gold': self.gold,
            'score': self.score,
            'pos': self.position,
            'hitbox_radius': self.hitbox_radius,
            'attack_range': self.attack_range,
        }
