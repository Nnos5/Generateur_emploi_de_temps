import os
import json
from timetable_generator import TimetableGenerator
from timetable_visualizer import TimetableVisualizer

def main():
    """Programme principal pour générer et visualiser les emplois du temps."""
    print("=== Générateur d'Emploi du Temps - Université de Yaoundé I ===")
    print("Chargement des données...")
    
    if not os.path.exists('rooms.json') or not os.path.exists('subjects.json'):
        print("Erreur: Les fichiers de données 'rooms.json' et 'subjects.json' doivent être dans le répertoire courant.")
        return
    
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    generator = TimetableGenerator('rooms.json', 'subjects.json')
    
    print("Construction du modèle mathématique...")
    
    print("Résolution du problème d'optimisation...")
    if generator.solve():
        print(f"Solution trouvée avec valeur objectif: {generator.solution['objective_value']}")
        
        print("Génération des emplois du temps...")
        timetables = generator.generate_timetable()
        
        print("Sauvegarde des emplois du temps au format Excel...")
        generator.save_timetables(output_dir)
        
        solution_file = f"{output_dir}/timetable_solution.json"
        with open(solution_file, 'w', encoding='utf-8') as file:
            json.dump(generator.solution, file, ensure_ascii=False, indent=2)
        
        print("Génération des visualisations...")
        visualizer = TimetableVisualizer(generator.solution)
        
        classes = set(a['class'] for a in generator.solution['assignments'])
        
        images_dir = f"{output_dir}/images"
        os.makedirs(images_dir, exist_ok=True)
        
        for class_name in sorted(classes):
            visualizer.plot_timetable(class_name, images_dir)
        
        pdf_file = f"{output_dir}/emplois_du_temps.pdf"
        visualizer.export_to_pdf(pdf_file)
        
        print(f"\nProcessus terminé avec succès!")
        print(f"Les résultats ont été sauvegardés dans le répertoire '{output_dir}':")
        print(f"- Excel: {output_dir}/emplois_du_temps.xlsx")
        print(f"- Images: {output_dir}/images/")
        print(f"- PDF: {pdf_file}")
    else:
        print("Échec: Impossible de trouver une solution valide pour l'emploi du temps.")
        
        print("\nSuggestions pour résoudre le problème:")
        print("1. Vérifiez que les fichiers JSON sont correctement formatés")
        print("2. Assurez-vous qu'il y a suffisamment de salles pour tous les cours")
        print("3. Vérifiez qu'il n'y a pas de conflits insolubles dans les contraintes")
        print("4. Essayez d'assouplir temporairement certaines contraintes")

if __name__ == "__main__":
    main()