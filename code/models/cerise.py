from models.fruit import Fruit

class Cerise(Fruit):
    """Fruit de type Cerise"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
    
    @property
    def valeur(self):
        return 3
    
    @property
    def couleur(self):
        return "#dc143c"  # Rouge foncé
    
    @property
    def emoji(self):
        return "🍒"
    
    def get_type(self):
        return "Cerise"