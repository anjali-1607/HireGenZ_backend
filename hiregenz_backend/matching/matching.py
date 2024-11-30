from .utils import preprocess_text, calculate_similarity, match_salary, match_locations

def match_candidate_to_job(candidate, job):
    # Preprocess and parse data
    candidate_skills = preprocess_text(candidate.skills).split(", ")
    job_skills = preprocess_text(job.skills).split(", ")

    candidate_certifications = preprocess_text(candidate.certifications).split(", ") if candidate.certifications else []
    job_certifications = preprocess_text(job.certifications).split(", ") if job.certifications else []

    candidate_education = preprocess_text(candidate.education).split(", ")
    job_education = preprocess_text(job.education).split(", ")

    candidate_work_experience = candidate.work_experience  # Optional: Parse into years
    job_work_experience = job.work_experience  # Optional: Parse into years

    preference = candidate.preference

    # Calculate scores
    skills_score = calculate_similarity(candidate_skills, job_skills)
    certification_score = calculate_similarity(candidate_certifications, job_certifications)
    education_score = calculate_similarity(candidate_education, job_education)
    
    salary_score = match_salary(
        preference.expected_salary_min,
        preference.expected_salary_max,
        job.offered_salary_min,
        job.offered_salary_max
    )
    location_score = match_locations(preference.preferred_locations, job.locations)

    # Weighted aggregation of scores
    final_score = (
        0.4 * skills_score +
        0.2 * certification_score +
        0.2 * education_score +
        0.1 * salary_score +
        0.1 * location_score
    )

    return final_score
