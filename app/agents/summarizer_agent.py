from app.core.llm import get_llm

llm = get_llm()

def summarizer_agent(text, user_query):
    prompt = f"""
    User asked: {user_query}

    Based on the above request, respond appropriately:

    - If user asks for brief/short → give concise answer
    - If user asks for detailed → give detailed explanation
    - If unclear → give balanced response

    Content:
    {text}
    """
    
    return llm.invoke(prompt)