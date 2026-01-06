import random
import logging
from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from src.models.models import Task, Story, Project, Section, User, TeamMembership
from src.utils.llm import generate_text
from src.utils.dates import random_date_in_range, get_business_day
from src.config import UNASSIGNED_TASK_RATE, GOOGLE_API_KEY

def generate_tasks(
    workspace_id: str, 
    projects: List[Project], 
    sections: List[Section], 
    users: List[User],
    team_memberships: List[TeamMembership]
) -> Tuple[List[Task], List[Story]]:
    
    tasks = []
    stories = []
    
    # Map project -> sections
    project_sections = {}
    for s in sections:
        if s.project_id not in project_sections:
            project_sections[s.project_id] = []
        project_sections[s.project_id].append(s)
        
    # Map project -> consistent team members (for assignment)
    # We find which team the project belongs to, then find users in that team
    project_members = {}
    team_user_map = {} # team_id -> [user_ids]
    for tm in team_memberships:
        if tm.team_id not in team_user_map:
            team_user_map[tm.team_id] = []
        team_user_map[tm.team_id].append(tm.user_id)
        
    for p in projects:
        t_id = p.team_id
        if t_id and t_id in team_user_map:
            # Filter users list to get actual User objects
            member_ids = team_user_map[t_id]
            project_members[p.id] = [u for u in users if u.id in member_ids]
        else:
            project_members[p.id] = users # Fallback: anyone can check it out

    # --- POOLING STRATEGY (OPTIMIZED v2) ---
    logging.info("Initializing Task & Comment Pools (Performance Super-Optimization)...")
    task_pool = {}
    comment_pool = []

    def get_cached_task_names(project_name, section_name):
        """Generates 20 names at once and caches them to avoid N+1 API calls."""
        key = f"{project_name}-{section_name}"
        if key not in task_pool:
            # Ask LLM for a BATCH of names
            prompt = f"List 20 realistic, short task names for a '{project_name}' project in the '{section_name}' phase. Return just the names, one per line."
            text = generate_text(prompt, temperature=0.9)
            # Split by newlines and clean up
            names = [line.strip().lstrip('- ').strip() for line in text.split('\n') if line.strip()]
            task_pool[key] = names if names else ["Generic Task"]
        return task_pool[key]

    # Pre-fill comment pool ONCE
    c_prompt = "Generate 50 short, professional comments for a project management tool (e.g., 'Looking into it', 'Done', 'Fixed'). One per line."
    c_text = generate_text(c_prompt)
    comment_pool.extend([l.strip().lstrip('- ').strip() for l in c_text.split('\n') if l.strip()])
    if not comment_pool:
        comment_pool = ["Looking into it.", "Done.", "Can you review?", "Blocked.", "Nice work!"]

    for project in projects:
        p_sections = project_sections.get(project.id, [])
        if not p_sections:
            continue
            
        # Determine number of tasks
        num_tasks = random.randint(15, 45) 
        
        # 1. OPTIMIZATION: Get the pool of names for this specific project context
        # We pick one section usage as the 'context' for the batch, or we could rotate.
        # To match user request of "project context", we'll just query once per project/section combo lazily
        
        for _ in range(num_tasks):
            section = random.choice(p_sections)
            
            # 2. FAST GENERATION: Pick from pool instead of calling API
            available_names = get_cached_task_names(project.name, section.name)
            name = random.choice(available_names)
            
            # 2. Assignee
            possible_assignees = project_members.get(project.id, users)
            if random.random() < UNASSIGNED_TASK_RATE or not possible_assignees:
                assignee_id = None
            else:
                assignee_id = random.choice(possible_assignees).id
                
            # 3. Dates & Status
            created_at = random_date_in_range(project.created_at, datetime.now())
            
            completed = False
            completed_at = None
            due_date = None
            
            lower_sec = section.name.lower()
            if "done" in lower_sec or "published" in lower_sec:
                completed = True
                completed_at = random_date_in_range(created_at, datetime.now())
            elif "backlog" in lower_sec:
                due_date = None
            else:
                # In progress
                due_date = (created_at + timedelta(days=random.randint(1, 14))).date()
                if due_date < datetime.now().date():
                     if random.random() > 0.2:
                         due_date = (datetime.now() + timedelta(days=random.randint(1, 7))).date()

            # Ensure logic: completed_at > created_at
            if completed_at and completed_at < created_at:
                completed_at = created_at + timedelta(hours=random.randint(1, 48))

            # Null Entropy
            description = f"Task description for {name}. Generated by simulation."
            if random.random() < 0.1: 
                description = None

            task = Task(
                name=name,
                workspace_id=workspace_id,
                project_id=project.id,
                section_id=section.id,
                assignee_id=assignee_id,
                description=description, 
                completed=completed,
                completed_at=completed_at,
                due_date=due_date,
                created_at=created_at
            )
            tasks.append(task)
            
            # 4. FAST COMMENTS: Pick from pool
            if random.random() < 0.4: 
                num_comments = random.randint(1, 3)
                for _ in range(num_comments):
                    commenter = random.choice(possible_assignees) if possible_assignees else random.choice(users)
                    c_text = random.choice(comment_pool)
                    
                    story = Story(
                        target_id=task.id,
                        text=c_text,
                        created_by=commenter.id,
                        created_at=random_date_in_range(created_at, datetime.now())
                    )
                    stories.append(story)
    
    return tasks, stories
