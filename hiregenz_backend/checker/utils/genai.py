import google.generativeai as genai
from django.conf import settings
import json

# Configure the Google Generative AI API key
genai.configure(api_key=settings.GOOGLE_API_KEY)


def generate_feedback(content):
    """
    Use Google Generative AI to generate resume improvement suggestions in JSON format.
    """
    prompt = f"""
    Analyze the resume content provided below and give feedback in the following JSON format:

    {{
      "short_summary": "",  // A brief summary of the resume's overall impression.
      "action_points": [
        "", "", "", "", ""  // Five actionable suggestions for improving the resume.
      ],
      "overall_quality": "", // The quality of the resume (poor, average, excellent, or outstanding).
      "chance_get_selected": "" // The likelihood of the resume being shortlisted, ranked out of 100.
    }}

    Ensure the feedback is clear, concise, and actionable, while adhering to this exact format.

    Resume Content:  
    {content}
    """

    # Initialize the generative model
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    # Generate the response
    response = model.generate_content(prompt)

    try:
        # Remove code block markers and clean up the response
        cleaned_response = (
            response.text.replace("```json", "")
            .replace("```", "")
            .strip()
        )
        
        # Parse the cleaned response into JSON
        feedback_json = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        # Handle invalid JSON format and return detailed error info
        feedback_json = {
            "error": "Invalid JSON format in the response",
            "raw_response": response.text,
            "exception": str(e)
        }
    
    return feedback_json
