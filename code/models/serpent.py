class Serpent:
    """Classe représentant le serpent"""
    
    def __init__(self, x=5, y=5):
        self._corps = [(x, y)]
        self._direction = "DROITE"
        self._prochaine_direction = "DROITE"
        self._grandir = False
        self._score = 0
        self._est_vivant = True
        self.id = None
    
    @property
    def corps(self):
        return self._corps.copy()
    
    @property
    def tete(self):
        return self._corps[0] if self._corps else None
    
    @property
    def score(self):
        return self._score
    
    @property
    def est_vivant(self):
        return self._est_vivant
    
    @property
    def longueur(self):
        return len(self._corps)
    
    def changer_direction(self, direction):
        """Change la direction du serpent"""
        # Empêcher de faire demi-tour
        if (self._direction == "HAUT" and direction == "BAS") or \
           (self._direction == "BAS" and direction == "HAUT") or \
           (self._direction == "GAUCHE" and direction == "DROITE") or \
           (self._direction == "DROITE" and direction == "GAUCHE"):
            return
        self._prochaine_direction = direction
    
    def avancer(self):
        """Fait avancer le serpent d'une case"""
        if not self._est_vivant:
            return
        
        self._direction = self._prochaine_direction
        
        # Calculer la nouvelle tête
        x, y = self._corps[0]
        if self._direction == "HAUT":
            nouvelle_tete = (x, y - 1)
        elif self._direction == "BAS":
            nouvelle_tete = (x, y + 1)
        elif self._direction == "GAUCHE":
            nouvelle_tete = (x - 1, y)
        else:  # DROITE
            nouvelle_tete = (x + 1, y)
        
        # Ajouter la nouvelle tête
        self._corps.insert(0, nouvelle_tete)
        
        # Si le serpent ne doit pas grandir, retirer la queue
        if not self._grandir:
            self._corps.pop()
        else:
            self._grandir = False
    
    def manger(self, fruit):
        """Le serpent mange un fruit"""
        self._score += fruit.valeur
        self._grandir = True
        return self._score
    
    def verifier_collision(self, largeur, hauteur):
        """Vérifie les collisions avec les murs ou le corps"""
        if not self._est_vivant:
            return True
        
        x, y = self._corps[0]
        
        # Collision avec les murs
        if x < 0 or x >= largeur or y < 0 or y >= hauteur:
            self._est_vivant = False
            return True
        
        # Collision avec le corps (sauf la tête)
        if self._corps[0] in self._corps[1:]:
            self._est_vivant = False
            return True
        
        return False
    
    def get_info(self):
        """Retourne les informations du serpent"""
        return {
            "longueur": self.longueur,
            "score": self._score,
            "vivant": self._est_vivant,
            "position_tete": self.tete
        }
    
    def __str__(self):
        return f"🐍 Score: {self._score} | Longueur: {self.longueur}"