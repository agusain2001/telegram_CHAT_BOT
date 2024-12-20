from typing import List, Dict

def generate_keywords(data: Dict[str, str]) -> List[str]:
    """
    Generates marketing keywords based on user data.
    """
    industry = data.get("industry", "General")
    objective = data.get("objective", "Marketing")
    audience = data.get("audience", "Audience")
    
    # Ensure all inputs are strings and capitalize for consistency
    industry = industry.capitalize()
    objective = objective.capitalize()
    audience = audience.capitalize()
    
    return [
        f"{industry} marketing",
        f"{objective} strategy",
        f"{audience} engagement",
        f"{industry} trends",
        f"{audience} outreach"
    ]
