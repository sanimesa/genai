# ./adk_agent_samples/mcp_agent/agent.py
import os
import asyncio
import contextlib
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters

# Load environment variables from .env file in the parent directory
# Place this near the top, before using env vars like API keys
load_dotenv('../.env')

#get the current directory
current_directory = os.getcwd()
print(f"Current working directory: {current_directory}")

# --- Module-level variables to hold the agent and cleanup stack ---
# These will be populated during the initialization phase
root_agent: LlmAgent | None = None
_exit_stack: contextlib.AsyncExitStack | None = None # Using an underscore as it's intended for internal use

# --- Step 1: Import Tools from MCP Server (Async) ---
async def get_tools_async():
  """Gets tools from the File System MCP Server."""
  print("Attempting to connect to MCP Filesystem server...")
  # Using the current directory as the root for the MCP server
  mcp_root_path = current_directory # Or provide an absolute path if needed
  
  try:
      tools, exit_stack = await MCPToolset.from_server(
          # Use StdioServerParameters for local process communication
          connection_params=StdioServerParameters(
              command='npx', # Command to run the server
              args=["-y",    # Arguments for the command
                    "@modelcontextprotocol/server-filesystem",
                    mcp_root_path], # Use the specified path
          )
          # For remote servers, you would use SseServerParams instead:
          # connection_params=SseServerParams(url="http://remote-server:port/path", headers={...})
      )
      print("MCP Toolset created successfully.")
      # MCP requires maintaining a connection to the local MCP Server.
      # exit_stack manages the cleanup of this connection.
      return tools, exit_stack
  except Exception as e:
      print(f"Error connecting to MCP server: {e}")
      # Depending on your needs, you might want to re-raise, return None, or exit.
      # Returning empty tools but a stack might be problematic if stack expects tools.
      # A safer approach is to raise or return (None, None) and handle it in the caller.
      raise # Re-raise the exception to indicate failure


# --- Step 2: Agent Definition (Async initialization function) ---
async def initialize_agent_async():
  """Initializes the ADK Agent and makes it available at the module level."""
  global root_agent, _exit_stack # Declare intent to modify module-level variables

  if root_agent is not None:
      print("Agent already initialized.")
      return root_agent

  print("Initializing agent...")
  tools, exit_stack = await get_tools_async()
  print(f"Fetched {len(tools)} tools from MCP server.")
  print("Available tools:", list(map(lambda item: item.name, tools)))

  # Create the agent
  agent_instance = LlmAgent(
      model='gemini-2.0-flash', # Adjust model name if needed based on availability
      name='filesystem_assistant',
      instruction='Help user interact with the local filesystem using available tools.',
      tools=tools, # Provide the MCP tools to the ADK agent
  )

  # Assign to module-level variables
  root_agent = agent_instance
  _exit_stack = exit_stack

  print("Agent initialization complete.")
  return root_agent

# --- Cleanup Function ---
async def shutdown_agent_async():
    """Performs cleanup for the agent and its resources (like MCP connection)."""
    global _exit_stack
    if _exit_stack:
        print("Shutting down agent resources (MCP server connection)...")
        try:
            await _exit_stack.aclose()
            print("Cleanup complete.")
        except Exception as e:
            print(f"Error during agent shutdown: {e}")
        finally:
            _exit_stack = None # Ensure stack is marked as closed

# --- Step 3: Main Execution Logic (for CLI testing) ---
async def run_cli_example():
    """Runs a simple example query using the initialized agent (for CLI testing)."""
    # Ensure the agent is initialized first
    await initialize_agent_async()

    if root_agent is None:
        print("Agent failed to initialize. Cannot run CLI example.")
        return

    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService() # Optional

    session = session_service.create_session(
        state={}, app_name='mcp_filesystem_app', user_id='user_fs_cli'
    )

    # TODO: Change the query to be relevant to YOUR specified folder.
    # e.g., "list files in the 'documents' subfolder" or "read the file 'notes.txt'"
    query = f"list files in the folder {current_directory}"
    print(f"User Query (CLI): '{query}'")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    runner = Runner(
        app_name='mcp_filesystem_app',
        agent=root_agent, # Use the module-level agent
        artifact_service=artifacts_service, # Optional
        session_service=session_service,
    )

    print("Running agent (CLI)...")
    try:
        events_async = runner.run_async(
            session_id=session.id, user_id=session.user_id, new_message=content
        )

        async for event in events_async:
          print(f"Event received: {event}")

    except Exception as e:
        print(f"An error occurred during CLI run: {e}")


# --- Command Line Entry Point ---
if __name__ == '__main__':
    # This block now initializes, runs the example, and cleans up.
    # The web UI will NOT run this block.
    try:
        print("Running agent script from CLI...")
        asyncio.run(run_cli_example())
    except Exception as e:
        print(f"An error occurred during script execution: {e}")
    finally:
        # Ensure cleanup happens even if the CLI example fails after init
        # asyncio.run cannot directly run awaited shutdown_agent_async
        # in its finally block if the loop is already closed.
        # A more robust approach for CLI shutdown would be needed if not exiting
        # immediately, but for a simple script like this, it's often acceptable
        # to let resources potentially linger if the script crashes *after* the run_cli_example call.
        # For proper async shutdown in CLI, you'd need a separate loop context or run it differently.
        # However, the primary goal here is to show web UI integration.
        # The web UI's shutdown hooks will handle this correctly.
        print("CLI script finished.")