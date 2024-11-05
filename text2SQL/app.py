import streamlit as st
import os
import pandas as pd
import io
import pathlib
import app_driver

#TODO: use tips from here
#https://github.com/dataprofessor/dashboard-kit

current_dir = pathlib.Path(__file__).parent.resolve()
print("current dir:", current_dir)
import sys
print("sys path: ", sys.path)

@st.cache_data
def load_driver():
    return app_driver.AppDriver(current_dir / pathlib.Path("config"))

# Load the cached model
app_driver = load_driver()

def ask_llm(question: str):
    return app_driver.ask_llm(question)

# Initialize session state variables
if 'show_system_instructions' not in st.session_state:
    st.session_state['show_system_instructions'] = False

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'user_question' not in st.session_state:
    st.session_state['user_question'] = ''

# Load system instructions from a file to persist across sessions
if 'system_instructions' not in st.session_state:
    if os.path.exists('system_instructions.txt'):
        with open('system_instructions.txt', 'r') as file:
            st.session_state['system_instructions'] = file.read()
    else:
        st.session_state['system_instructions'] = ''

# Sidebar settings
st.sidebar.title("Settings")

# Data Selection Section
st.sidebar.subheader("Data Selection")
dataset_choice = st.sidebar.selectbox(
    "Choose a dataset",
    ("Dataset A", "Dataset B", "Dataset C")
)

# LLM Settings Section
st.sidebar.subheader("LLM Settings")
llm_choice = st.sidebar.selectbox(
    "Choose an LLM",
    ("Gemini", "GPT-4o")
)

temperature = st.sidebar.number_input(
    "Model Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1
)

top_k = st.sidebar.number_input(
    "Top K",
    min_value=0,
    value=50,
    step=1
)

top_p = st.sidebar.number_input(
    "Top P",
    min_value=0.0,
    max_value=1.0,
    value=0.9,
    step=0.1
)

# Toggle button for showing/hiding system instructions
if st.sidebar.button(
    "Show System Instructions" if not st.session_state['show_system_instructions']
    else "Hide System Instructions"
):
    st.session_state['show_system_instructions'] = not st.session_state['show_system_instructions']

# Clear History button
if st.sidebar.button("Clear History"):
    st.session_state['history'] = []
    st.rerun()

# Rerun button
if st.sidebar.button("Rerun"):
    st.rerun()

# Main page
st.title("Text to SQL Generation App")

# System Instructions Panel
if st.session_state['show_system_instructions']:
    system_instructions = st.text_area(
        "System Instructions",
        value=st.session_state['system_instructions'],
        height=100
    )
    # Save system instructions if they have changed
    if system_instructions != st.session_state['system_instructions']:
        st.session_state['system_instructions'] = system_instructions
        with open('system_instructions.txt', 'w') as file:
            file.write(system_instructions)
else:
    system_instructions = st.session_state['system_instructions']

# Define the function to handle submission
def submit_question():
    # Access variables from the session state
    user_question = st.session_state['user_question']
    system_instructions = st.session_state['system_instructions']
    # Dummy API call function
    # def dummy_api_call(question, system_instructions, llm_choice, temperature, top_k, top_p, dataset_choice):
    #     return (
    #         f"This is a dummy answer to your question: '{question}' "
    #         f"using LLM '{llm_choice}' on dataset '{dataset_choice}'."
    #     )
    # answer = dummy_api_call(
    #     user_question,
    #     system_instructions,
    #     llm_choice,
    #     temperature,
    #     top_k,
    #     top_p,
    #     dataset_choice
    # )
    answer = ask_llm(user_question)
    # Append the question and answer to history
    st.session_state['history'].append({'question': user_question, 'answer': answer})
    # Clear the user question
    st.session_state['user_question'] = ''
    # Rerun the app to update the UI
    # st.rerun()

# User Question Input
st.text_area("Ask a question about your data:", key='user_question')

# Submit button with callback
st.button("Submit", on_click=submit_question)

# Display all previous questions and answers
for qa in reversed(st.session_state['history']):
    st.markdown(f"**Question:** {qa['question']}")
    st.markdown(f"**SQL:** {qa['answer'][0]}")

    try:
        data = io.StringIO(qa['answer'][1])
        df = pd.read_csv(data)
        # df_reset = df.reset_index(drop=True)
        df_dropped = df.drop(df.columns[0], axis=1)
        st.dataframe(df_dropped) 
    except Exception as e:
        # Handle the exception
        print("An error occurred:", e)    
        st.markdown(f"**Answer: ** {qa['answer'][1]}")
        st.markdown(f"**Error:** {str(e)}")
    
    st.markdown("---")  # Separator
