from LLM.generate_resume_prompt import build_resume_prompt
from langgraph.graph import StateGraph
from langchain_core.runnables import Runnable, RunnableConfig
from typing import TypedDict
import json
import os
from fastapi import  HTTPException
from dotenv import load_dotenv

from LLM.load_prompt import load_prompt
from LLM.utils import get_prompt
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
    hr_key_points: dict
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

def hr_specialist_agent(state: ResumeState) -> ResumeState:
    job_desc = state["job_description"]

    hr_prompt = load_prompt(prompt_file= get_prompt("agents.yaml"),
                            prompt_key='hr_prompt',
                            job_desc=job_desc)

    hr_response = query_to_llm(hr_prompt)
    hr_response = hr_response.replace("```json", "").replace("```", "")

    try:
        key_points = json.loads(hr_response)
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON from HR agent: {str(e)}\nResponse was: {hr_response}")

    return {**state, "hr_key_points": key_points}


# Generator node
def generator_agent(state: ResumeState) -> ResumeState:
    prompt = build_resume_prompt(state["profile_data"], state["hr_key_points"])
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

    eval_prompt = load_prompt(prompt_file= get_prompt("agents.yaml"),
                            prompt_key='eval_prompt',
                            job_desc=job_desc,
                            resume = json.dumps(resume, indent=2)
                            )


    eval_response = query_to_llm(eval_prompt)
    # print(f"-----{eval_response}--------")
    eval_response  = eval_response.replace("```json", "").replace("```", "")
    score = json.loads(eval_response).get("score", 0)
    return {**state, "score": score}

# Router
def router(state: ResumeState) -> str:
    if state["score"] >= 70 or state["attempts"] >= 3:
        return "return_result"
    else:
        state["attempts"] += 1
        return "rewrite_resume"


# Define the LangGraph
graph = StateGraph(ResumeState)

graph.add_node("extract_key_points", hr_specialist_agent)
graph.add_node("generate_resume", generator_agent)
graph.add_node("evaluate_resume", evaluator_agent)
graph.add_node("rewrite_resume", generator_agent)
graph.add_node("return_result", lambda state: state)

graph.add_edge("extract_key_points", "generate_resume")
graph.add_edge("generate_resume", "evaluate_resume")
graph.add_edge("rewrite_resume", "evaluate_resume")

graph.add_conditional_edges("evaluate_resume", router)

graph.set_entry_point("extract_key_points")

resume_graph = graph.compile()

