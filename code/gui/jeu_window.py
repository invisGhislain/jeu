import customtkinter as ctk
from tkinter import messagebox
import random
from datetime import datetime

from models.serpent import Serpent
from models.pomme import Pomme
from models.banane import Banane
from models.cerise import Cerise
from database.db_manager import DatabaseManager

# Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JeuWindow:
    """Fenêtre principale du jeu Snake - Version compacte"""
    
    # Constantes - Taille réduite
    TAILLE_GRILLE = 20
    TAILLE_CELLULE = 22  # Réduit de 25 à 22
    DELAI = 150
    
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("🐍 Jeu du Serpent")
        self.window.geometry("650x720")  # Fenêtre plus petite
        self.window.minsize(600, 650)
        self.window.resizable(False, False)
        
        self.db = DatabaseManager()
        
        self.serpent = None
        self.fruits = []
        self.en_jeu = False
        self.jeu_termine = False
        self.timer = None
        self.fruits_manges = 0
        self.id_partie = None
        
        self._creer_interface()
        self._verifier_partie_existante()
    
    def _creer_interface(self):
        """Crée l'interface graphique"""
        self.main_frame = ctk.CTkFrame(self.window, fg_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        self._creer_entete()
        
        # Canvas - Taille calculée automatiquement
        taille_totale = self.TAILLE_GRILLE * self.TAILLE_CELLULE
        self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a")
        self.canvas_frame.pack(pady=5)
        
        self.canvas = ctk.CTkCanvas(
            self.canvas_frame,
            width=taille_totale,
            height=taille_totale,
            bg="#1a1a1a",
            highlightthickness=1,
            highlightbackground="#333333"
        )
        self.canvas.pack()
        
        self._creer_controles()
        self._creer_barre_etat()
        
        # Liaison des touches
        self.window.bind("<Up>", lambda e: self._changer_direction("HAUT"))
        self.window.bind("<Down>", lambda e: self._changer_direction("BAS"))
        self.window.bind("<Left>", lambda e: self._changer_direction("GAUCHE"))
        self.window.bind("<Right>", lambda e: self._changer_direction("DROITE"))
        self.window.bind("<z>", lambda e: self._changer_direction("HAUT"))
        self.window.bind("<s>", lambda e: self._changer_direction("BAS"))
        self.window.bind("<q>", lambda e: self._changer_direction("GAUCHE"))
        self.window.bind("<d>", lambda e: self._changer_direction("DROITE"))
        self.window.bind("<space>", lambda e: self._basculer_pause())
        self.window.focus_set()
    
    def _creer_entete(self):
        """En-tête compact"""
        header = ctk.CTkFrame(self.main_frame, height=45, fg_color="#2b2b2b")
        header.pack(fill="x", pady=(0, 5))
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="🐍 Serpent", font=("Helvetica", 18, "bold"))
        title.pack(side="left", padx=12)
        
        stats_frame = ctk.CTkFrame(header, fg_color="transparent")
        stats_frame.pack(side="right", padx=12)
        
        self.score_label = ctk.CTkLabel(stats_frame, text="🏆 0", font=("Helvetica", 13, "bold"))
        self.score_label.pack(side="left", padx=8)
        
        self.longueur_label = ctk.CTkLabel(stats_frame, text="📏 1", font=("Helvetica", 13, "bold"))
        self.longueur_label.pack(side="left", padx=8)
        
        self.status_label = ctk.CTkLabel(stats_frame, text="⏸️", font=("Helvetica", 14, "bold"), text_color="#ffaa00")
        self.status_label.pack(side="left", padx=8)
    
    def _creer_controles(self):
        """Contrôles compacts"""
        controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        controls_frame.pack(pady=6)
        
        # Première ligne
        row1 = ctk.CTkFrame(controls_frame, fg_color="transparent")
        row1.pack(pady=2)
        
        ctk.CTkButton(row1, text="🔄 Nouveau", command=self._nouvelle_partie, 
                     width=90, height=28, font=("Helvetica", 10, "bold"), fg_color="#008000").pack(side="left", padx=3)
        
        self.btn_pause = ctk.CTkButton(row1, text="⏸️ Pause", command=self._basculer_pause, 
                                       width=90, height=28, font=("Helvetica", 10, "bold"), fg_color="#cc8800")
        self.btn_pause.pack(side="left", padx=3)
        
        self.btn_sauvegarder = ctk.CTkButton(row1, text="💾 Sauver", command=self._sauvegarder_partie, 
                                             width=90, height=28, font=("Helvetica", 10, "bold"), fg_color="#1f538d")
        self.btn_sauvegarder.pack(side="left", padx=3)
        
        ctk.CTkButton(row1, text="📂 Reprendre", command=self._reprendre_partie, 
                     width=90, height=28, font=("Helvetica", 10, "bold"), fg_color="#cc8800").pack(side="left", padx=3)
        
        ctk.CTkButton(row1, text="⏹️ Quitter", command=self._quitter, 
                     width=90, height=28, font=("Helvetica", 10, "bold"), fg_color="#8B0000").pack(side="left", padx=3)
        
        # Légende compacte
        row2 = ctk.CTkFrame(controls_frame, fg_color="transparent")
        row2.pack(pady=2)
        
        ctk.CTkLabel(row2, text="🍎1  🍌2  🍒3  |  ⬆️⬇️⬅️➡️ ZQSD  |  Espace Pause", 
                    font=("Helvetica", 10), text_color="gray").pack()
    
    def _creer_barre_etat(self):
        """Barre d'état compacte"""
        status_frame = ctk.CTkFrame(self.main_frame, height=25, fg_color="#2b2b2b")
        status_frame.pack(fill="x", pady=(5, 0))
        status_frame.pack_propagate(False)
        
        self.message_label = ctk.CTkLabel(status_frame, text="✅ Prêt", font=("Helvetica", 10))
        self.message_label.pack(side="left", padx=12)
        
        self.partie_id_label = ctk.CTkLabel(status_frame, text="", font=("Helvetica", 9), text_color="gray")
        self.partie_id_label.pack(side="right", padx=12)
    
    def _changer_direction(self, direction):
        if self.serpent and not self.jeu_termine:
            self.serpent.changer_direction(direction)
    
    def _verifier_partie_existante(self):
        derniere = self.db.get_derniere_partie()
        if derniere:
            if messagebox.askyesno(
                "Partie sauvegardée",
                f"Reprendre la partie ?\n"
                f"🏆 Score: {derniere['score']}\n"
                f"📏 Longueur: {derniere['longueur']}"
            ):
                self._charger_partie(derniere)
                return
        
        self._nouvelle_partie()
    
    def _charger_partie(self, partie_data):
        try:
            self.id_partie = partie_data['id']
            self.fruits_manges = partie_data['fruits_manges']
            
            self.serpent = Serpent()
            self.serpent._corps = partie_data['corps'].copy()
            self.serpent._direction = partie_data['direction']
            self.serpent._prochaine_direction = partie_data['direction']
            self.serpent._score = partie_data['score']
            self.serpent._est_vivant = True
            
            self.fruits = []
            for f_data in partie_data['fruits']:
                if f_data['type'] == 'pomme':
                    fruit = Pomme(f_data['x'], f_data['y'])
                elif f_data['type'] == 'banane':
                    fruit = Banane(f_data['x'], f_data['y'])
                elif f_data['type'] == 'cerise':
                    fruit = Cerise(f_data['x'], f_data['y'])
                self.fruits.append(fruit)
            
            self.en_jeu = True
            self.jeu_termine = False
            
            self.status_label.configure(text="▶️", text_color="#00ff00")
            self.btn_pause.configure(text="⏸️ Pause")
            self.message_label.configure(text=f"✅ Partie reprise")
            self.partie_id_label.configure(text=f"#{self.id_partie}")
            
            self._mettre_a_jour_affichage()
            self._mettre_a_jour_statistiques()
            
            self._boucle_jeu()
            
        except Exception as e:
            print(f"Erreur: {e}")
            messagebox.showerror("Erreur", "Impossible de charger la partie")
            self._nouvelle_partie()
    
    def _nouvelle_partie(self):
        if self.timer:
            self.window.after_cancel(self.timer)
            self.timer = None
        
        self.serpent = Serpent(5, 5)
        self.fruits = []
        self.en_jeu = True
        self.jeu_termine = False
        self.fruits_manges = 0
        self.id_partie = None
        
        for _ in range(3):
            self._ajouter_fruit()
        
        self._mettre_a_jour_affichage()
        self._mettre_a_jour_statistiques()
        self.status_label.configure(text="▶️", text_color="#00ff00")
        self.btn_pause.configure(text="⏸️ Pause")
        self.message_label.configure(text="✅ Nouvelle partie")
        self.partie_id_label.configure(text="")
        
        self._sauvegarder_partie()
        self._boucle_jeu()
    
    def _basculer_pause(self):
        if self.jeu_termine or self.serpent is None:
            return
        
        self.en_jeu = not self.en_jeu
        
        if self.en_jeu:
            self.status_label.configure(text="▶️", text_color="#00ff00")
            self.btn_pause.configure(text="⏸️ Pause")
            self.message_label.configure(text="✅ Reprise")
            self._boucle_jeu()
        else:
            self.status_label.configure(text="⏸️", text_color="#ffaa00")
            self.btn_pause.configure(text="▶️ Reprendre")
            self.message_label.configure(text="⏸️ Pause")
            if self.timer:
                self.window.after_cancel(self.timer)
                self.timer = None
    
    def _sauvegarder_partie(self):
        if self.serpent is None or self.jeu_termine:
            return
        
        partie_data = {
            'date_modification': datetime.now().isoformat(),
            'score': self.serpent.score,
            'longueur': self.serpent.longueur,
            'est_terminee': self.jeu_termine,
            'corps': self.serpent.corps,
            'direction': self.serpent._direction,
            'fruits_manges': self.fruits_manges,
            'fruits': [
                {'type': f.get_type().lower(), 'x': f.x, 'y': f.y} 
                for f in self.fruits
            ]
        }
        
        try:
            if self.id_partie:
                partie_data['id'] = self.id_partie
                self.db.sauvegarder_partie(partie_data)
            else:
                partie_data['date_creation'] = datetime.now().isoformat()
                self.id_partie = self.db.sauvegarder_partie(partie_data)
                self.partie_id_label.configure(text=f"#{self.id_partie}")
                self.message_label.configure(text="✅ Sauvegardé")
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
    
    def _reprendre_partie(self):
        if self.timer:
            self.window.after_cancel(self.timer)
            self.timer = None
        
        parties = self.db.get_toutes_parties()
        parties_non_terminees = [p for p in parties if not p['est_terminee']]
        
        if not parties_non_terminees:
            messagebox.showinfo("Info", "Aucune partie sauvegardée")
            return
        
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("📂 Reprendre")
        dialog.geometry("400x350")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Sélectionnez une partie:", font=("Helvetica", 14, "bold")).pack(pady=8)
        
        list_frame = ctk.CTkScrollableFrame(dialog, height=200)
        list_frame.pack(fill="both", expand=True, padx=15, pady=8)
        
        for partie in parties_non_terminees:
            btn = ctk.CTkButton(
                list_frame,
                text=f"🏆 {partie['score']}  |  📏 {partie['longueur']}  |  {partie['date_modification'][:16]}",
                command=lambda p=partie: self._selectionner_partie(p, dialog),
                width=350,
                height=30,
                anchor="w",
                font=("Helvetica", 11),
                fg_color="#1f538d"
            )
            btn.pack(pady=2, fill="x")
        
        ctk.CTkButton(dialog, text="❌ Annuler", command=dialog.destroy, width=120).pack(pady=8)
    
    def _selectionner_partie(self, partie_data, dialog):
        dialog.destroy()
        if messagebox.askyesno("Confirmation", f"Reprendre ?\nScore: {partie_data['score']}"):
            self._charger_partie(partie_data)
    
    def _boucle_jeu(self):
        if self.jeu_termine:
            return
        
        if not self.en_jeu:
            self.timer = self.window.after(100, self._boucle_jeu)
            return
        
        if self.serpent is None:
            return
        
        self.serpent.avancer()
        
        if self.serpent.verifier_collision(self.TAILLE_GRILLE, self.TAILLE_GRILLE):
            self._fin_jeu()
            return
        
        tete = self.serpent.tete
        fruits_a_manger = []
        for i, fruit in enumerate(self.fruits):
            if fruit.x == tete[0] and fruit.y == tete[1]:
                fruits_a_manger.append(i)
        
        for i in reversed(fruits_a_manger):
            fruit = self.fruits.pop(i)
            self.serpent.manger(fruit)
            self.fruits_manges += 1
            self._ajouter_fruit()
        
        if self.fruits_manges % 10 == 0:
            self._sauvegarder_partie()
        
        self._mettre_a_jour_affichage()
        self._mettre_a_jour_statistiques()
        
        self.timer = self.window.after(self.DELAI, self._boucle_jeu)
    
    def _fin_jeu(self):
        self.jeu_termine = True
        self.en_jeu = False
        self.status_label.configure(text="💀", text_color="#ff0000")
        self.btn_pause.configure(text="⏹️ Terminé")
        
        if self.timer:
            self.window.after_cancel(self.timer)
            self.timer = None
        
        if self.id_partie:
            partie_data = {
                'id': self.id_partie,
                'date_modification': datetime.now().isoformat(),
                'score': self.serpent.score,
                'longueur': self.serpent.longueur,
                'est_terminee': True,
                'corps': self.serpent.corps,
                'direction': self.serpent._direction,
                'fruits_manges': self.fruits_manges,
                'fruits': [
                    {'type': f.get_type().lower(), 'x': f.x, 'y': f.y} 
                    for f in self.fruits
                ]
            }
            self.db.sauvegarder_partie(partie_data)
        
        self._mettre_a_jour_affichage()
        self.message_label.configure(text=f"💀 Game Over ! Score: {self.serpent.score}")
        
        meilleurs = self.db.get_meilleurs_scores(5)
        
        msg = f"💀 Partie terminée !\n\n"
        msg += f"🏆 Score: {self.serpent.score}\n"
        msg += f"📏 Longueur: {self.serpent.longueur}\n"
        msg += f"🍎 Fruits: {self.fruits_manges}\n\n"
        
        if meilleurs:
            msg += "🏅 Meilleurs scores:\n"
            for i, p in enumerate(meilleurs[:3], 1):
                msg += f"  {i}. {p['score']} pts\n"
        
        messagebox.showinfo("Game Over", msg)
    
    def _ajouter_fruit(self):
        if len(self.fruits) >= 5:
            return
        
        types_fruits = [
            (Pomme, 0.5),
            (Banane, 0.3),
            (Cerise, 0.2)
        ]
        
        r = random.random()
        cumul = 0
        type_fruit = Pomme
        for cls, prob in types_fruits:
            cumul += prob
            if r <= cumul:
                type_fruit = cls
                break
        
        for _ in range(100):
            x = random.randint(0, self.TAILLE_GRILLE - 1)
            y = random.randint(0, self.TAILLE_GRILLE - 1)
            
            if (x, y) not in self.serpent.corps and not any(f.x == x and f.y == y for f in self.fruits):
                fruit = type_fruit(x, y)
                self.fruits.append(fruit)
                return
    
    def _mettre_a_jour_affichage(self):
        self.canvas.delete("all")
        taille = self.TAILLE_CELLULE
        
        # Grille
        for i in range(self.TAILLE_GRILLE + 1):
            self.canvas.create_line(i * taille, 0, i * taille, self.TAILLE_GRILLE * taille, fill="#2a2a2a", width=1)
            self.canvas.create_line(0, i * taille, self.TAILLE_GRILLE * taille, i * taille, fill="#2a2a2a", width=1)
        
        # Fruits
        for fruit in self.fruits:
            x = fruit.x * taille + taille // 2
            y = fruit.y * taille + taille // 2
            rayon = taille // 2 - 3
            self.canvas.create_oval(x - rayon, y - rayon, x + rayon, y + rayon, fill=fruit.couleur, outline="")
            self.canvas.create_text(x, y, text=fruit.emoji, font=("Arial", 12))
        
        # Serpent
        if self.serpent:
            corps = self.serpent.corps
            for i, (x, y) in enumerate(corps):
                x1 = x * taille
                y1 = y * taille
                x2 = x1 + taille - 1
                y2 = y1 + taille - 1
                
                if i == 0:
                    couleur = "#44ff44"
                    couleur_contour = "#00cc00"
                else:
                    intensite = 100 - (i / max(1, len(corps)) * 40)
                    couleur = f"#{int(50 + intensite):02x}{int(180 + intensite // 2):02x}{int(50 + intensite // 4):02x}"
                    couleur_contour = "#006600"
                
                self.canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=couleur, outline=couleur_contour, width=1)
            
            # Yeux
            if corps:
                x, y = corps[0]
                x_centre = x * taille + taille // 2
                y_centre = y * taille + taille // 2
                
                direction = self.serpent._direction
                if direction == "HAUT":
                    offsets = [(-3, -3), (3, -3)]
                elif direction == "BAS":
                    offsets = [(-3, 3), (3, 3)]
                elif direction == "GAUCHE":
                    offsets = [(-3, -3), (-3, 3)]
                else:
                    offsets = [(3, -3), (3, 3)]
                
                for dx, dy in offsets:
                    self.canvas.create_oval(x_centre + dx - 2, y_centre + dy - 2, 
                                           x_centre + dx + 2, y_centre + dy + 2, 
                                           fill="white", outline="black", width=1)
                    self.canvas.create_oval(x_centre + dx, y_centre + dy - 1, 
                                           x_centre + dx + 1, y_centre + dy + 1, 
                                           fill="black")
    
    def _mettre_a_jour_statistiques(self):
        if self.serpent:
            self.score_label.configure(text=f"🏆 {self.serpent.score}")
            self.longueur_label.configure(text=f"📏 {self.serpent.longueur}")
    
    def _quitter(self):
        if self.en_jeu and not self.jeu_termine:
            if messagebox.askyesno("Quitter", "Sauvegarder avant de quitter ?"):
                self._sauvegarder_partie()
        
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter ?"):
            if self.timer:
                self.window.after_cancel(self.timer)
            self.window.destroy()
    
    def run(self):
        self.window.mainloop()