import streamlit as st
import openai
import uuid
import time
import json
import re
from openai import OpenAI
import random
import requests
from streamlit_lottie import st_lottie_spinner, st_lottie

# Fixed questions
fixed_questions = [
    "What is the paper about?",
    "What is/are the causes of obesity outlined by the authors?",
    "What is the main conclusion of the paper?",
    "What are the limitations of the study?",
    "What are the strengths of the study?",
    # Add more fixed questions as needed
]

user_name = st.session_state.user_name if 'user_name' in st.session_state else None
current_question_index = st.session_state.current_question_index if 'current_question_index' in st.session_state else 0

def spinner():   # Animated json spinner

    @st.cache_data
    def load_lottie_url(url:str):
        r= requests.get(url)
        if r.status_code != 200:
            return
        return r.json()


    lottie_url = "https://lottie.host/65dbbc74-ba39-44fe-97fa-1b7b7fc09cce/pa0DVwSS9k.json"
    lottie_json = load_lottie_url(lottie_url)

    st_lottie(lottie_json, height=200)
    time.sleep(5)  # Simulate some processing time

# def spinner():   # Streamlit spinner  (Uncomment this and comment the above function to use this)
#             # Randomly choose from different "thinking" messages
#     thinking_messages = ["Thinking...", "Generating response...", "Consulting the AI...", "Analyzing your question..."]
#     thinking_message = random.choice(thinking_messages)
#     with st.spinner(thinking_message):
#         time.sleep(2)  # Simulate some processing time

def extract_score(text):
    # Define the regular expression pattern
    pattern = r'"score": (\d+)'
    
    # Use regex to find the score pattern in the text
    match = re.search(pattern, text)
    
    # If a match is found, return the score, otherwise return None
    if match:
        return int(match.group(1))
    else:
        return None

def chatbot(question):
    # Initialize OpenAI client
    client = OpenAI()

    # Models 
    MODEL = "gpt-3.5-turbo-1106" # Latest model
    
    # Initialize session state variables
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "run" not in st.session_state:
        st.session_state.run = {"status": None}

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "retry_error" not in st.session_state:
        st.session_state.retry_error = 0

    # Initialize OpenAI assistant
    if "assistant" not in st.session_state:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        st.session_state.assistant = openai.beta.assistants.retrieve(st.secrets["OPENAI_ASSISTANT"])
        st.session_state.thread = client.beta.threads.create(
            metadata={'session_id': st.session_state.session_id}
        )
        
    # Display chat messages
    elif hasattr(st.session_state.run, 'status') and st.session_state.run.status == "completed":
        st.session_state.messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread.id
        )
        for message in reversed(st.session_state.messages.data):
            if message.role in ["user", "assistant"]:
                with st.chat_message(message.role):
                    for content_part in message.content:
                        message_text = content_part.text.value
                        st.markdown(message_text)

    # Chat input and message creation with file ID
    if prompt := st.chat_input(f"Question: {question}", key=f"chat_{question}"):
        with st.chat_message('user'):
            st.write(prompt)

        message_data = {
            "thread_id": st.session_state.thread.id,
            "role": "user",
            "content": prompt
        }

        # Include file ID in the request if available
        if "file_id" in st.session_state:
            message_data["file_ids"] = [st.session_state.file_id]

        st.session_state.messages = client.beta.threads.messages.create(**message_data)

        st.session_state.run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id=st.session_state.assistant.id,
        )
        if st.session_state.retry_error < 3:
            time.sleep(1)
            st.rerun()

    # Handle run status
    if hasattr(st.session_state.run, 'status'):
        if st.session_state.run.status == "running":

            if st.session_state.retry_error < 3:
                st.rerun()

        elif st.session_state.run.status == "failed":
            st.session_state.retry_error += 1
            with st.chat_message('assistant'):
                if st.session_state.retry_error < 3:
                    st.write("Run failed, retrying ......")
                    st.rerun()
                else:
                    st.error("FAILED: The OpenAI API is currently processing too many requests. Please try again later ......")

        elif st.session_state.run.status != "completed":
            st.session_state.run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=st.session_state.run.id,
            )
            if st.session_state.retry_error < 3:
                spinner()
                st.rerun()


def get_user_answer(question):
    user_ans = st.text_area(label=f"Student: {question}", key=question)
    return user_ans

def question_generator():
    for question in fixed_questions:
        yield question




def handle_question_answer():
    # Initialize session state variables if they don't exist
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0

    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}

    while st.session_state.current_question_index < len(fixed_questions):
        current_question_index = st.session_state.current_question_index
        current_question = fixed_questions[current_question_index]
        
        
        # Call chatbot to interact with the user
        st.write(current_question)
        chatbot(current_question)
        
        score = extract_score(str(st.session_state.messages))
        

            # Display the extracted score
        if score is not None:
            st.write(f"The extracted score is: {score}")
            # Example logic: Do not release the next question until the score is at least 2
            if score >= 2:
                next_quest = st.button(f"Next Question", on_click=on_submit)

                if next_quest and st.session_state.user_answers != "":
                    st.write(current_question)
                    break
            else:
                st.write("Score is less than 2. Cannot release the next question.")
                break
        else:
            st.write("No score found in the text.")
            break  # Break the loop if submit button is not pressed or user_ans is empty
        break


def on_submit():
    st.session_state.current_question_index += 1
    
################ Main App #####################
st.title('Critical Appraisal - Tea consumption reduces ovarian cancer risk')
st.write('In this guided case study, we\'ll both read the same case study. Then, you\'ll be guided through an analysis of the paper. Let\'s begin by reading the paper!')

pdf_file_path = 'paper_assistant/Lee_journal.pdf'

# Download button for the PDF
with open(pdf_file_path, "rb") as pdf_file:
    st.download_button(label="Download PDF",
                    data=pdf_file,
                    file_name="Lee_journal.pdf",
                    mime="application/octet-stream")
    
user_name = st.text_input(label="First, what is your name?", key="user_name")
if st.button("Submit") == True or user_name != "":
            # st.session_state.user_name = user_name
    handle_question_answer()
    # st.write(st.session_state)
    # st.write("++++++++++>",st.session_state.messages)
    
