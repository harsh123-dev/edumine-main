import numpy as np
import pandas as pd
import random
import os

np.random.seed(42)
random.seed(42)

n_samples = 600

departments = ['Computer Science', 'Data Science', 'Electronics & Comm.', 'Information Tech', 'Mechanical Eng.']
parent_edus = ['High School', 'Associate Degree', 'Bachelor Degree', 'Master Degree', 'Doctorate']
first_names = [
    'Aarav', 'Diya', 'Rohan', 'Ananya', 'Vivaan', 'Isha', 'Aditya', 'Meera', 'Kabir', 'Tanvi',
    'Arjun', 'Pooja', 'Rahul', 'Sneha', 'Vikram', 'Neha', 'Karan', 'Priya', 'Aryan', 'Kavya',
    'Dev', 'Riya', 'Akash', 'Aditi', 'Nikhil', 'Shreya', 'Siddharth', 'Nandini', 'Varun', 'Swati'
]
last_names = [
    'Sharma', 'Verma', 'Patel', 'Reddy', 'Iyer', 'Gupta', 'Kumar', 'Singh', 'Nair', 'Joshi',
    'Rao', 'Chopra', 'Malhotra', 'Deshmukh', 'Bose', 'Choudhury', 'Menon', 'Chatterjee', 'Bhat', 'Mehta'
]

records = []

for i in range(1, n_samples + 1):
    student_id = f"STU-{1000 + i}"
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    name = f"{fname} {lname}"
    dept = random.choice(departments)
    gender = random.choice(['Female', 'Male'])
    
    # Latent student engagement profile to ensure realistic correlations
    # 0 = disengaged/struggling, 1 = average, 2 = diligent/high-achiever
    profile = np.random.choice([0, 1, 2], p=[0.25, 0.45, 0.30])
    
    if profile == 0:
        # Struggling / Disengaged
        study_hours = round(np.random.normal(6, 2.5), 1)
        attendance = round(np.random.normal(64, 9), 1)
        lms_hours = round(np.random.normal(4.5, 2), 1)
        assignment_score = round(np.random.normal(52, 12), 1)
        midterm_score = round(np.random.normal(50, 11), 1)
        past_failures = int(np.random.choice([0, 1, 2, 3], p=[0.3, 0.4, 0.2, 0.1]))
        extracurricular = random.choice(['No', 'No', 'Yes'])
        parent_edu = random.choice(['High School', 'High School', 'Associate Degree', 'Bachelor Degree'])
    elif profile == 1:
        # Average / Moderate
        study_hours = round(np.random.normal(14, 3.5), 1)
        attendance = round(np.random.normal(81, 6), 1)
        lms_hours = round(np.random.normal(9.5, 3), 1)
        assignment_score = round(np.random.normal(74, 8), 1)
        midterm_score = round(np.random.normal(71, 9), 1)
        past_failures = int(np.random.choice([0, 1], p=[0.85, 0.15]))
        extracurricular = random.choice(['Yes', 'No'])
        parent_edu = random.choice(parent_edus)
    else:
        # Diligent / High-achiever
        study_hours = round(np.random.normal(24, 4), 1)
        attendance = round(np.random.normal(92, 4), 1)
        lms_hours = round(np.random.normal(16, 4), 1)
        assignment_score = round(np.random.normal(89, 6), 1)
        midterm_score = round(np.random.normal(88, 7), 1)
        past_failures = 0
        extracurricular = random.choice(['Yes', 'Yes', 'No'])
        parent_edu = random.choice(['Bachelor Degree', 'Master Degree', 'Doctorate', 'Associate Degree'])
        
    # Bounds clamping
    study_hours = max(1.0, min(38.0, study_hours))
    attendance = max(40.0, min(99.5, attendance))
    lms_hours = max(1.0, min(35.0, lms_hours))
    assignment_score = max(25.0, min(100.0, assignment_score))
    midterm_score = max(20.0, min(100.0, midterm_score))
    
    # Calculate Final Exam Score from weighted behavioral and academic attributes + noise
    latent_academic = (
        0.30 * midterm_score +
        0.25 * assignment_score +
        0.20 * attendance +
        0.15 * (study_hours * 2.5) +
        0.10 * (lms_hours * 2.8) -
        (past_failures * 4.5) +
        np.random.normal(0, 4.5)
    )
    final_exam = round(max(15.0, min(100.0, latent_academic)), 1)
    
    # Final GPA (scale 0 - 4.0)
    gpa = round(max(1.0, min(4.0, (final_exam / 25.0) + np.random.normal(0, 0.08))), 2)
    
    # Academic Risk Status: based on final_exam < 60, attendance < 72%, or assignment < 60%
    risk_score = (
        (1.0 if attendance < 72.0 else 0.0) * 0.35 +
        (1.0 if assignment_score < 60.0 else 0.0) * 0.30 +
        (1.0 if midterm_score < 55.0 else 0.0) * 0.25 +
        (1.0 if study_hours < 8.0 else 0.0) * 0.15 +
        (0.20 * past_failures)
    )
    
    # Threshold for Risk
    if risk_score >= 0.45 or final_exam < 55.0:
        academic_risk = "At-Risk"
    else:
        academic_risk = "Safe"
        
    records.append({
        'Student_ID': student_id,
        'Name': name,
        'Department': dept,
        'Gender': gender,
        'Study_Hours_Per_Week': study_hours,
        'Attendance_Percentage': attendance,
        'LMS_Engagement_Hours': lms_hours,
        'Assignment_Completion_Rate': assignment_score,
        'Midterm_Score': midterm_score,
        'Past_Failures': past_failures,
        'Parent_Education': parent_edu,
        'Extracurricular_Activity': extracurricular,
        'Final_Exam_Score': final_exam,
        'Final_GPA': gpa,
        'Academic_Risk': academic_risk
    })

df = pd.DataFrame(records)
os.makedirs('data', exist_ok=True)
df.to_csv('data/sample_students.csv', index=False)
print(f"Successfully generated {len(df)} student records at data/sample_students.csv")
print(f"Risk distribution:\n{df['Academic_Risk'].value_counts()}")
