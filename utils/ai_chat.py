import os
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

def get_openai_client():
    """Get OpenAI client instance"""
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=OPENAI_API_KEY)


def get_chat_response(messages, assessment_context=None):
    """
    Get a response from the AI assistant
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        assessment_context: Optional dictionary with assessment results to provide context
    
    Returns:
        str: AI assistant's response
    """
    # Build system message with assessment context if provided
    system_message = {
        "role": "system",
        "content": "You are a helpful AI assistant specializing in AI process readiness and organizational transformation. "
        "You help users understand their assessment results and provide guidance on improving their AI readiness."
    }
    
    if assessment_context:
        context_text = "\n\nCurrent Assessment Context:\n"
        context_text += f"- Overall Score: {assessment_context.get('total_score', 'N/A')}/30\n"
        context_text += f"- Readiness Level: {assessment_context.get('readiness_band', 'N/A')}\n"
        context_text += "\nDimension Scores:\n"
        
        for dim in assessment_context.get('dimension_scores', []):
            context_text += f"- {dim['title']}: {dim['score']}/5\n"
        
        system_message["content"] += context_text
    
    # Combine system message with user messages
    all_messages = [system_message] + messages
    
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-5",
            messages=all_messages,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except ValueError as e:
        # API key not configured
        return "The AI assistant is not configured. Please ensure your OpenAI API key is set in the environment variables."
    except Exception as e:
        # Log the error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"OpenAI API Error: {error_details}")
        
        # Check for common error types
        error_msg = str(e).lower()
        if "api_key" in error_msg or "authentication" in error_msg:
            return "There's an issue with the API key authentication. Please check that your OpenAI API key is valid and properly configured."
        elif "quota" in error_msg or "insufficient" in error_msg:
            return "The OpenAI API quota has been exceeded. Please check your OpenAI account usage and billing settings."
        elif "rate" in error_msg or "limit" in error_msg:
            return "Too many requests to the AI service. Please wait a moment and try again."
        else:
            return f"I'm having trouble connecting to the AI service right now. Please try again in a moment. If the issue persists, contact support with this error: {str(e)[:100]}"


def get_assessment_insights(scores_data):
    """
    Get AI-generated insights about the assessment results
    
    Args:
        scores_data: Dictionary containing assessment scores
    
    Returns:
        str: AI-generated insights
    """
    context = {
        "total_score": scores_data['total'],
        "readiness_band": scores_data['readiness_band']['label'],
        "dimension_scores": scores_data['dimension_scores']
    }
    
    prompt = f"""Based on this AI Process Readiness Assessment:
    
Overall Score: {scores_data['total']}/30 ({scores_data['percentage']}%)
Readiness Level: {scores_data['readiness_band']['label']}

Dimension Scores:
"""
    
    for dim in scores_data['dimension_scores']:
        prompt += f"- {dim['title']}: {dim['score']}/5\n"
    
    prompt += "\nProvide a brief, actionable summary (2-3 paragraphs) highlighting the key strengths, areas for improvement, and recommended next steps."
    
    messages = [{"role": "user", "content": prompt}]
    
    return get_chat_response(messages, context)
