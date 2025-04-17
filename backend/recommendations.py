import pandas as pd

def calculate_match(user_skills, required_skills):
    total_weight = 0
    matched_weight = 0
    for skill, req_level in required_skills.items():
        if req_level > 0: 
            total_weight += req_level
            user_level = user_skills["hard_skills"].get(skill, 0)
            if user_level >= req_level:
                matched_weight += req_level
            else:
                matched_weight += user_level  
    return round((matched_weight / total_weight) * 100, 1) if total_weight > 0 else 0

def get_recommendations(candidate, db):
    user_skills = db.get_user_skills(candidate["id"])
    roles = db.get_all_roles()
    
    role_matches = {}
    for role in roles:
        required = db.get_skills_matrix(role)
        role_matches[role] = calculate_match(user_skills, required)

    sorted_roles = sorted(role_matches.items(), key=lambda x: x[1], reverse=True)[:4]
    

    all_required = set()
    for role in roles:
        all_required.update(db.get_skills_matrix(role).keys())
    additional = {skill: lvl for skill, lvl in user_skills["hard_skills"].items() if skill not in all_required}
    
    return {
        "roles": [
            {
                "name": role,
                "match_percent": percent,
                "skills": db.get_skills_matrix(role)
            } for role, percent in sorted_roles
        ],
        "additional_skills": additional,
        "soft_skills": user_skills["soft_skills"]
    }