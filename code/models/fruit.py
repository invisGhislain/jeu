from abc import ABC, abstractmethod

class Fruit(ABC):
    """Classe abstraite représentant un fruit"""
    
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self.id = None
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    @property
    @abstractmethod
    def valeur(self):
        """Valeur en points du fruit"""
        pass
    
    @property
    @abstractmethod
    def couleur(self):
        """Couleur du fruit"""
        pass
    
    @property
    @abstractmethod
    def emoji(self):
        """Emoji du fruit"""
        pass
    
    @abstractmethod
    def get_type(self):
        """Retourne le type du fruit"""
        pass
    
    def get_info(self):
        """Retourne les informations du fruit"""
        return {
            "x": self._x,
            "y": self._y,
            "type": self.get_type(),
            "valeur": self.valeur,
            "couleur": self.couleur,
            "emoji": self.emoji
        }