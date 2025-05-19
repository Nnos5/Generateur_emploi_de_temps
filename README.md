# 📈 Générateur d'Emploi du Temps Universitaire

<div align="center">
  
![Université de Yaoundé I](https://www.dynafac.org/images/members/image/Univ-de-Yaounde-I-ENS-partner-dynafac.jpg)

**Projet 1 - INF 4178 : Génie Logiciel I**

**NDEUNA NGANA OUSMAN SINCLAIR - 21T2433**

*Département d'Informatique - Université de Yaoundé I*

</div>

## 📝 Sommaire
- [Introduction](#introduction)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Structure du Projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Modèle Mathématique](#modèle-mathématique)
- [Personnalisation](#personnalisation)
- [Résultats](#résultats)
- [Dépannage](#dépannage)

## 📚 Introduction

Ce projet implémente un système automatique de génération d'emplois du temps pour le département d'Informatique de l'Université de Yaoundé I. Développé dans le cadre du cours INF 4178 (Génie Logiciel I), ce système utilise la programmation par contraintes avec Google OR-Tools pour résoudre ce problème d'optimisation complexe.

## ✨ Fonctionnalités

- ✅ Génération automatique d'emplois du temps respectant toutes les contraintes spécifiées
- ✅ Prévention des conflits de classes, d'enseignants et de salles
- ✅ Optimisation des horaires pour favoriser les cours du matin
- ✅ Exportation des résultats en multiples formats (Excel, PDF, images)
- ✅ Visualisations graphiques claires et colorées des emplois du temps

## 🔧 Prérequis

Pour exécuter ce projet, vous aurez besoin des éléments suivants:

- **Python 3.7+**
- **Bibliothèques Python**:
  ```
  ortools     # Solveur d'optimisation
  pandas      # Manipulation de données
  numpy       # Calculs numériques
  matplotlib  # Visualisations
  openpyxl    # Export Excel
  ```
- **Fichiers de données**:
  - `rooms.json` - Informations sur les salles disponibles
  - `subjects.json` - Informations sur les cours et curriculum

## 📂 Structure du Projet

```
timetable-generator/
│
├── generateur.py   # Implémentation du modèle et résolution
├── visualiseur.py  # Visualisation des emplois du temps
├── main.py                  # Script principal
├── json_checker.py          # Outil de vérification des données
│
├── rooms.json               # Données des salles
├── subjects.json            # Données des cours
│
└── output/                  # Dossier de résultats (Créé après lancement du programme)
    ├── emplois_du_temps.xlsx  # Fichier Excel
    ├── timetable_solution.json  # Solution JSON
    ├── emplois_du_temps.pdf  # Document PDF
    └── images/              # Visualisations graphiques
```

## 📥 Installation

1. **Clonez ou téléchargez** ce projet dans un répertoire local:
   ```bash
   git clone https://github.com/Noubissie237/timetable-generator.git
   cd timetable-generator
   ```

2. **Installez les dépendances** requises:
   ```bash
   pip install ortools pandas numpy matplotlib openpyxl
   ```

3. **Vérifiez** que les fichiers `rooms.json` et `subjects.json` sont présents dans le répertoire du projet.

## 🚀 Utilisation

### Exécution du Programme Complet

1. Ouvrez un terminal dans le répertoire du projet
2. Exécutez le script principal:
   ```bash
   python3 main.py
   ```
3. Le programme va:
   - Charger les données des salles et des cours
   - Construire et résoudre le modèle d'optimisation
   - Générer les emplois du temps
   - Sauvegarder les résultats (Excel, JSON, PDF, images)

Tous les résultats seront sauvegardés dans le répertoire `output/`.

### Vérification des Données

Pour vérifier la validité des fichiers JSON avant la génération:
```bash
python3 json_checker.py
```

## 📐 Modèle Mathématique

Le modèle mathématique implémenté est basé sur la programmation par contraintes:

### 1. Variables de Décision
Variables binaires `x_{c,s,r,p,d}` indiquant si la classe `c` suit le cours `s` dans la salle `r` à la période `p` le jour `d`.

### 2. Contraintes Principales
- **Non-conflit pour les classes**: Une classe ne peut pas être dans deux endroits à la fois
- **Programmation unique**: Chaque cours est programmé exactement une fois par semaine
- **Non-conflit pour les enseignants**: Un enseignant ne peut pas donner deux cours en même temps
- **Non-conflit pour les salles**: Une salle ne peut pas accueillir deux cours en même temps
- **Respect du curriculum**: Une classe suit uniquement les cours de son programme

### 3. Fonction Objectif
Maximiser la somme pondérée des cours, avec des poids plus élevés pour les périodes du matin.

## ⚙️ Personnalisation

### Modification des Poids des Périodes

Pour favoriser certaines plages horaires, modifiez la liste `self.period_weights` dans le constructeur de `TimetableGenerator`:

```python
# Les périodes du matin ont un poids plus élevé
self.period_weights = [5, 4, 3, 2, 1]
```

### Ajout de Contraintes Supplémentaires

Pour ajouter des contraintes personnalisées, modifiez la méthode `build_model()` de la classe `TimetableGenerator`.

## 📊 Résultats

Après l'exécution, vous trouverez dans le répertoire `output/`:

- **emplois_du_temps.xlsx**: Fichier Excel avec une feuille par classe
- **timetable_solution.json**: Solution complète au format JSON
- **images/**: Visualisations graphiques des emplois du temps
- **emplois_du_temps.pdf**: Document PDF regroupant tous les emplois du temps



## 🔍 Dépannage

### Aucune Solution Trouvée

Si le programme ne trouve pas de solution:
- Vérifiez les fichiers JSON avec `json_checker.py`
- Assouplissez temporairement certaines contraintes
- Vérifiez que le nombre de salles et de créneaux est suffisant pour tous les cours

### Problèmes de Performance

Pour les problèmes de grande taille:
- Ajoutez un paramètre `time_limit` au solveur:
  ```python
  solver.parameters.max_time_in_seconds = 300  # 5 minutes
  ```
- Utilisez plusieurs threads:
  ```python
  solver.parameters.num_search_workers = 8
  ```
- Acceptez des solutions sous-optimales mais valides



