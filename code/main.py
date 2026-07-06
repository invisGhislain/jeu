"""
🐍 Jeu du Serpent
Application avec interface graphique et sauvegarde
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.jeu_window import JeuWindow

def main():
    print("=" * 50)
    print("🐍 Jeu du Serpent")
    print("=" * 50)
    print("🎮 Lancement du jeu...")
    print("📖 Flèches ou ZQSD pour diriger")
    print("📖 Espace pour Pause/Reprise")
    print("💾 Sauvegarde automatique")
    
    app = JeuWindow()
    app.run()

if __name__ == "__main__":
    main()