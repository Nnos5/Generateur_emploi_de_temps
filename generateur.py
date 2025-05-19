import json
from ortools.sat.python import cp_model
import pandas as pd
import os
from collections import defaultdict

class TimetableGenerator:
    def __init__(self, rooms_file, subjects_file):
        """Initialiser le générateur d'emploi du temps avec les fichiers de données."""
        self.days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
        self.periods = ['7h00-9h55', '10h05-12h55', '13h05-15h55', '16h05-18h55', '19h05-21h55']
        # Poids des périodes (favorisant celles du matin)
        self.period_weights = [5, 4, 3, 2, 1]  # p1 a plus de poids, p5 a moins de poids
        
        self.rooms = self._load_rooms(rooms_file)
        self.subjects, self.classes = self._load_subjects(subjects_file)
        
        self.solution = None
        self.timetable = None
        
        print(f"Nombre de salles chargées: {len(self.rooms)}")
        print(f"Nombre de matières chargées: {len(self.subjects)}")
        print(f"Classes trouvées: {', '.join(self.classes)}")
    
    def _load_rooms(self, filename):
        """Charger les données des salles depuis le fichier JSON."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            info_rooms = []
            for department, rooms in data.items():
                if department == "Informatique":
                    for room in rooms:
                        info_rooms.append({
                            'num': room['num'],
                            'capacity': int(room['capacite']),
                            'building': room['batiment'],
                            'department': room['filier']
                        })
            
            return info_rooms
        except Exception as e:
            print(f"Erreur lors du chargement des salles: {str(e)}")
            return []
    
    def _load_subjects(self, filename):
        """Charger les données des cours et des classes depuis le fichier JSON."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            subjects = []
            classes = set()
            
            for level, level_data in data['niveau'].items():
                for semester, semester_data in level_data.items():
                    class_name = f"INFO{level}{semester}"
                    classes.add(class_name)
                    
                    for subject in semester_data.get('subjects', []):
                        subject_name = subject.get('name', '')
                        if isinstance(subject_name, list):
                            subject_name = next((name for name in subject_name if name), "")
                        
                        if subject_name:  # Ignorer les cours sans nom
                            course_lecturer = subject.get('Course Lecturer', ["", ""])
                            assistant_lecturer = subject.get('Assitant lecturer', ["", ""])
                            
                            if not isinstance(course_lecturer, list):
                                course_lecturer = [course_lecturer, ""]
                            if not isinstance(assistant_lecturer, list):
                                assistant_lecturer = [assistant_lecturer, ""]
                            
                            subjects.append({
                                'name': subject_name,
                                'code': subject.get('code', ''),
                                'credits': subject.get('credit', 0),
                                'class': class_name,
                                'lecturer': course_lecturer[0] if course_lecturer else "",
                                'assistant': assistant_lecturer[0] if assistant_lecturer else ""
                            })
            
            return subjects, list(classes)
        except Exception as e:
            print(f"Erreur lors du chargement des matières: {str(e)}")
            return [], []
    
    def build_model(self):
        """Construire le modèle de programmation par contraintes."""
        model = cp_model.CpModel()
    
        
        # Variables de décision
        # x[c][s][r][p][d] = 1 si la classe c suit le sujet s dans la salle r à la période p le jour d
        x = {}
        
        # Pour chaque classe
        for c in self.classes:
            x[c] = {}
            # Pour chaque sujet de cette classe
            subjects_for_class = [s for s in self.subjects if s['class'] == c]
            
            for s in subjects_for_class:
                x[c][s['code']] = {}
                
                # Pour chaque salle
                for r in self.rooms:
                    x[c][s['code']][r['num']] = {}
                    
                    # Pour chaque période
                    for p in range(len(self.periods)):
                        x[c][s['code']][r['num']][p] = {}
                        
                        # Pour chaque jour
                        for d in range(len(self.days)):
                            x[c][s['code']][r['num']][p][d] = model.NewBoolVar(
                                f'x_{c}_{s["code"]}_{r["num"]}_{p}_{d}'
                            )
        
        # Contrainte 1: Une classe ne peut pas avoir plusieurs cours en même temps
        for c in self.classes:
            subjects_for_class = [s for s in self.subjects if s['class'] == c]
            
            for p in range(len(self.periods)):
                for d in range(len(self.days)):
                    # Toutes les variables pour cette classe, période et jour
                    vars_for_time = []
                    
                    for s in subjects_for_class:
                        for r in self.rooms:
                            if s['code'] in x[c] and r['num'] in x[c][s['code']]:
                                vars_for_time.append(x[c][s['code']][r['num']][p][d])
                    
                    # Au plus un cours par période pour une classe
                    if vars_for_time:
                        model.Add(sum(vars_for_time) <= 1)
        
        # Contrainte 2: Chaque cours doit être programmé exactement une fois par semaine
        for c in self.classes:
            subjects_for_class = [s for s in self.subjects if s['class'] == c]
            
            for s in subjects_for_class:
                # Toutes les variables pour ce cours
                vars_for_subject = []
                
                for r in self.rooms:
                    for p in range(len(self.periods)):
                        for d in range(len(self.days)):
                            if s['code'] in x[c] and r['num'] in x[c][s['code']]:
                                vars_for_subject.append(x[c][s['code']][r['num']][p][d])
                
                # Exactement un créneau pour ce cours
                if vars_for_subject:
                    model.Add(sum(vars_for_subject) <= 1)
        
        # Contrainte 3: Éviter les conflits d'enseignants
        # Un enseignant ne peut pas donner deux cours en même temps
        for p in range(len(self.periods)):
            for d in range(len(self.days)):
                # Grouper par enseignant
                teacher_vars = defaultdict(list)
                
                for c in self.classes:
                    subjects_for_class = [s for s in self.subjects if s['class'] == c]
                    
                    for s in subjects_for_class:
                        if s['lecturer']:  # Si l'enseignant est spécifié
                            for r in self.rooms:
                                if s['code'] in x[c] and r['num'] in x[c][s['code']]:
                                    teacher_vars[s['lecturer']].append(x[c][s['code']][r['num']][p][d])
                
                # Pour chaque enseignant, au plus un cours par créneau
                for teacher, vars_list in teacher_vars.items():
                    if vars_list:
                        model.Add(sum(vars_list) <= 1)
        
        # Contrainte 4: Éviter les conflits de salles
        # Une salle ne peut pas accueillir deux cours en même temps
        for r in self.rooms:
            for p in range(len(self.periods)):
                for d in range(len(self.days)):
                    # Toutes les variables pour cette salle, période et jour
                    vars_for_room = []
                    
                    for c in self.classes:
                        subjects_for_class = [s for s in self.subjects if s['class'] == c]
                        
                        for s in subjects_for_class:
                            if s['code'] in x[c] and r['num'] in x[c][s['code']]:
                                vars_for_room.append(x[c][s['code']][r['num']][p][d])
                    
                    # Au plus un cours par salle et par créneau
                    if vars_for_room:
                        model.Add(sum(vars_for_room) <= 1)
        
        # Fonction objectif: Maximiser les cours le matin (périodes 0 et 1)
        objective_terms = []
        
        for c in self.classes:
            subjects_for_class = [s for s in self.subjects if s['class'] == c]
            
            for s in subjects_for_class:
                for r in self.rooms:
                    for p in range(len(self.periods)):
                        for d in range(len(self.days)):
                            if s['code'] in x[c] and r['num'] in x[c][s['code']]:
                                # Ajouter le poids de la période à la fonction objectif
                                objective_terms.append(
                                    x[c][s['code']][r['num']][p][d] * self.period_weights[p]
                                )
        
        if objective_terms:
            model.Maximize(sum(objective_terms))
        
        return model, x
    
    def solve(self):
        """Résoudre le modèle d'emploi du temps."""
        model, x = self.build_model()
        
        solver = cp_model.CpSolver()
        
        # Paramètres du solveur pour améliorer les chances de trouver une solution
        solver.parameters.max_time_in_seconds = 300  # 5 minutes maximum
        solver.parameters.num_search_workers = 8  # Utiliser plus de threads
        solver.parameters.log_search_progress = True  # Activer les logs
        
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"Solution {'optimale' if status == cp_model.OPTIMAL else 'faisable'} trouvée!")
            
            # Stocker la solution
            self.solution = {
                'status': 'optimal' if status == cp_model.OPTIMAL else 'feasible',
                'objective_value': solver.ObjectiveValue(),
                'assignments': []
            }
            
            # Extraire les affectations
            for c in self.classes:
                subjects_for_class = [s for s in self.subjects if s['class'] == c]
                
                for s in subjects_for_class:
                    for r in self.rooms:
                        for p in range(len(self.periods)):
                            for d in range(len(self.days)):
                                if (s['code'] in x[c] and r['num'] in x[c][s['code']] and 
                                    p in x[c][s['code']][r['num']] and d in x[c][s['code']][r['num']][p] and
                                    solver.Value(x[c][s['code']][r['num']][p][d]) == 1):
                                    
                                    self.solution['assignments'].append({
                                        'class': c,
                                        'subject_code': s['code'],
                                        'subject_name': s['name'],
                                        'room': r['num'],
                                        'period': p,
                                        'day': d,
                                        'lecturer': s['lecturer']
                                    })
            
            return True
        else:
            print(f"Aucune solution trouvée! Status: {status}")
            return False
    
    def generate_timetable(self):
        """Générer l'emploi du temps sous forme de tableau."""
        if not self.solution:
            print("Veuillez d'abord résoudre le modèle!")
            return None
        
        # Créer un emploi du temps vide pour chaque classe
        timetables = {}
        
        for c in self.classes:
            # Créer un DataFrame vide
            timetable = pd.DataFrame(
                index=self.periods,
                columns=self.days
            )
            timetables[c] = timetable
        
        # Remplir les emplois du temps avec les affectations
        for assignment in self.solution['assignments']:
            cls = assignment['class']
            day = self.days[assignment['day']]
            period = self.periods[assignment['period']]
            
            cell_content = (
                f"{assignment['subject_code']} - {assignment['subject_name']}\n"
                f"Salle: {assignment['room']}\n"
                f"Prof: {assignment['lecturer']}"
            )
            
            timetables[cls].at[period, day] = cell_content
        
        self.timetable = timetables
        return timetables
    
    def save_timetables(self, output_dir):
        """Sauvegarder les emplois du temps au format Excel."""
        if not self.timetable:
            print("Veuillez d'abord générer l'emploi du temps!")
            return
        
        # Créer un fichier Excel avec une feuille par classe
        os.makedirs(output_dir, exist_ok=True)
        with pd.ExcelWriter(f"{output_dir}/emplois_du_temps.xlsx") as writer:
            for cls, timetable in self.timetable.items():
                timetable.to_excel(writer, sheet_name=cls)
        
        print(f"Emplois du temps sauvegardés dans {output_dir}/emplois_du_temps.xlsx")


# Programme principal pour tester la génération
if __name__ == "__main__":
    # Initialiser le générateur
    generator = TimetableGenerator('rooms.json', 'subjects.json')
    
    # Résoudre le modèle
    if generator.solve():
        # Générer les emplois du temps
        timetables = generator.generate_timetable()
        
        # Afficher l'emploi du temps pour une classe (à titre d'exemple)
        if timetables and 'INFO1s1' in timetables:
            print("\nEmploi du temps pour INFO1s1:\n")
            print(timetables['INFO1s1'])
        
        # Sauvegarder les emplois du temps
        generator.save_timetables('output')
    else:
        print("Impossible de générer un emploi du temps valide.")