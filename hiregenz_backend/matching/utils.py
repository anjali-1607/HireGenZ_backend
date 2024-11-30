from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load embedding model (reuse across requests)
model = SentenceTransformer('bert-base-nli-mean-tokens')

# Preprocess text
def preprocess_text(text):
    return text.lower().strip()

# Calculate semantic similarity
def calculate_similarity(list1, list2):
    if not list1 or not list2:
        return 0  # No match if either list is empty
    embeddings1 = model.encode(list1, convert_to_tensor=True)
    embeddings2 = model.encode(list2, convert_to_tensor=True)
    similarities = util.cos_sim(embeddings1, embeddings2)
    return np.mean(similarities).item()  # Return average similarity score

# Match salary ranges
def match_salary(expected_min, expected_max, offered_min, offered_max):
    if not (expected_min and expected_max and offered_min and offered_max):
        return 0  # No match if salary details are missing
    # Check for overlap in salary ranges
    return 1 if expected_max >= offered_min and offered_max >= expected_min else 0

# Match locations
def match_locations(candidate_locations, job_locations):
    if not candidate_locations or not job_locations:
        return 0
    return len(set(candidate_locations) & set(job_locations)) > 0
