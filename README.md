# Chauffage collectif

Simulation 2D de diffusion de chaleur en Python avec affichage en temps réel via Pygame.

## Fonctionnalités

- Grille 2D de température (valeurs 0 à 255)
- Mise à jour par moyenne des 4 voisins (haut, bas, gauche, droite)
- Affichage temps réel (niveaux de gris ou carte thermique)
- Pause, reprise et itération pas-à-pas
- Sauvegarde optionnelle des données dans un fichier JSON
- Paramétrage complet via arguments CLI

## Prérequis

- Windows (le projet inclut des optimisations/fonctions spécifiques Windows)
- Python 3.10+
- `pip`

## Installation

Depuis la racine du projet :

```bat
install.bat
```

Ce script :
- crée un environnement virtuel `venv`
- installe les dépendances
- copie un script de lancement par défaut

## Lancement

### Méthode simple

```bat
launch.bat
```

### Méthode manuelle

```bat
venv\Scripts\activate.bat
python main.py --height 30 --width 40
```

## Mise à jour

```bat
update.bat
```

## Contrôles clavier

- `Alt` : pause / reprise
- `Espace` : une itération (quand en pause)
- `Échap` : quitter

## Arguments principaux

Quelques options utiles de `main.py` :

- `--height` / `--width` : dimensions de la grille
- `--iterations_per_cycle` : nombre d’itérations par cycle
- `--max_iteration` : nombre de cycles
- `--do_limit_fps` / `--fps` : limitation de vitesse de simulation
- `--do_save_data` / `--data_save_name` : export JSON
- `--do_gray_colors` : affichage gris (`True`) ou thermique (`False`)
- `--do_display_temp` : affiche la température du pixel sous la souris (en pause)

## Données de sortie

Si la sauvegarde est activée (`--do_save_data True`), le fichier JSON contient :

- les paramètres globaux (`general_info`)
- les données par cycle (`iteration_1`, `iteration_2`, ...)
- les statistiques de performance (temps, itérations/s)

## Dépendances

Voir `requirements.txt` :

- `numpy`
- `pygame`
- `pygame-ce`
- `pywin32`
- `windows-curses`

## Remarques

- Le script `launch.bat` contient un exemple de paramètres que vous pouvez adapter.
- Pour de grandes grilles ou beaucoup d’itérations, désactivez la sauvegarde JSON (`--do_save_data False`) pour de meilleures performances.
