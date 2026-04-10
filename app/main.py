from app.core.orchestrator import multi_agent_system

if __name__ == "__main__":
    query = input("Enter your query: ")
    
    result = multi_agent_system(query)
    
    print("\n--- RESEARCH ---\n")
    print(result["research"])
    
    print("\n--- SUMMARY ---\n")
    print(result["summary"])
    
    print("\n--- PLAN ---\n")
    print(result["plan"])



# python -m app.main     root folder to run karna means multi agent ai system