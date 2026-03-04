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
        self.hp = 100.0
        self.max_hp = 100.0
        self.attack = 5
        self.speed = 5
        self.health_regen_rate = 1.0  # Regens 1 HP per second
        self.gold = 0
        self.inventory = []
        self.position = [0, 0]
        self.is_alive = True
    
    def take_damage(self, damage):
        """Take damage"""
        actual_damage = max(1, damage)
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return actual_damage
    
    def update(self, dt):
        """Update player state per frame (e.g. passive regen)"""
        if self.is_alive and self.hp < self.max_hp:
            self.hp += self.health_regen_rate * dt
            if self.hp > self.max_hp:
                self.hp = self.max_hp
    
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
        self.exp_to_level = int(self.exp_to_level * 1.1)
        print(f"{self.name} leveled up to {self.level}!")
    
    def add_item(self, item):
        """Add item to inventory"""
        self.inventory.append(item)
    
    def remove_item(self, item):
        """Remove item from inventory"""
        if item in self.inventory:
            self.inventory.remove(item)
    
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
            'hp': int(self.hp),
            'max_hp': int(self.max_hp),
            'attack': self.attack,
            'speed': self.speed,
            'health_regen': self.health_regen_rate,
            'gold': self.gold,
        }
