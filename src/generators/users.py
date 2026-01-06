import random
import logging
from faker import Faker
from datetime import datetime, timedelta
from typing import List, Tuple
from src.models.models import User, Team, Workspace, TeamMembership
from src.config import NUM_USERS, START_DATE_OFFSET_DAYS
from src.utils.dates import random_date_in_range

fake = Faker()

DEPARTMENTS = ["Engineering", "Product", "Design", "Marketing", "Sales", "Operations"]
ROLES = ["Admin", "Member", "Guest"]

def generate_workspace() -> Workspace:
    company = fake.company()
    domain = fake.domain_name()
    return Workspace(name=company, domain=domain)

def generate_users(workspace_id: str, count: int = NUM_USERS) -> List[User]:
    logging.info(f"Generating {count} Users...")
    users = []
    seen_emails = set()
    
    logging.info(f"Generating {count} Users...")
    users = []
    
    for i in range(count):
        profile = fake.simple_profile()
        # Guarantee uniqueness via counter
        username = profile['username']
        domain = fake.domain_name()
        email = f"{username}.{i}@{domain}"
        
        dept = random.choices(DEPARTMENTS, weights=[30, 15, 10, 20, 15, 10])[0]
        role = random.choices(ROLES, weights=[5, 90, 5])[0]
        
        if i % 1000 == 0:
            logging.info(f"Generated {i} users...")
            
        user = User(
            email=email,
            name=profile['name'],
            workspace_id=workspace_id,
            department=dept,
            role=role,
            avatar_url=f"https://ui-avatars.com/api/?name={profile['name'].replace(' ', '+')}",
            joined_at=random_date_in_range(datetime.now() - timedelta(days=START_DATE_OFFSET_DAYS), datetime.now())
        )
        users.append(user)
    return users

def generate_teams(workspace_id: str, users: List[User]) -> Tuple[List[Team], List[TeamMembership]]:
    teams = []
    memberships = []
    
    # Create one team per department
    dept_teams = {}
    for dept in DEPARTMENTS:
        team = Team(
            name=f"{dept} Team",
            workspace_id=workspace_id,
            description=f"The {dept} department team."
        )
        teams.append(team)
        dept_teams[dept] = team
        
        # Add users to their department team
        dept_users = [u for u in users if u.department == dept]
        for user in dept_users:
            memberships.append(TeamMembership(user_id=user.id, team_id=team.id))
            
    # --- SCALING: Generate Squads (Small Teams) ---
    # Aim for ~10 users per squad to act as project units.
    # Total squads approx len(users) / 10
    logging.info("Generating Squads (Scaling Teams)...")
    squad_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa", "Phoenix", "Dragon", "Tiger", "Eagle", "Lion", "Wolf", "Bear", "Shark", "Whale", "Dolphin"]
    
    for dept in DEPARTMENTS:
        d_users = [u for u in users if u.department == dept]
        # Shuffle
        random.shuffle(d_users)
        
        # Chunk into squads of 5-15
        i = 0
        squad_idx = 1
        while i < len(d_users):
            squad_size = random.randint(5, 15)
            chunk = d_users[i : i + squad_size]
            i += squad_size
            
            if not chunk:
                break
                
            s_name = f"{dept} Squad {squad_idx}"
            if squad_idx <= len(squad_names):
                s_name = f"{dept} {squad_names[squad_idx-1]}"
                
            team = Team(
                name=s_name,
                workspace_id=workspace_id,
                description=f"Squad within {dept}"
            )
            teams.append(team)
            
            for u in chunk:
                 memberships.append(TeamMembership(user_id=u.id, team_id=team.id))
            
            squad_idx += 1

    return teams, memberships
