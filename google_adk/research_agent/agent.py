# Conceptual Code: Hierarchical Research Task
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools import google_search

# Low-level tool-like agents
web_searcher = LlmAgent(name="WebSearch", 
                        model="gemini-2.0-flash", 
                        tools=[google_search], 
                        instruction="Perform a web search for the given topic, prefix your response with'####### WEB SEARCH RESULTS #######' ", 
                        description="Performs web searches for facts.")

summarizer = LlmAgent(name="Summarizer", 
                      model="gemini-2.0-flash", 
                      description="Summarizes text.")

# Mid-level agent combining tools
research_assistant = LlmAgent(
    name="ResearchAssistant",
    model="gemini-2.0-flash",
    description="Finds and summarizes information on a topic.",
    instruction="Given a research topic, prepare a plan with sub-topics of interest. Then provide response combining the information. Always use WebSearch to ground your information",
    tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
)

# High-level agent delegating research
root_agent = LlmAgent(
    name="ReportWriter",
    model="gemini-2.0-flash",
    instruction="Write a report on topic X. Use the ResearchAssistant to gather information.",
    tools=[agent_tool.AgentTool(agent=research_assistant)]
    # Alternatively, could use LLM Transfer if research_assistant is a sub_agent
)
# User interacts with ReportWriter.
# ReportWriter calls ResearchAssistant tool.
# ResearchAssistant calls WebSearch and Summarizer tools.
# Results flow back up.