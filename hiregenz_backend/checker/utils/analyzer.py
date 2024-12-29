import spacy
import re
from textstat import flesch_reading_ease

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# List of stopwords from spaCy
stop_words = nlp.Defaults.stop_words


def analyze_resume(content):
    """
    Analyze the resume for key sections and completeness.
    This function ensures all sections are extracted, even if they are empty.
    """
    # Extract sections from the resume content
    sections = {
        "contact_info": extract_contact_info(content),
        "professional_summary": extract_section(content, "Summary"),
        "skills": extract_section(content, "Skills"),
        "education": extract_section(content, "Education"),
        "work_experience": extract_section(content, "Experience"),
        "certifications": extract_section(content, "Certifications"),
        "languages": extract_section(content, "Languages"),
        "projects": extract_section(content, "Projects")
    }
    # Ensure all sections return meaningful data (even if empty)
    for section in sections:
        if not sections[section]:  # If the section is empty
            sections[section] = "No content found"  # Placeholder for empty sections

    return sections


def extract_contact_info(content):
    """
    Extract contact information such as email, phone numbers, and social media links.
    If no data is found, return placeholders.
    """
    # Refined regex for email
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    # Improved regex for phone numbers (handles international and common formats)
    phone_pattern = (
        r"\+?"                 # Optional '+' for international numbers
        r"(?:\d{1,3})?"         # Country code (1-3 digits)
        r"[-.\s]?"              # Separator (dash, dot, or space)
        r"\(?\d{2,4}\)?"       # Area code (2-4 digits), optionally in parentheses
        r"[-.\s]?"              # Separator
        r"\d{3,4}"              # Central office code (3-4 digits)
        r"[-.\s]?"              # Separator
        r"\d{4}"                # Line number (4 digits)
    )

    # Refined regex for social media links (e.g., LinkedIn, GitHub)
    social_pattern = (
        r"(https?://)?"          # Optional http/https prefix
        r"(www\.)?"             # Optional 'www.'
        r"([a-zA-Z0-9_-]+)"      # Domain name (e.g., linkedin, github)
        r"\.(com|org|net|edu|io)"  # Top-level domain
    )

    # Extract emails, phone numbers, and social links
    emails = re.findall(email_pattern, content)
    phones = re.findall(phone_pattern, content)
    social_links = [".".join(match) for match in re.findall(social_pattern, content)]

    # If no content is found, return placeholders
    if not emails:
        emails = None
    if not phones:
        phones = None
    if not social_links:
        social_links = None

    return {
        "emails": emails,
        "phones": phones,
        "social_links": social_links
    }


def extract_section(content, section_name):
    """
    Extract content for a specific section (e.g., Skills, Education, Work Experience).
    If no content is found, return an empty string.
    """
    section_pattern = r"(?<=\b" + re.escape(section_name) + r"\b)(.*?)(?=\n[A-Z])"
    matches = re.findall(section_pattern, content, re.DOTALL | re.IGNORECASE) 
    # If no content is found, return an empty string
    return matches[0] if matches else ""


def calculate_formatting(content):
    """
    Calculate a dynamic formatting score based on:
    - Presence of clear section headings
    - Use of bullet points or list items
    - Overall structure and clarity
    """
    # Define patterns for identifying common resume sections
    headings = re.findall(r"\b(Experience|Education|Skills|Summary|Projects|Certifications|Languages)\b", content, re.IGNORECASE)
    bullet_points = re.findall(r"^\s*[-*•]\s+", content, re.MULTILINE)  # Bullets: dash, asterisk, or circle

    # Section presence: The more sections, the better the format
    section_score = len(set(headings))  # Score based on unique sections

    # Bullet point score: More bullet points generally mean better formatting
    bullet_score = len(bullet_points) * 0.2  # Weight bullets by 0.2 for scoring

    # Overall formatting score: Combine the section score and bullet score
    total_score = section_score + bullet_score
    return min(total_score, 10)  # Cap the score at 10 for simplicity


def score_resume(content):
    """
    Score the resume based on formatting, readability, and content quality.
    """
    # Use spaCy to process the content
    doc = nlp(content)

    # Tokenize text (spaCy's tokenization)
    tokens = [token.text for token in doc]
    num_words = len(tokens)

    # Calculate readability using textstat
    readability = flesch_reading_ease(content)

    # Calculate content quality score (unique words)
    unique_words = len(set(tokens))

    # Calculate keywords (non-stopwords)
    keywords = [word for word in tokens if word.lower() not in stop_words]

    # Get the dynamic formatting score
    formatting_score = calculate_formatting(content)

    return {
        "formatting": formatting_score,  # Dynamic formatting score
        "content_quality": unique_words / num_words * 10 if num_words else 0,
        "keywords": len(keywords),
        "readability": readability
    }
