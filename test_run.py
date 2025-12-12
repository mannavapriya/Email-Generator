"""
test_run.py - test harness for the LangGraph email workflow
"""
from langchain_core.messages import HumanMessage
from workflow.langgraph_flow import run_email_workflow

if __name__ == "__main__":
    prompt = "to: Alice\nI want to write a thank you note for my interviewer. tone: formal"
    print("Prompt:\n", prompt)
    result = run_email_workflow(prompt)
    print("Result:\n", result)
