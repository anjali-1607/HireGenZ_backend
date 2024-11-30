import openai

openai.api_key = "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"

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
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return eval(response['choices'][0]['message']['content'])  # Parse JSON response
