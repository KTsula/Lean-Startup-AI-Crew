from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from typing import List, Dict
import json

class OrchestratorAgent:
    def __init__(self):
        self.tools = [SerperDevTool()]
        self.agent = Agent(
            role='Startup Methodology Orchestrator',
            goal='Guide the startup process following Lean Methodology principles',
            backstory="""You are an expert startup advisor with vast experience in 
            applying the Lean Startup methodology. You excel at identifying the right 
            steps to validate business ideas and help entrepreneurs avoid common pitfalls.
            You always think step by step and explain your reasoning clearly.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools
        )

    def create_initial_tasks(self, idea_type: str, description: str) -> list:
        """Create initial tasks based on the provided idea type and description."""
        analysis_task = Task(
            description=f"""Analyze the provided {idea_type} following the Lean Startup methodology.
            Idea: {description}

            Follow this process exactly:

            1. First, explain your initial thoughts about this idea. Format as:
               INITIAL THOUGHTS: <your thoughts>

            2. Then, list and explain key assumptions that need validation. For each:
               ASSUMPTION: <assumption>
               REASONING: <why this needs validation>

            3. Identify potential risks and challenges. For each:
               RISK: <risk description>
               POTENTIAL IMPACT: <impact explanation>

            4. List specific next steps based on Lean Startup methodology:
               NEXT STEPS:
               1. <step>
               2. <step>
               ...

            5. Specify what needs to be validated through customer interviews/testing:
               VALIDATION NEEDED: <what to validate>
               METHOD: <how to validate>

            6. Finally, outline initial Business Model Canvas elements:
               BMC ELEMENT - <element name>: <description>

            7. End your analysis with a structured JSON summary following this EXACT format:
               {{
                   "key_assumptions": [
                       {{"assumption": "...", "reasoning": "..."}}
                   ],
                   "risks_and_challenges": [
                       {{"risk": "...", "impact": "..."}}
                   ],
                   "next_steps": ["..."],
                   "validations_needed": [
                       {{"validation": "...", "method": "..."}}
                   ],
                   "bmc_elements": {{
                       "value_proposition": "...",
                       "customer_segments": "...",
                       "channels": "...",
                       "customer_relationships": "...",
                       "revenue_streams": "...",
                       "key_resources": "...",
                       "key_activities": "...",
                       "key_partners": "...",
                       "cost_structure": "..."
                   }}
               }}

            Make sure to follow ALL steps and maintain the exact format specified above.
            For the JSON summary, use proper JSON formatting with correct quotes and escaping.
            """,
            expected_output="A detailed analysis showing your thought process and a final JSON summary",
            agent=self.agent
        )

        return [analysis_task]

    def get_crew(self, tasks: list) -> Crew:
        """Create a crew with the orchestrator agent and specified tasks."""
        return Crew(
            agents=[self.agent],
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )