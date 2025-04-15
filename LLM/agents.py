from LLM.generate_resume_prompt import build_resume_prompt
from langgraph.graph import StateGraph
from langchain_core.runnables import Runnable, RunnableConfig
from typing import TypedDict
import json
import os
from fastapi import  HTTPException
from dotenv import load_dotenv

from schemas import ResumeCreate
load_dotenv() 

import google.generativeai as genai
GEMINI_API_TOKEN = os.getenv("GEMINI_API_TOKEN")
if not GEMINI_API_TOKEN:
    raise ValueError("GEMINI_API_TOKEN environment variable not set")
genai.configure(api_key=GEMINI_API_TOKEN)

class ResumeState(TypedDict):
    profile_data: dict
    job_description: str
    generated_resume: dict
    score: int
    attempts: int

def query_to_llm(prompt: str) -> str:
    """Helper function to query the Gemini API for chat completions."""
    model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Or 'gemini-pro-vision' for multimodal

    try:
        response = model.generate_content(prompt)
        

        # The text output is directly accessible
        generated_text = response.text.strip()
        print(generated_text)
        return generated_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API call failed: {str(e)}")



# Generator node
def generator_agent(state: ResumeState) -> ResumeState:
    prompt = build_resume_prompt(state["profile_data"], state["job_description"])
    resume_json = query_to_llm(prompt)
    try:
        resume_json = resume_json.replace("```json", "").replace("```", "")
        resume_data = json.loads(resume_json)
    except json.JSONDecodeError:
        raise Exception("Invalid resume JSON")
    return {**state, "generated_resume": resume_data}

# Evaluator node
def evaluator_agent(state: ResumeState) -> ResumeState:
    resume = state["generated_resume"]
    job_desc = state["job_description"]

    eval_prompt = (
    "You are an ATS evaluation assistant. Your task is to assess the following resume for its compatibility with Applicant Tracking Systems (ATS) and how well it aligns with the job description.\n\n"
    f"Resume:\n{json.dumps(resume, indent=2)}\n\n"
    f"Job Description:\n{job_desc}\n\n"
    "Evaluate based on these ATS criteria:\n"
    "- **Keywords:** Does the resume include relevant keywords and skills from the job description?\n"
    "- **Contact Information:** Are the contact details clear and easily parsable?\n"
    "- **Conciseness:** Are there overly long or dense text blocks?\n"
    "- **Grammar and Spelling:** Are there any errors that might confuse the system?\n\n"
    "Give a score from 0 to 100 based on ATS compatibility and alignment with the job description (relevance, tailoring, and keyword alignment).\n\n"
    "**Important: Only respond with a valid JSON object in the exact format below — no extra explanation, no comments, no markdown.**\n\n"
    "Example:\n"
    "{ \"score\": 85 }\n\n"
    "Now, return the score JSON for this evaluation:"
)


    eval_response = query_to_llm(eval_prompt)
    # print(f"-----{eval_response}--------")
    eval_response  = eval_response.replace("```json", "").replace("```", "")
    score = json.loads(eval_response).get("score", 0)
    return {**state, "score": score}

# Router
def router(state: ResumeState) -> str:
    if state["score"] >= 80 or state["attempts"] >= 3:
        return "return_result"
    else:
        state["attempts"] += 1
        return "rewrite_resume"


# Define the LangGraph
graph = StateGraph(ResumeState)
graph.add_node("generate_resume", generator_agent)
graph.add_node("evaluate_resume", evaluator_agent)
graph.add_node("rewrite_resume", generator_agent)  # Add the missing node
graph.add_node("return_result", lambda state: state)  # Terminal node doesn't need processing

graph.add_conditional_edges("evaluate_resume", router)
graph.add_edge("generate_resume", "evaluate_resume")
graph.add_edge("rewrite_resume", "evaluate_resume")  # Correct edge destination
graph.set_entry_point("generate_resume")

resume_graph = graph.compile()
