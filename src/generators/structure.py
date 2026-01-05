import random
from typing import List, Tuple
from src.models.models import Project, Section, Team, User
from src.utils.llm import generate_text
from src.utils.dates import random_date_in_range, get_business_day
from src.config import ARCHIVED_PROJECT_RATE, GOOGLE_API_KEY
from datetime import datetime, timedelta

PROJECT_TEMPLATES = {
    "Engineering": ["Core Infrastructure Migration", "API V2 Refactor", "Q3 Bug Bash", "Mobile App Performance Tuning"],
    "Marketing": ["Q4 Brand Campaign", "SEO Optimization", "Social Media Calendar", "Conference Planning"],
    "Product": ["User Research Q2", "Feature Roadmap Planning", "Competitor Analysis"],
    "Design": ["Design System V2", "Website Redesign", "Mobile UI Kit"],
    "Sales": ["Enterprise Lead Gen", "Sales Enablement Deck", "CRM Cleanup"],
    "Operations": ["Office Move", "Quarterly Offsite Planning", "Vendor Review"]
}

SECTIONS_TEMPLATES = {
    "Engineering": ["Backlog", "To Do", "In Progress", "Code Review", "QA", "Done"],
    "Marketing": ["Ideation", "Drafting", "Review", "Approved", "Published"],
    "Standard": ["To Do", "In Progress", "Blocked", "Done"]
}

def generate_projects(workspace_id: str, teams: List[Team], users: List[User]) -> Tuple[List[Project], List[Section]]:
    projects = []
    all_sections = []
    
    # Pre-calculate department map for teams to pick right templates
    # This heuristic assumes team name contains department name
    
    for team in teams:
        # Determine department context
        dept = "Standard"
        for d in PROJECT_TEMPLATES.keys():
            if d.lower() in team.name.lower():
                dept = d
                break
        
        # Decide how many projects this team has
        num_projects = random.randint(2, 5)
        
        for _ in range(num_projects):
            # Pick a name
            if dept != "Standard" and PROJECT_TEMPLATES.get(dept):
                base_name = random.choice(PROJECT_TEMPLATES[dept])
                name = f"{base_name} - {datetime.now().year}" # Avoid duplicate exact names logic later if needed
            else:
                 # Fallback/LLM
                 if GOOGLE_API_KEY:
                     name = generate_text(f"Generate a realistic enterprise project name for a {dept} team.", temperature=0.8).strip().replace('"','')
                 else:
                     name = f"{team.name} Project {random.randint(100, 999)}"

            owner = random.choice(users) # logic could be tighter to pick team member
            
            # Dates
            created_at = random_date_in_range(datetime.now() - timedelta(days=180), datetime.now())
            
            project = Project(
                name=name,
                workspace_id=workspace_id,
                team_id=team.id,
                owner_id=owner.id,
                created_at=created_at,
                archived=(random.random() < ARCHIVED_PROJECT_RATE),
                color=random.choice(["Red", "Green", "Blue", "Yellow", "Orange", "Purple"])
            )
            projects.append(project)
            
            # Sections
            section_names = SECTIONS_TEMPLATES.get(dept, SECTIONS_TEMPLATES["Standard"])
            for idx, s_name in enumerate(section_names):
                section = Section(
                    name=s_name,
                    project_id=project.id,
                    order_index=idx,
                    created_at=created_at
                )
                all_sections.append(section)
                
    return projects, all_sections
