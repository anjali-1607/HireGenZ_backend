import google.generativeai as genai
from django.conf import settings

# Configure the Google Generative AI API key
genai.configure(api_key=settings.GOOGLE_API_KEY)


def generate_feedback(content):
    """
    Use Google Generative AI to generate resume improvement suggestions.
    """
    prompt = f"""
    Analyze the resume content provided below and give clear, actionable feedback. Your analysis should include:

1. Suggestions to improve readability and formatting.  
2. Identification of missing keywords relevant to job applications.  
3. Tips for using better action-oriented language in bullet points.  
4. Feedback presented in 5 clear points, using simple and easy-to-understand language.  
5. A percentage estimate of the resume’s likelihood of being shortlisted by companies.  
6. An "Overall Result" score between 0-10 based on the quality of the resume.
Resume Content:  
{content}

    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    return response.text  # Return the generated text feedback
