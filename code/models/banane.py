from models.fruit import Fruit

class Banane(Fruit):
    """Fruit de type Banane"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
    
    @property
    def valeur(self):
        return 2
    
    @property
    def couleur(self):
        return "#ffd700"  # Jaune
    
    @property
    def emoji(self):
        return "🍌"
    
    def get_type(self):
        return "Banane"