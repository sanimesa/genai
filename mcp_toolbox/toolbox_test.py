from google.adk.tools.toolbox_tool import ToolboxTool
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

toolbox = ToolboxTool("http://127.0.0.1:5000")

APP_NAME="hotel_agent"
USER_ID="user1234"
SESSION_ID="1234"


# Load a specific set of tools
tools = toolbox.get_toolset(toolset_name='note-management-toolset'),
print(type(tools))
print(tools)

# Load single tool
tool = toolbox.get_tool(tool_name='search-notes-by-status')

root_agent = Agent(
    name="notes_manager",
    model="gemini-2.0-flash",
    description=(
        "An agent that helps with notes management."
    ),
    instruction=(
        "You are a helpful agent who can manage notes for a user."
    ),
    tools=[tool] # Provide the list of tools to the Agent
)


# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


# Agent Interaction
def call_agent(query):
    """
    Helper function to call the agent with a query.
    """
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            print(event.content.parts)
            final_response = event.content.parts[0].text

            print("Agent Response: ", final_response)

call_agent("Can you list all open entries?")