 # Importing required packages
import streamlit as st
import openai
import uuid
import time
import pandas
import io
from openai import OpenAI
from openai.types import chat
from openai.types import CreateEmbeddingResponse, Embedding
from openai.types import FileContent, FileDeleted, FileObject

# Initialize OpenAI client
client = OpenAI()

# Your chosen model
MODEL = "gpt-3.5-turbo-1106"

# Initialize session state variables
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "run" not in st.session_state:
    st.session_state.run = {"status": None}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "retry_error" not in st.session_state:
    st.session_state.retry_error = 0

if "assistant" not in st.session_state:
    st.session_state.assistant = None

if "thread" not in st.session_state:
    st.session_state.thread = None
    
if "user_answers" not in st.session_state:
    st.session_state.user_answers = 0

# Fixed questions
fixed_questions = [
    "What is the paper about?",
    "What is/are the causes of obesity outlined by the authors?",
    # Add more fixed questions as needed
]


def get_name():
    input_text=st.text_input(label="First, what is your name?", placeholder="First name only is fine.", key="user_name")
    return input_text

def get_answer(key):
    input_ans=st.text_area(label="Please Answer the following", placeholder="Try your best to answer", key=key)
    return input_ans



# Define ConversationState classquestion
class ConversationState:
    def __init__(self):
        self.prompts = []
        self.responses = []

# Function to send prompt to AI
def send_prompt(prompt):
    st.session_state.run = client.beta.threads.runs.create(
    thread_id=st.session_state.thread.id,
    assistant_id=st.session_state.assistant.id)

# Function to retrieve AI response
def retrieve_answer(prompt):
    if st.session_state.thread is None:
        st.error("Error: Thread not initialized.")
        return

    output = client.beta.threads.messages.list(
        thread_id=st.session_state.thread.id
    )

    if output.data:
        latest_message = output.data[-1]  # Get the last message from the list
        # Now, extract the content of the message
        latest_message_content = latest_message.content[0].text.value
        # Continue with the rest of your code
    else:
        st.warning("No messages found in the thread.")
        


################ Main App #######################
st.title('Critical Appraisal - Tea consumption reduces ovarian cancer risk')
st.write('In this guided case study, we\'ll both read the same case study. Then, you\'ll be guided through an analysis of the paper. Let\'s begin by reading the paper!')

pdf_file_path = 'paper_assistant/Lee_journal.pdf'

# Download button for the PDF
with open(pdf_file_path, "rb") as pdf_file:
    st.download_button(label="Download PDF",
                       data=pdf_file,
                       file_name="Lee_journal.pdf",
                       mime="application/octet-stream")

user_name = get_name()

# Initialize OpenAI assistant
if "assistant" not in st.session_state:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.assistant = openai.beta.assistants.retrieve(st.secrets["OPENAI_ASSISTANT"])
    st.session_state.thread = client.beta.threads.create(
        metadata={'session_id': st.session_state.session_id}
    )
    st.success("OpenAI Assistant initialized")


if user_name is not None and st.button('Submit'):
    st.spinner("## This is session state before the first call is made")
    # state = ConversationState()
    st.title('Interactive AI Conversation')
    assistant = client.beta.assistants.create(
        name=user_name,
        instructions="You are a personal guider for users to a critical review of a paper and give them feedback at each step. So the questions I ask the students will be fixed, then the student will respond, and then the you will give feedback.",
        tools=[{"type": "retrieval"}],
        model="gpt-3.5-turbo-1106"
    )
    
    # Upload file to openai
    with open(pdf_file_path, 'rb') as file:
        file_content = file.read()
    file_response = FileContent(file_content)
    # file_response = client.files.create(file=file_content, purpose='assistants')
    st.session_state.file = file_response
    st.success("File uploaded successfully to OpenAI!")    
    
    # Initialize the thread
    st.session_state.thread = client.beta.threads.create(
        metadata={'session_id': st.session_state.session_id}
    )

    
        # Loop through fixed questions
    for index, question in enumerate(fixed_questions):
        # Ques = retrieve_answer(question)
        # st.write(Ques)
        st.write(question)
        key =  "user_ans" + str(index)
        user_ans = get_answer(key)
        user_ans = user_ans =+ index




        # Create a button for the user to submit their answers
        if st.button("Submit Answers"):
            # Store the user_answers dictionary in the session state after the loop
            st.session_state.user_answers = input_ans


    # # Check if the user has provided an answer
    # # if user_anss:
    #     # Compare user's answer with the expected answer
    #     expected_answer = "Expected answer for the question"
    #     feedback = "Correct! Well done!" if user_anss.lower() == expected_answer.lower() else "Oops! That's not quite right."

    #     # Display feedback to the user
    #     st.write("Feedback:", feedback)

    #     # Optionally, generate a dynamic prompt based on the user's response
    #     dynamic_prompt = f"Based on your answer to the previous question, ask a related question..."
    #     dyp = retrieve_answer(dynamic_prompt)
    #     st.write(dyp)
    # else:
    #     st.warning("Please provide an answer before moving to the next question.")
    #     break  # Stop the loop if the user hasn't answered
