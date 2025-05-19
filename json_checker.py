import json

def check_json_files():
    """Vérifie et affiche les informations des fichiers JSON pour le débogage."""
    
    try:
        with open('rooms.json', 'r', encoding='utf-8') as file:
            rooms_data = json.load(file)
        
        print("\n=== Vérification du fichier rooms.json ===")
        if "Informatique" in rooms_data:
            informatique_rooms = rooms_data["Informatique"]
            print(f"Nombre de salles d'informatique: {len(informatique_rooms)}")
            
            print("Exemples de salles:")
            for i, room in enumerate(informatique_rooms[:3]):
                print(f"  {i+1}. Numéro: {room.get('num', 'N/A')}, Capacité: {room.get('capacite', 'N/A')}, Bâtiment: {room.get('batiment', 'N/A')}")
        else:
            print("ERREUR: Clé 'Informatique' manquante dans rooms.json")
    except Exception as e:
        print(f"ERREUR lors de la vérification de rooms.json: {str(e)}")
    
    try:
        with open('subjects.json', 'r', encoding='utf-8') as file:
            subjects_data = json.load(file)
        
        print("\n=== Vérification du fichier subjects.json ===")
        if "niveau" in subjects_data:
            niveaux = subjects_data["niveau"]
            print(f"Nombre de niveaux: {len(niveaux)}")
            
            total_subjects = 0
            for level, level_data in niveaux.items():
                for semester, semester_data in level_data.items():
                    if "subjects" in semester_data:
                        total_subjects += len(semester_data["subjects"])
            
            print(f"Nombre total de matières: {total_subjects}")
            
            print("Exemples de matières par niveau:")
            for level, level_data in niveaux.items():
                for semester, semester_data in level_data.items():
                    if "subjects" in semester_data and semester_data["subjects"]:
                        subject = semester_data["subjects"][0]
                        subject_name = subject.get("name", "N/A")
                        if isinstance(subject_name, list):
                            subject_name = ", ".join(filter(None, subject_name))
                        print(f"  Niveau {level}, Semestre {semester}: {subject.get('code', 'N/A')} - {subject_name}")
        else:
            print("ERREUR: Clé 'niveau' manquante dans subjects.json")
    except Exception as e:
        print(f"ERREUR lors de la vérification de subjects.json: {str(e)}")
    
    print("\n=== Analyse des contraintes potentielles ===")
    
    classes = []
    subjects_per_class = {}
    all_lecturers = set()
    
    try:
        if "niveau" in subjects_data:
            for level, level_data in niveaux.items():
                for semester, semester_data in level_data.items():
                    class_name = f"INFO{level}{semester}"
                    classes.append(class_name)
                    
                    if "subjects" in semester_data:
                        subjects_per_class[class_name] = len(semester_data["subjects"])
                        
                        for subject in semester_data["subjects"]:
                            if "Course Lecturer" in subject:
                                lecturer = subject["Course Lecturer"]
                                if isinstance(lecturer, list) and lecturer:
                                    all_lecturers.add(lecturer[0])
                                elif isinstance(lecturer, str):
                                    all_lecturers.add(lecturer)
        
        total_rooms = len(informatique_rooms) if "Informatique" in rooms_data else 0
        total_periods = 5 * 6  # 5 périodes par jour, 6 jours
        
        print(f"Nombre de classes: {len(classes)}")
        print(f"Nombre de salles disponibles: {total_rooms}")
        print(f"Nombre total de créneaux horaires: {total_periods}")
        print(f"Nombre d'enseignants uniques: {len(all_lecturers)}")
        
        max_subjects = max(subjects_per_class.values()) if subjects_per_class else 0
        print(f"Nombre maximum de matières par classe: {max_subjects}")
        
        if max_subjects > total_periods:
            print("\nALERTE: Certaines classes ont plus de matières que de créneaux horaires disponibles!")
            print("C'est une contrainte insoluble qui empêchera de trouver une solution valide.")
        
        if len(classes) * max_subjects > total_rooms * total_periods:
            print("\nALERTE: Le nombre total de cours à programmer pourrait dépasser la capacité disponible.")
            print("Cela pourrait rendre difficile ou impossible de trouver une solution.")
    
    except Exception as e:
        print(f"ERREUR lors de l'analyse des contraintes: {str(e)}")

if __name__ == "__main__":
    check_json_files()