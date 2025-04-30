from google.adk.tools.toolbox_tool import ToolboxTool
from google.adk.agents import LlmAgent

toolbox = ToolboxTool("https://127.0.0.1:5000")

# Load a specific set of tools
tools = toolbox.get_toolset(toolset_name='my-toolset-name'),
# Load single tool
tools = toolbox.get_tool (tool_name='my-tool-name'),

root_agent = LlmAgent(
    name="NotesManager",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant who helps the user in taking random notes." \
    "These notes could be ideas, reminders, meeting notes, etc. ",
    tools=[research_assistant, pdf_generator],
)
