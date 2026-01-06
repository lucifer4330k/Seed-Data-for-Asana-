import random
import logging
from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from src.models.models import Task, Story, Project, Section, User, TeamMembership
from src.utils.llm import generate_text
from src.utils.dates import random_date_in_range, get_business_day
from src.config import UNASSIGNED_TASK_RATE, GOOGLE_API_KEY

# Add these pools at the top of the file
TASK_NAME_POOL = []
COMMENT_POOL = []
DESCRIPTION_POOL = []

def ensure_pools_populated():
    if not TASK_NAME_POOL:
        # Generate a batch of generic task names ONCE
        try:
            prompt = "List 50 realistic, short task names for a tech company (e.g. 'Fix login bug', 'Q3 Budget', 'Design Review'). Output just the names."
            text = generate_text(prompt)
            TASK_NAME_POOL.extend([line.strip("- ").strip() for line in text.split('\n') if line.strip()])
        except Exception as e:
            logging.warning(f"LLM failed for task pool: {e}")
            # Fallback if API completely fails
            TASK_NAME_POOL.extend(["Fix bug", "Update docs", "Meeting", "Review PR", "Deploy", "Test Feature"])

    if not COMMENT_POOL:
        # Generate a batch of comments ONCE
        try:
            prompt = "List 30 short professional comments (e.g. 'Done', 'Looking into it', 'Blocked')."
            text = generate_text(prompt)
            COMMENT_POOL.extend([line.strip("- ").strip() for line in text.split('\n') if line.strip()])
        except Exception as e:
            logging.warning(f"LLM failed for comment pool: {e}")
            COMMENT_POOL.extend(["Done", "Looking into it", "Blocked", "Nice work"])
            
    if not DESCRIPTION_POOL:
        # Generate a batch of descriptions ONCE
        try:
            prompt = "List 20 realistic task descriptions (1-2 sentences). e.g., 'Please review the attached PR.', 'Customer reported an issue on staging.'. Output just the text lines."
            text = generate_text(prompt)
            DESCRIPTION_POOL.extend([line.strip("- ").strip() for line in text.split('\n') if line.strip()])
        except Exception as e:
            logging.warning(f"LLM failed for description pool: {e}")
            DESCRIPTION_POOL.extend(["Please review attached docs.", "Priority fix required.", "See ticket #543."])

def generate_tasks(
    workspace_id: str, 
    projects: List[Project], 
    sections: List[Section], 
    users: List[User],
    team_memberships: List[TeamMembership]
) -> Tuple[List[Task], List[Story]]:
    
    # 1. Initialize pools
    ensure_pools_populated()
    
    tasks = []
    stories = []
    
    # Map project -> sections
    project_sections = {}
    for s in sections:
        if s.project_id not in project_sections:
            project_sections[s.project_id] = []
        project_sections[s.project_id].append(s)
        
    # Map project -> consistent team members (for assignment)
    project_members = {}
    team_user_map = {} 
    for tm in team_memberships:
        if tm.team_id not in team_user_map:
            team_user_map[tm.team_id] = []
        team_user_map[tm.team_id].append(tm.user_id)
        
    for p in projects:
        t_id = p.team_id
        if t_id and t_id in team_user_map:
            member_ids = team_user_map[t_id]
            project_members[p.id] = [u for u in users if u.id in member_ids]
        else:
            project_members[p.id] = users 

    for project in projects:
        p_sections = project_sections.get(project.id, [])
        if not p_sections:
            continue
            
        num_tasks = random.randint(15, 45)
        
        for _ in range(num_tasks):
            section = random.choice(p_sections)
            
            # 2. FAST FIX: Pick from pool instead of calling API
            name = random.choice(TASK_NAME_POOL) if TASK_NAME_POOL else "General Task"
            
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
                due_date = (created_at + timedelta(days=random.randint(1, 14))).date()
                if due_date < datetime.now().date():
                     if random.random() > 0.2:
                         due_date = (datetime.now() + timedelta(days=random.randint(1, 7))).date()

            if completed_at and completed_at < created_at:
                completed_at = created_at + timedelta(hours=random.randint(1, 48))

            description = None
            if DESCRIPTION_POOL:
                description = random.choice(DESCRIPTION_POOL)
            else:
                 description = f"Task description for {name}. Generated by simulation."
                 
            # Null Entropy: 10% still have no description (Realism)
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
            
            # 3. FAST FIX: Comments from pool
            if random.random() < 0.4:
                num_comments = random.randint(1, 3)
                for _ in range(num_comments):
                    c_text = random.choice(COMMENT_POOL) if COMMENT_POOL else "Looking into it."
                    
                    commenter = random.choice(possible_assignees) if possible_assignees else random.choice(users)
                    story = Story(
                        target_id=task.id,
                        text=c_text,
                        created_by=commenter.id,
                        created_at=random_date_in_range(created_at, datetime.now())
                    )
                    stories.append(story)
    
    return tasks, stories
