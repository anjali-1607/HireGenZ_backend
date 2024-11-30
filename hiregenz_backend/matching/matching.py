from .utils import preprocess_text, calculate_similarity, match_salary, match_locations

from sentence_transformers import SentenceTransformer

# model = SentenceTransformer('all-MiniLM-L6-v2')  # Use a pre-trained model
model = SentenceTransformer('bert-base-nli-mean-tokens')

def match_candidate_to_job(candidate, job):
    # Preprocess and parse data, converting everything to lowercase
    candidate_skills = [
        skill.lower().strip() for skill in preprocess_text(candidate.skills).split(", ")
    ] if candidate.skills else []
    job_skills = [skill.lower().strip() for skill in job.key_skills] if job.key_skills else []

    candidate_certifications = [
        cert.lower().strip() for cert in preprocess_text(candidate.certifications).split(", ")
    ] if candidate.certifications else []
    job_certifications = []  # Adjust if needed (populate if JobPost has a certifications field)

    candidate_education = [
        edu.lower().strip() for edu in preprocess_text(candidate.education).split(", ")
    ] if candidate.education else []
    job_education = [
        edu.lower().strip() for edu in preprocess_text(job.education).split(", ")
    ] if job.education else []

    candidate_work_experience = candidate.work_experience  # Optional: Parse into years
    job_work_experience = job.experience  # Use the `experience` field from JobPost

    preference = getattr(candidate, "preference", None)  # Ensure preference exists

    # Validate if preference exists before accessing its fields
    salary_score = 0
    location_score = 0
    if preference:
        salary_score = match_salary(
            preference.expected_salary_min,
            preference.expected_salary_max,
            job.min_ctc,
            job.max_ctc
        )
        location_score = match_locations(preference.preferred_locations, job.locations)

    # Calculate scores
    skills_score = calculate_similarity(candidate_skills, job_skills, model=model)
    certification_score = calculate_similarity(candidate_certifications, job_certifications, model=model)
    education_score = calculate_similarity(candidate_education, job_education, model=model)

    # Weighted aggregation of scores
    final_score = (
        0.4 * skills_score +
        0.2 * certification_score +
        0.2 * education_score +
        0.1 * salary_score +
        0.1 * location_score
    )

    return final_score
