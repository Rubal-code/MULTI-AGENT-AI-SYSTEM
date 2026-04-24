from app.core.llm import get_llm
llm = get_llm()

def planner_agent(text):

    prompt = f"""
    Create a COMPLETE and STRUCTURED roadmap.

    STRICT RULES:
    - Minimum 5 phases
    - Each phase must include:
        • Topics
        • Skills
        • Tools
    - No "Day 1 / Week 1"
    - Do NOT shorten output
    - Make it practical

    FORMAT:

    Phase 1: Title
    - Topics:
    - Skills:
    - Tools:

    Continue properly...

    Content:
    {text}
    """

    return llm.invoke(prompt)