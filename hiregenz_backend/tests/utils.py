import openai
from django.conf import settings

# Use the API key from settings
openai.api_key = settings.OPENAI_API_KEY

def generate_mcqs(job_description):
    prompt = f"""
    Generate 5 multiple-choice questions based on the following job description:
    {job_description}
    Each question should have 4 options with one correct answer. Provide the output in JSON format like this:
    [
        {{
            "question": "What is Python?",
            "options": ["A programming language", "A snake", "A car", "A drink"],
            "answer": "A programming language"
        }}
    ]
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}]
    )
    return eval(response['choices'][0]['message']['content'])  # Parse JSON response
