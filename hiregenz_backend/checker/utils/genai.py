import google.generativeai as genai
from django.conf import settings

# Configure the Google Generative AI API key
genai.configure(api_key=settings.GOOGLE_API_KEY)


def generate_feedback(content):
    """
    Use Google Generative AI to generate resume improvement suggestions.
    """
    prompt = f"""
    Analyze the following resume content. Provide:
    - Suggestions for improving readability and formatting.
    - Missing keywords.
    - Suggestions for better action-oriented phrasing.
    Resume Content:
    {content}
    please make sure feedback should be in short 3-4 lines and in easy language not long more than that also should give clear feedback that what percent have chance to that your resume my short listed in the companies..
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    return response.text  # Return the generated text feedback
