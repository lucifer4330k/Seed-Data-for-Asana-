-- Asana Simulation Database Schema

-- Enable Foreign Key constraints
PRAGMA foreign_keys = ON;

-- 1. Workspaces / Organizations
CREATE TABLE workspaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Users
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    avatar_url TEXT,
    workspace_id TEXT NOT NULL,
    role TEXT, -- e.g., 'Admin', 'Member', 'Guest'
    department TEXT, -- e.g., 'Engineering', 'Marketing'
    joined_at TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

-- 3. Teams
CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    workspace_id TEXT NOT NULL,
    created_at TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

-- 4. Team Memberships
CREATE TABLE team_memberships (
    user_id TEXT NOT NULL,
    team_id TEXT NOT NULL,
    role TEXT DEFAULT 'Member',
    PRIMARY KEY (user_id, team_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- 5. Projects
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    team_id TEXT,
    workspace_id TEXT NOT NULL,
    owner_id TEXT,
    archived BOOLEAN DEFAULT 0,
    color TEXT,
    start_date DATE,
    due_date DATE,
    created_at TIMESTAMP,
    modified_at TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- 6. Sections (Columns in Board view, Sections in List view)
CREATE TABLE sections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    project_id TEXT NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 7. Tasks
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    assignee_id TEXT,
    project_id TEXT,      -- Can be null if it's a private task, but usually in a project
    section_id TEXT,
    parent_id TEXT,       -- For subtasks
    workspace_id TEXT NOT NULL,
    
    -- Status & Dates
    completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    due_date DATE,
    start_date DATE,
    created_at TIMESTAMP NOT NULL,
    modified_at TIMESTAMP,
    
    -- Meta
    priority TEXT,        -- Low, Medium, High (System field)
    
    FOREIGN KEY (assignee_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (parent_id) REFERENCES tasks(id),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

-- 8. Stories (Comments & Activity)
CREATE TABLE stories (
    id TEXT PRIMARY KEY,
    target_id TEXT NOT NULL, -- Usually task_id
    target_type TEXT DEFAULT 'task',
    text TEXT,               -- The comment body
    type TEXT DEFAULT 'comment', -- 'comment', 'system'
    created_by TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 9. Custom Field Definitions
CREATE TABLE custom_field_definitions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- 'text', 'number', 'enum', 'date'
    workspace_id TEXT NOT NULL,
    description TEXT,
    enum_options JSON, -- Store options like {"high": "red", "low": "blue"}
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

-- 10. Custom Field Values (EAV)
CREATE TABLE custom_field_values (
    task_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    value TEXT, -- Stores the actual value (or enum option ID)
    value_number REAL, -- For sorting numeric fields easily
    PRIMARY KEY (task_id, field_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(id)
);

-- 11. Tags
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT,
    workspace_id TEXT NOT NULL,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

-- 12. Task Tags Association
CREATE TABLE task_tags (
    task_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- Indexes for performance
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_stories_target ON stories(target_id);
