# Conceptual Code: Hierarchical Research Task
import os
from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools import google_search
import loguru
from .function_tools import html_to_pdf

# User interacts with ReportWriter.
# ReportWriter calls ResearchAssistant tool.
# ResearchAssistant calls WebSearch and Summarizer tools.
# Results flow back up.

current_directory = os.path.dirname(os.path.abspath(__file__))
loguru.logger.add(os.path.join(current_directory, "research_agent.log"), rotation="10 MB", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

# --- Define the Callback Function ---
def simple_before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    print(f"[Callback] Before model call for agent: {agent_name}")

    # Inspect the last user message in the request contents
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[Callback] Inspecting last user message: '{last_user_message}'")

    loguru.logger.info(f"[Callback] Before model call for agent: {agent_name}: {last_user_message}")


# Low-level tool-like agents
web_searcher = LlmAgent(
    name="WebSearch",
    model="gemini-2.0-flash",
    tools=[google_search],
    instruction="Perform a web search for the given topic and return the results.",
    description="Performs web searches for facts.",
    before_model_callback=simple_before_model_modifier,
)

summarizer = LlmAgent(
    name="Summarizer",
    model="gemini-2.0-flash",
    description="Summarizes text.",
    # instruction="Review the information provided to you and break it down into sub-topics of interest." \
    # "Return a properly formatted concise document with headings and sub-headings. Do not omit any information." \
    # "Remove duplications and redundancies and irrelevant data. ",
    instruction="Provide a detailed document organizing the information given to you." \
    "Remove duplications and redundancies",
    before_model_callback=simple_before_model_modifier,
)

# Mid-level agents combining tools
pdf_generator = LlmAgent(
    name="PDFGenerator",
    model="gemini-2.0-flash",
    description="Generates PDF files.",
    instruction="Use the html_to_pdf tool to generate PDF, provide the tool with HTML formatted content and an appropriate filename",
    tools=[html_to_pdf],
    before_model_callback=simple_before_model_modifier,
)

research_assistant = LlmAgent(
    name="ResearchAssistant",
    model="gemini-2.0-flash",
    description="Finds and summarizes information on a topic.",
    instruction="Given a research topic, think about possible sources for information. " \
    "For example: news, medical journals, business publications, websites specific to the topic." \
    "Always use the WebSearch to retrieve information from each possible source." \
    "When the information gathering is completed, use the Summarizer to summarize the information.",
    tools=[
        agent_tool.AgentTool(agent=web_searcher),
        agent_tool.AgentTool(agent=summarizer),
    ],
    before_model_callback=simple_before_model_modifier,
)

# High-level agent delegating research
root_agent = LlmAgent(
    name="ReportWriter",
    model="gemini-2.0-flash",
    instruction="Write a report on topic X. Use the ResearchAssistant to gather information." \
    "If the user query requires any disambiguation, seek clarification. " \
    "When completed, ask the user if a PDF file generation is desired." ,
    sub_agents=[research_assistant, pdf_generator],
)
