from models.fruit import Fruit

class Pomme(Fruit):
    """Fruit de type Pomme"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
    
    @property
    def valeur(self):
        return 1
    
    @property
    def couleur(self):
        return "#ff0000"  # Rouge
    
    @property
    def emoji(self):
        return "🍎"
    
    def get_type(self):
        return "Pomme"