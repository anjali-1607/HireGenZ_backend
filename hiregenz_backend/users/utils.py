import re
import spacy

# Preload SpaCy model
nlp = spacy.load("en_core_web_sm")

SKILL_KEYWORDS = [
    "Python", "Java", "C++", "SQL", "JavaScript", "React", "Angular", "Node.js", "HTML", "CSS",
    "Docker", "Kubernetes", "AWS", "Azure", "Data Analysis", "Machine Learning", "Deep Learning",
    "AI", "DevOps", "TensorFlow", "Pandas", "NumPy", "Scikit-learn", "Excel", "Tableau", "Power BI",
    "Git", "Jenkins", "RESTful APIs", "Flask", "Django", "PostgreSQL", "MongoDB", "GraphQL", "Tailwind CSS"
]

def extract_email(text):
    """Extract email from text using regex."""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None

def extract_phone(text):
    """Extract phone number from text using regex."""
    match = re.search(r'\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{4,10}', text)
    return match.group(0) if match else None

def extract_name(text):
    """Extract name from the first few lines using heuristics."""
    lines = text.splitlines()[:5]
    for line in lines:
        if re.match(r'^[A-Z][a-z]+\s[A-Z][a-z]+$', line.strip()):  # Matches "First Last"
            return line.strip()
    return None

def extract_skills(text):
    """Extract skills using predefined keywords."""
    doc = nlp(text)
    skills = {token.text for token in doc if token.text in SKILL_KEYWORDS}
    return list(skills)

def extract_section(text, heading):
    """Extract specific sections like certifications or summary."""
    pattern = rf"{heading}.*?(?=\n[A-Z\s]+:|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(0).strip() if match else None

def extract_resume_data(text):
    """Extract structured data from resume text."""
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "certifications": extract_section(text, "CERTIFICATIONS"),
        "education": extract_section(text, "EDUCATION"),
        "work_experience": extract_section(text, "WORK EXPERIENCE"),
        "professional_summary": extract_section(text, "SUMMARY"),
    }
