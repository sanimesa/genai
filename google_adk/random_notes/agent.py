from datetime import datetime
from google.adk.tools.toolbox_tool import ToolboxTool
from google.adk.agents import LlmAgent

toolbox = ToolboxTool("http://127.0.0.1:5000")

# Load a specific set of tools
tools = toolbox.get_toolset(toolset_name='note-management-toolset')

# Load single tool
search_notes_tool = toolbox.get_tool(tool_name='search-notes-by-status')

current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

root_agent = LlmAgent(
    name="NotesManager",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant who helps the user in taking random notes." \
    "The current date is " + current_date + "." \
    "These notes could be categorized as ideas, reminders, meeting notes, personal notes etc. " \
    "You may need to perform multiple searches and ask user for clarifications.",
    tools=tools,
)
