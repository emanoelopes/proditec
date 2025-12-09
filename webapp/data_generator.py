import pandas as pd
import numpy as np
import random

def generate_student_data(num_students=30, class_name="Turma A"):
    """
    Generates mock data for a class of students.
    """
    np.random.seed(42 if class_name == "Turma A" else 24) # Different seeds for different classes
    
    first_names = ["Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Julia", 
                   "Lucas", "Mariana", "Nicolas", "Olivia", "Pedro", "Rafael", "Sofia", "Thiago", "Vitoria", "Yuri"]
    last_names = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Almeida", "Pereira", "Lima", "Gomes"]
    
    students = []
    
    for _ in range(num_students):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Simulate grades for 5 modules
        # Profile 1: High performers (high grades, high engagement)
        # Profile 2: Struggling (low grades, high engagement)
        # Profile 3: Disengaged (low grades, low engagement)
        
        profile = np.random.choice([1, 2, 3], p=[0.4, 0.3, 0.3])
        
        if profile == 1:
            grades = np.random.normal(8.5, 1.0, 5)
            login_count = int(np.random.normal(50, 10))
            forum_posts = int(np.random.normal(15, 5))
        elif profile == 2:
            grades = np.random.normal(5.0, 1.5, 5)
            login_count = int(np.random.normal(40, 10))
            forum_posts = int(np.random.normal(8, 3))
        else: # Profile 3
            grades = np.random.normal(3.0, 2.0, 5)
            login_count = int(np.random.normal(10, 5))
            forum_posts = int(np.random.normal(2, 1))
            
        grades = np.clip(grades, 0, 10) # Ensure grades are between 0 and 10
        login_count = max(0, login_count)
        forum_posts = max(0, forum_posts)
        
        student = {
            "Nome": name,
            "Turma": class_name,
            "Módulo 1": round(grades[0], 1),
            "Módulo 2": round(grades[1], 1),
            "Módulo 3": round(grades[2], 1),
            "Módulo 4": round(grades[3], 1),
            "Módulo 5": round(grades[4], 1),
            "Acessos": login_count,
            "Postagens no Fórum": forum_posts
        }
        students.append(student)
        
    return pd.DataFrame(students)

def get_all_data():
    """
    Returns combined data for Turma A and Turma B.
    """
    df_a = generate_student_data(35, "Turma A")
    df_b = generate_student_data(30, "Turma B")
    return pd.concat([df_a, df_b], ignore_index=True)
