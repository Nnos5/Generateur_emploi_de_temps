import json
import pandas as pd
import os
from ortools.sat.python import cp_model
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

class TimetableVisualizer:
    def __init__(self, timetable_data):
        """Initialiser le visualiseur d'emploi du temps."""
        self.timetable_data = timetable_data
        self.days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
        self.periods = ['7h00-9h55', '10h05-12h55', '13h05-15h55', '16h05-18h55', '19h05-21h55']
        
        # Générer une palette de couleurs pour les différentes matières
        self.subject_colors = {}
        
    def generate_colors(self, assignments):
        """Générer des couleurs uniques pour chaque matière."""
        # Extraire toutes les matières uniques
        subjects = set()
        for assignment in assignments:
            subjects.add(assignment['subject_code'])
        
        # Créer une palette de couleurs
        color_map = plt.cm.get_cmap('tab20', len(subjects))
        colors = [mcolors.rgb2hex(color_map(i)[:3]) for i in range(len(subjects))]
        
        # Assigner des couleurs aux matières
        self.subject_colors = {subject: colors[i] for i, subject in enumerate(subjects)}
    
    def plot_timetable(self, class_name, output_dir=None):
        """Visualiser l'emploi du temps d'une classe sous forme de grille."""
        # Filtrer les affectations pour cette classe
        assignments = [a for a in self.timetable_data['assignments'] if a['class'] == class_name]
        
        # Générer des couleurs si ce n'est pas déjà fait
        if not self.subject_colors:
            self.generate_colors(self.timetable_data['assignments'])
        
        # Créer une figure
        fig, ax = plt.subplots(figsize=(15, 8))
        plt.title(f'Emploi du temps - {class_name}', fontsize=16)
        
        # Créer une grille pour l'emploi du temps
        grid = np.zeros((len(self.periods), len(self.days)))
        labels = np.empty((len(self.periods), len(self.days)), dtype=object)
        
        # Remplir la grille avec les affectations
        for assignment in assignments:
            period = assignment['period']
            day = assignment['day']
            grid[period, day] = 1
            labels[period, day] = (
                f"{assignment['subject_code']}\n"
                f"{assignment['room']}\n"
                f"{assignment['lecturer']}"
            )
        
        # Créer une matrice de couleurs
        colors = np.empty((len(self.periods), len(self.days)), dtype=object)
        for assignment in assignments:
            period = assignment['period']
            day = assignment['day']
            colors[period, day] = self.subject_colors.get(assignment['subject_code'], 'lightgray')
        
        # Masquer les cellules vides
        masked_colors = np.ma.masked_where(grid == 0, colors)
        
        # Tracer la grille
        for i in range(len(self.periods)):
            for j in range(len(self.days)):
                if grid[i, j] == 1:
                    rect = plt.Rectangle(
                        (j, i), 1, 1, 
                        facecolor=colors[i, j], 
                        alpha=0.8, 
                        edgecolor='black'
                    )
                    ax.add_patch(rect)
                    ax.text(
                        j + 0.5, i + 0.5, labels[i, j],
                        ha='center', va='center', fontsize=9
                    )
        
        # Configurer les axes
        ax.set_xticks(np.arange(len(self.days)) + 0.5)
        ax.set_yticks(np.arange(len(self.periods)) + 0.5)
        ax.set_xticklabels(self.days)
        ax.set_yticklabels(self.periods)
        
        # Ajouter une grille de fond
        ax.set_xticks(np.arange(len(self.days) + 1), minor=True)
        ax.set_yticks(np.arange(len(self.periods) + 1), minor=True)
        ax.grid(which='minor', color='black', linestyle='-', linewidth=1)
        
        # Ajuster les limites des axes
        ax.set_xlim(0, len(self.days))
        ax.set_ylim(0, len(self.periods))
        
        # Ajouter une légende pour les matières
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=color, alpha=0.8, edgecolor='black', label=subject)
            for subject, color in self.subject_colors.items()
            if subject in [a['subject_code'] for a in assignments]
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        # Ajuster la mise en page
        plt.tight_layout()
        
        # Sauvegarder l'image si un répertoire de sortie est spécifié
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            plt.savefig(f"{output_dir}/{class_name}_timetable.png", dpi=300, bbox_inches='tight')
        
        return fig
    
    def export_to_pdf(self, output_file):
        """Exporter tous les emplois du temps dans un fichier PDF."""
        # Extraire toutes les classes uniques
        classes = set(a['class'] for a in self.timetable_data['assignments'])
        
        # Générer des couleurs si ce n'est pas déjà fait
        if not self.subject_colors:
            self.generate_colors(self.timetable_data['assignments'])
        
        # Créer un fichier PDF
        with PdfPages(output_file) as pdf:
            for class_name in sorted(classes):
                fig = self.plot_timetable(class_name)
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
        
        print(f"Emplois du temps exportés dans {output_file}")

# Fonction principale pour utiliser le visualiseur
def visualize_timetable(solution_file, output_dir=None, pdf_file=None):
    """Visualiser les emplois du temps à partir d'un fichier de solution."""
    # Charger la solution
    with open(solution_file, 'r', encoding='utf-8') as file:
        solution = json.load(file)
    
    # Créer le visualiseur
    visualizer = TimetableVisualizer(solution)
    
    # Extraire toutes les classes uniques
    classes = set(a['class'] for a in solution['assignments'])
    
    # Visualiser l'emploi du temps pour chaque classe
    for class_name in sorted(classes):
        visualizer.plot_timetable(class_name, output_dir)
    
    # Exporter en PDF si demandé
    if pdf_file:
        visualizer.export_to_pdf(pdf_file)

if __name__ == "__main__":
    # Exemple d'utilisation
    visualize_timetable(
        'output/timetable_solution.json',
        output_dir='output/timetable_images',
        pdf_file='output/emplois_du_temps.pdf'
    )