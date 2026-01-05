import os
import sqlite3
import logging
from pathlib import Path
from src.config import DB_PATH
from src.generators.users import generate_workspace, generate_users, generate_teams
from src.generators.structure import generate_projects
from src.generators.tasks import generate_tasks

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_db():
    logging.info("Initializing Database...")
    schema_path = Path("schema.sql")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
            
def save_objects(conn, table_name, objects):
    if not objects:
        return
    
    # Get columns from the first object
    # Assumes all objects are dataclasses and have matching fields to table columns
    # We might need explicit mapping if names differ, but our models match schema.
    
    sample = objects[0]
    columns = [k for k in sample.__dict__.keys()]
    placeholders = ",".join(["?"] * len(columns))
    col_names = ",".join(columns)
    
    values = []
    for obj in objects:
        # Convert date/datetime objects to string/isoformat if needed, 
        # but sqlite3 adapter often handles this. Better to be explicit for safety?
        # Let's rely on standard python types, users are usually fine.
        vals = []
        for k in columns:
            v = getattr(obj, k)
            if v is None:
                vals.append(None)
            else:
                 vals.append(v)
        values.append(tuple(vals))
        
    logging.info(f"Saving {len(objects)} rows to {table_name}...")
    
    batch_size = 500
    for i in range(0, len(values), batch_size):
        batch = values[i:i + batch_size]
        try:
            conn.executemany(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})", batch)
            conn.commit()
            logging.info(f"Saved batch {i//batch_size} ({len(batch)} items) to {table_name}")
        except Exception as e:
            logging.error(f"Error saving batch {i} to {table_name}: {e}")
            logging.error(f"First item in batch: {batch[0] if batch else 'Empty'}")

def main():
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Workspace
    logging.info("Generating Workspace...")
    workspace = generate_workspace()
    save_objects(conn, "workspaces", [workspace])
    
    # 2. Users
    logging.info("Generating Users...")
    users = generate_users(workspace.id)
    save_objects(conn, "users", users)
    
    # 3. Teams & Memberships
    logging.info("Generating Teams...")
    teams, memberships = generate_teams(workspace.id, users)
    save_objects(conn, "teams", teams)
    save_objects(conn, "team_memberships", memberships)
    
    # 4. Projects & Sections
    logging.info("Generating Projects...")
    projects, sections = generate_projects(workspace.id, teams, users)
    save_objects(conn, "projects", projects)
    save_objects(conn, "sections", sections)
    
    # 5. Tasks & Stories
    logging.info("Generating Tasks (this may take time with LLM)...")
    tasks, stories = generate_tasks(workspace.id, projects, sections, users, memberships)
    save_objects(conn, "tasks", tasks)
    save_objects(conn, "stories", stories)
    
    conn.close()
    logging.info(f"Simulation Complete. Database at: {DB_PATH}")

if __name__ == "__main__":
    main()
