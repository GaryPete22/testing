import pandas as pd
import re

def is_valid_email(email):
    """Check if email is valid as per given criteria."""
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*@[a-zA-Z]+\.(com)$'
    return bool(re.match(pattern, email))

def find_absence_streaks(attendance_df):
    """Find students absent for more than three consecutive days (latest streak)."""
    attendance_df['attendance_date'] = pd.to_datetime(attendance_df['attendance_date'])
    attendance_df = attendance_df.sort_values(by=['student_id', 'attendance_date'])
    
    absence_streaks = []
    
    for student_id, group in attendance_df.groupby('student_id'):
        group = group[group['status'] == 'Absent'].copy()  # Fix: Use .copy() to avoid SettingWithCopyWarning
        group['gap'] = group['attendance_date'].diff().dt.days.ne(1).cumsum()

        streaks = group.groupby('gap')['attendance_date'].agg(['min', 'max', 'count']).reset_index()
        latest_streak = streaks[streaks['count'] > 3].tail(1)  # Get the latest streak

        if not latest_streak.empty:
            absence_streaks.append([
                student_id,
                pd.Timestamp(latest_streak['min'].values[0]).strftime('%d-%m-%Y'),  # Fix: Convert numpy datetime
                pd.Timestamp(latest_streak['max'].values[0]).strftime('%d-%m-%Y'),  # Fix: Convert numpy datetime
                int(latest_streak['count'].values[0])  # Convert to int
            ])
    
    return pd.DataFrame(absence_streaks, columns=['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days'])

def run():
    attendance_data = [
        (101, '2024-03-01', 'Absent'), (101, '2024-03-02', 'Absent'), 
        (101, '2024-03-03', 'Absent'), (101, '2024-03-04', 'Absent'), 
        (101, '2024-03-05', 'Present'),
        (102, '2024-03-02', 'Absent'), (102, '2024-03-03', 'Absent'),
        (102, '2024-03-04', 'Absent'), (102, '2024-03-05', 'Absent'),
        (103, '2024-03-05', 'Absent'), (103, '2024-03-06', 'Absent'),
        (103, '2024-03-07', 'Absent'), (103, '2024-03-08', 'Absent'),
        (103, '2024-03-09', 'Absent'), (104, '2024-03-01', 'Present'),
        (104, '2024-03-02', 'Present'), (104, '2024-03-03', 'Absent'),
        (104, '2024-03-04', 'Present'), (104, '2024-03-05', 'Present')
    ]

    attendance_df = pd.DataFrame(attendance_data, columns=['student_id', 'attendance_date', 'status'])
   
   
    absence_streaks_df = find_absence_streaks(attendance_df)

    students_data = [
        (101, 'Alice Johnson', 'alice_parent@example.com'),
        (102, 'Bob Smith', 'bob_parent@example.com'),
        (103, 'Charlie Brown', 'invalid_email.com'),
        (104, 'David Lee', 'invalid_email.com'),
        (105, 'Eva White', 'eva_white@example.com')
    ]

    students_df = pd.DataFrame(students_data, columns=['student_id', 'student_name', 'parent_email'])

    final_df = pd.merge(absence_streaks_df, students_df, on='student_id', how='left')
    
    
    final_df['email'] = final_df['parent_email'].apply(lambda x: x if is_valid_email(x) else None)

  
    final_df['msg'] = final_df.apply(
        lambda row: f"Dear Parent, your child {row['student_name']} was absent from {row['absence_start_date']} to {row['absence_end_date']} for {row['total_absent_days']} days. Please ensure their attendance improves."
        if row['email'] else None, axis=1
    )
    

    final_df.drop(columns=['parent_email', 'student_name'], inplace=True)

    return final_df

output_df = run()
print(output_df)
