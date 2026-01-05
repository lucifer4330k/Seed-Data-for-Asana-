import sqlite3
import pandas as pd
from pathlib import Path
from src.config import DB_PATH

def verify():
    conn = sqlite3.connect(DB_PATH)
    
    print("=== Table Counts ===")
    tables = ["workspaces", "users", "teams", "projects", "sections", "tasks", "stories"]
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"{t}: {count}")
        
    print("\n=== Sample Tasks ===")
    tasks = pd.read_sql_query("SELECT name, description, completed, due_date FROM tasks ORDER BY RANDOM() LIMIT 5", conn)
    print(tasks.to_string())
    
    print("\n=== Sample Stories ===")
    stories = pd.read_sql_query("SELECT text, created_at FROM stories ORDER BY RANDOM() LIMIT 5", conn)
    print(stories.to_string())
    
    print("\n=== Integrity Check ===")
    orphans = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id NOT IN (SELECT id FROM projects)").fetchone()[0]
    print(f"Orphan Tasks: {orphans}")
    
    print("\n=== User Timestamp Distribution ===")
    user_dates = pd.read_sql_query("SELECT joined_at FROM users", conn)
    user_dates['joined_at'] = pd.to_datetime(user_dates['joined_at'])
    print(f"Min Joined Date: {user_dates['joined_at'].min()}")
    print(f"Max Joined Date: {user_dates['joined_at'].max()}")
    print(f"Unique Dates: {user_dates['joined_at'].nunique()}")
    
    print("\n=== Data Quality Checks ===")
    
    # 1. Weekend Check for Tasks
    tasks_dates = pd.read_sql_query("SELECT created_at FROM tasks", conn)
    tasks_dates['created_at'] = pd.to_datetime(tasks_dates['created_at'])
    weekends = tasks_dates['created_at'].dt.dayofweek >= 5
    weekend_pct = weekends.mean() * 100
    print(f"Tasks Created on Weekends: {weekend_pct:.2f}% (Target: < 5%)")
    
    # 2. Logic Check: Completed > Created
    logic_fail = conn.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1 AND completed_at < created_at").fetchone()[0]
    print(f"Logic Failures (Completed < Created): {logic_fail} (Target: 0)")
    
    # 3. Null Check
    null_desc = conn.execute("SELECT COUNT(*) FROM tasks WHERE description IS NULL").fetchone()[0]
    total_tasks = len(tasks_dates)
    print(f"Tasks with NULL Description: {null_desc} ({null_desc/total_tasks*100:.1f}%)")
    
    # 4. Mock Content Check
    mock_content = conn.execute("SELECT COUNT(*) FROM tasks WHERE name LIKE '%[MOCK CONTENT]%' OR description LIKE '%[MOCK CONTENT]%'").fetchone()[0]
    print(f"Rows with '[MOCK CONTENT]': {mock_content} (Target: 0)")

    conn.close()

if __name__ == "__main__":
    verify()
