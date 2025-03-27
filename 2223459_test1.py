import pandas as pd
import re

attendance_data = [
    (101, '2024-03-01', 'Absent'),
    (101, '2024-03-02', 'Absent'),
    (101, '2024-03-03', 'Absent'),
    (101, '2024-03-04', 'Absent'),
    (101, '2024-03-05', 'Present'),
    (102, '2024-03-01', 'Absent'),
    (102, '2024-03-02', 'Absent'),
    (102, '2024-03-03', 'Absent'),
    (102, '2024-03-04', 'Absent'),
    (102, '2024-03-05', 'Absent'),
    (103, '2024-03-06', 'Absent'),
    (103, '2024-03-07', 'Absent'),
    (103, '2024-03-08', 'Absent'),
    (103, '2024-03-09', 'Absent'),
    (104, '2024-03-01', 'Present'),
    (104, '2024-03-02', 'Present'),
    (104, '2024-03-03', 'Present'),
    (104, '2024-03-04', 'Present'),
    (104, '2024-03-05', 'Present'),
]

df = pd.DataFrame(attendance_data, columns=['student_id', 'attendance_date', 'status'])
df['attendance_date'] = pd.to_datetime(df['attendance_date'])

def find_absence_streaks(df):
    results = []
    
    for student_id, group in df.groupby('student_id'):
        group = group.sort_values('attendance_date')
        group['absent_flag'] = (group['status'] == 'Absent').astype(int)
        

        streaks = []
        start_date, end_date = None, None
        count = 0
        
        for i, row in group.iterrows():
            if row['absent_flag']:
                if start_date is None:
                    start_date = row['attendance_date']
                end_date = row['attendance_date']
                count += 1
            else:
                if count > 3:
                    streaks.append((start_date, end_date, count))
                start_date, end_date, count = None, None, 0
        
        if count > 3:
            streaks.append((start_date, end_date, count))
        
        if streaks:
            latest_streak = max(streaks, key=lambda x: x[1])  # Get latest by end_date
            results.append((student_id, latest_streak[0], latest_streak[1], latest_streak[2]))
    
    result_df = pd.DataFrame(results, columns=['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days'])
    return result_df

output_df = find_absence_streaks(df)
print(output_df)


def is_valid_email(email):
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*@[a-zA-Z]+\.com$'
    return re.match(pattern, email) is not None

def run():
    
    absence_streaks_data = [
        (101, '01-03-2024', '04-03-2024', 4),
        (102, '02-03-2024', '05-03-2024', 4),
        (103, '05-03-2024', '09-03-2024', 5),
    ]
    
    absence_df = pd.DataFrame(absence_streaks_data, columns=['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days'])
    
   
    students_data = [
        (101, 'Alice Johnson', 'alice_parent@example.com'),
        (102, 'Bob Smith', 'bob_parent@example.com'),
        (103, 'Charlie Brown', 'invalid_email.com'),
        (104, 'David Lee', 'invalid_email.com'),
        (105, 'Eva White', 'eva_white@example.com'),
    ]
    

    students_df = pd.DataFrame(students_data, columns=['student_id', 'student_name', 'parent_email'])
    
 
    merged_df = pd.merge(absence_df, students_df, on='student_id', how='left')


    merged_df['email'] = merged_df['parent_email'].apply(lambda x: x if is_valid_email(x) else None)
    
    
    merged_df['msg'] = merged_df.apply(
        lambda row: f"Dear Parent, your child {row['student_name']} was absent from {row['absence_start_date']} to {row['absence_end_date']} for {row['total_absent_days']} days. Please ensure their attendance improves." 
        if row['email'] else None,
        axis=1
    )
  
    merged_df.drop(columns=['parent_email', 'student_name'], inplace=True)
    
    return merged_df
