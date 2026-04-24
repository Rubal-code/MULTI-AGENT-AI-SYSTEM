from app.core.llm import get_llm
llm = get_llm()

def summarizer_agent(text, style="brief"):

    if style == "brief":
        prompt = f"""
        Summarize this in 2-3 lines in simple language.

        {text}
        """
    else:
        prompt = f"""
        Explain clearly:
        - Definition
        - Key points
        - Example

        {text}
        """

    return llm.invoke(prompt)