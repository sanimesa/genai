import asyncio
from google.adk.agents import LlmAgent, Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.tools import built_in_code_execution
from google.adk.code_executors.unsafe_local_code_executor import UnsafeLocalCodeExecutor
from google.genai import types

try:
    # For external imports (when part of the package)
    from .custom_unsafe_local_code_executor import CustomUnsafeLocalCodeExecutor
except ImportError:
    # For direct execution (fallback)
    from custom_unsafe_local_code_executor import CustomUnsafeLocalCodeExecutor

# Constants

CODING_AGENT_NAME="coding_agent"
ROOT_AGENT_NAME="customer_service_agent"
APP_NAME="data_analyzer"
USER_ID="user1234"
SESSION_ID="session_code_exec_async"
GEMINI_MODEL = "gemini-2.0-flash"
# GEMINI_MODEL = "gemini-2.5-flash-preview-04-17"

#load an excel file as a pandas dataframe
import pandas as pd

#load a file called data\vidalia_transcript.xlsx relative to the current file as a pandas dataframe
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "data", "vidalia_transcript.xlsx")
df = pd.read_excel(file_path)

# econ_1101_students = df[df['course_name'] == 'ECON 1101']
# highest_score = econ_1101_students['score'].max()
# highest_scoring_students = econ_1101_students[econ_1101_students['score'] == highest_score]['student_name']
# print(highest_scoring_students)


executor = CustomUnsafeLocalCodeExecutor(df=df)

# Agent Definition
root_agent = LlmAgent(
    name=CODING_AGENT_NAME,
    model=GEMINI_MODEL,
    # tools=[unsafe_local_code_executor],
    code_executor=executor,
    instruction="""You are an expert python data scientist who can answer questions based on a given dataset.
    When given a query about the dataset, write and execute Python code to answer the query.
    The data is available to you as a Pandas dataframe called df. 
    When given a question for which you need to understand the structure of the data, invoke the tool
    multiple times to get the info on structure. Also, when there is possible metadata search involved,
    you might want to get unique values of the relevant column. 
    """,
    description="Executes Python code to analyze data.",
)

# # High-level agent delegating research
# root_agent = Agent(
#     name=ROOT_AGENT_NAME,
#     model="gemini-2.0-flash",
#     instruction=""""You are a customer service agent who will answer user questions. 
#     Use the coding agent to get the answer and then provide it in a formatted manner.
#     The coding agent is equipped with all the data. 
#     """,
#     sub_agents=[code_agent],
# )

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

# Instantiate the desired artifact service
artifact_service = InMemoryArtifactService()

# runner = Runner(agent=code_agent, app_name=APP_NAME, session_service=session_service, artifact_service=artifact_service)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service, artifact_service=artifact_service)

# Agent Interaction (Async)
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    print(f"\n--- Running Query: {query} ---")
    final_response_text = "No final text response captured."
    try:
        # Use run_async
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            print(f"Event ID: {event.id}, Author: {event.author}")

            # --- Check for specific parts FIRST ---
            has_specific_part = False
            if event.content and event.content.parts:
                for part in event.content.parts: # Iterate through all parts
                    if part.executable_code:
                        # Access the actual code string via .code
                        print(f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```")
                        has_specific_part = True
                    elif part.code_execution_result:
                        # Access outcome and output correctly
                        print(f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}")
                        has_specific_part = True
                    # Also print any text parts found in any event for debugging
                    elif part.text and not part.text.isspace():
                        print(f"  Text: '{part.text.strip()}'")
                        # Do not set has_specific_part=True here, as we want the final response logic below

            # --- Check for final response AFTER specific parts ---
            # Only consider it final if it doesn't have the specific code parts we just handled
            if not has_specific_part and event.is_final_response():
                if event.content and event.content.parts and event.content.parts[0].text:
                    final_response_text = event.content.parts[0].text.strip()
                    print(f"==> Final Agent Response: {final_response_text}")
                else:
                    print("==> Final Agent Response: [No text content in final event]")


    except Exception as e:
        print(f"ERROR during agent run: {e}")
    print("-" * 30)


# Main async function to run the examples
async def main():
    # await call_agent_async("Calculate the value of (5 + 7) * 3")
    # await call_agent_async("What is 10 factorial?")
    # await call_agent_async("How many rows are in the dataset?")
    # await call_agent_async("How many columns are in the dataset?")
    await call_agent_async("Which students scored the highest in econ 1101?")    
    # await call_agent_async("What percentage of students toop AP courses?")    
    # await call_agent_async("What is the distribution of grades in maths courses ?")        
    # await call_agent_async("Can you identify the CTAE courses? CTAE is Career, Technical, Agriculture and Education?")            


# Execute the main async function
try:
    asyncio.run(main())
except RuntimeError as e:
    # Handle specific error when running asyncio.run in an already running loop (like Jupyter/Colab)
    if "cannot be called from a running event loop" in str(e):
        print("\nRunning in an existing event loop (like Colab/Jupyter).")
        print("Please run `await main()` in a notebook cell instead.")
        # If in an interactive environment like a notebook, you might need to run:
        # await main()
    else:
        raise e # Re-raise other runtime errors