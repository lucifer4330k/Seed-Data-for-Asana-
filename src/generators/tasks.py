import random
from typing import List, Tuple
from datetime import datetime, timedelta
from src.models.models import Task, Story, Project, Section, User, TeamMembership
from src.utils.llm import generate_text
from src.utils.dates import random_date_in_range
from src.config import UNASSIGNED_TASK_RATE

# --- HARDCODED POOLS (Safety Net) ---
# This ensures variety even if the LLM API fails or returns a single line.
TASK_NAMES_POOL = [
    "Fix memory leak in Redis cache", "Update landing page CSS", "Q3 Financial Review", 
    "Onboard new marketing intern", "Refactor user authentication API", "Design system consistency check",
    "Client feedback integration", "Weekly sync notes", "Prepare slide deck for board meeting",
    "Database migration to PostgreSQL 15", "Implement Dark Mode", "Fix typo in Terms of Service",
    "Optimize image loading speed", "Conduct user interviews", "Draft blog post for new feature",
    "Renew SSL certificates", "Update dependency versions", "Merge PR #405", "Resolve merge conflicts",
    "Setup CI/CD pipeline", "Configure AWS bucket permissions", "Write unit tests for billing module",
    "Sales team quarterly targets", "Update employee handbook", "Schedule team offsite",
    "Fix broken link on pricing page", "Investigate high latency in search", "Rotate API keys",
    "Localization for Spanish market", "Accessibility audit (WCAG)", "Redesign login flow",
    "Update privacy policy", "GDPR compliance check", "Monitor server logs", "Clean up old Jira tickets",
    "Prepare tax documents", "Review vendor contracts", "Brainstorm Q4 roadmap",
    "Fix text overflow on mobile", "Implement OAuth2 login", "Update SEO meta tags",
    "Create tutorial video", "Send newsletter", "Backup database", "Prune unused docker images"
]

COMMENTS_POOL = [
    "Done.", "Looking into it.", "Can you review this?", "Blocked by the backend team.",
    "Fixed in the latest build.", "Uploading assets now.", "Please see attached screenshot.",
    "Scheduling a meeting to discuss.", "This is ready for QA.", "Found a bug, reopening.",
    "LGTM!", "Nice work.", "Waiting on client feedback.", "Merging now.",
    "Deploying to staging.", "Can we push this to next sprint?", "I need access to the repo.",
    "Updated the docs.", "Verified in production.", "Let's discuss in the standup."
]

def generate_tasks(workspace_id, projects, sections, users, team_memberships):
    tasks = []
    stories = []
    
    # Map project -> sections
    project_sections = {s.project_id: [] for s in sections}
    for s in sections:
        project_sections[s.project_id].append(s)
        
    # Map project -> team members
    team_user_map = {}
    for tm in team_memberships:
        if tm.team_id not in team_user_map: team_user_map[tm.team_id] = []
        team_user_map[tm.team_id].append(tm.user_id)
        
    project_members = {}
    for p in projects:
        if p.team_id and p.team_id in team_user_map:
            p_users = [u for u in users if u.id in team_user_map[p.team_id]]
            project_members[p.id] = p_users if p_users else users
        else:
            project_members[p.id] = users

    for project in projects:
        p_sections = project_sections.get(project.id, [])
        if not p_sections: continue
            
        num_tasks = random.randint(5, 25)
        
        for _ in range(num_tasks):
            section = random.choice(p_sections)
            
            # 1. PICK FROM POOL
            base_name = random.choice(TASK_NAMES_POOL)
            # Add salt (random number) to 30% of tasks to make them unique
            name = f"{base_name} (#{random.randint(100, 9999)})" if random.random() < 0.3 else base_name
            
            # Assignee
            possible_assignees = project_members.get(project.id, users)
            assignee_id = None
            if possible_assignees and random.random() > UNASSIGNED_TASK_RATE:
                assignee_id = random.choice(possible_assignees).id
                
            # Dates
            created_at = random_date_in_range(project.created_at, datetime.now())
            completed = False
            completed_at = None
            due_date = (created_at + timedelta(days=random.randint(1, 14))).date()
            
            if "done" in section.name.lower() or "complete" in section.name.lower():
                completed = True
                completed_at = random_date_in_range(created_at, datetime.now())
            
            # 2. Entropy (Empty Descriptions)
            desc = f"Description for {name}"
            if random.random() < 0.15: # 15% chance of no description
                desc = None

            task = Task(
                name=name,
                workspace_id=workspace_id,
                project_id=project.id,
                section_id=section.id,
                assignee_id=assignee_id,
                description=desc,
                completed=completed,
                completed_at=completed_at,
                due_date=due_date,
                created_at=created_at
            )
            tasks.append(task)
            
            # 3. COMMENTS FROM POOL
            if random.random() < 0.4:
                story = Story(
                    target_id=task.id,
                    text=random.choice(COMMENTS_POOL),
                    created_by=random.choice(possible_assignees).id if possible_assignees else users[0].id,
                    created_at=random_date_in_range(created_at, datetime.now())
                )
                stories.append(story)

    return tasks, stories