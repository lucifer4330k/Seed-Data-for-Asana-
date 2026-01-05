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
    for dept in DEPARTMENTS:
        team = Team(
            name=f"{dept} Team",
            workspace_id=workspace_id,
            description=f"The {dept} department team."
        )
        teams.append(team)
        
        # Add users to their department team
        dept_users = [u for u in users if u.department == dept]
        for user in dept_users:
            memberships.append(TeamMembership(user_id=user.id, team_id=team.id))
            
    # thorough cross-functional teams
    cross_functional_teams = ["Growth Squad", "Mobile App Launch", "Enterprise Security"]
    for t_name in cross_functional_teams:
        team = Team(name=t_name, workspace_id=workspace_id, description="Cross-functional project team")
        teams.append(team)
        # Add random users
        squad_size = random.randint(5, 15)
        squad_users = random.sample(users, k=min(len(users), squad_size))
        for user in squad_users:
             memberships.append(TeamMembership(user_id=user.id, team_id=team.id))

    return teams, memberships
