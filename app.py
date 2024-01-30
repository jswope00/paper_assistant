 # Importing required packages
import streamlit as st
import openai
import uuid
import time
import pandas
import io
from openai import OpenAI

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


st.title('Critical Appraisal - Tea consumption reduces ovarian cancer risk')
st.write('In this guided case study, we\'ll both read the same case study. Then, you\'ll be guided through an analysis of the paper. Let\'s begin by reading the paper!')

pdf_file_path = 'Lee_journal.pdf'

# Download button for the PDF
with open(pdf_file_path, "rb") as pdf_file:
    st.download_button(label="Download PDF",
                       data=pdf_file,
                       file_name="Lee_journal.pdf",
                       mime="application/octet-stream")


def get_name():
    input_text=st.text_area(label="First, what is your name?", placeholder="First name only is fine.", key="user_name")
    return input_text

user_name = get_name()

def send_prompt():
    st.markdown("## This is the prompt going to AI, along with some context about what converssation it belongs in")
    st.write(message)
    st.session_state.run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id,
    )

def retrieve_answer():
    output = client.beta.threads.messages.list(
        thread_id=st.session_state.thread.id
    )
    st.markdown("## Now we write the messages list from AI")
    st.write(output.data)

    if output.data:
        latest_message = output.data[-1]  # Get the last message from the list
        st.write(latest_message)
        # Now, extract the content of the message
        latest_message_content = latest_message.content[0].text.value
        st.write(latest_message_content)
        
    else:
        st.write("No messages found in the thread.")

if user_name is not None and st.button('Submit'):
    st.markdown("## This is session state before the first call is made")
    st.write(st.session_state)
    # Initialize OpenAI assistant
    if "assistant" not in st.session_state:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        st.session_state.assistant = openai.beta.assistants.retrieve(st.secrets["OPENAI_ASSISTANT"])
        st.session_state.thread = client.beta.threads.create(
            metadata={'session_id': st.session_state.session_id}
        )
        st.markdown("## Thread Created:")
        st.write(st.session_state.thread)
        message = client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content="My name is " + user_name + ". Who are you?"
        )
        send_prompt()
        retrieve_answer()
        
        st.markdown("## This is session state after the the call is made to the AI")
        st.write(st.session_state)
    # Display chat messages
        st.markdown("## Now we wait")
        time.sleep(2)
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id,
            run_id=st.session_state.run.id,
        )
        st.markdown("## FIRST time retrieving status")
        st.write(st.session_state.run)
        time.sleep(2)
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id,
            run_id=st.session_state.run.id,
        )
        st.markdown("## SECOND time retrieving status")
        st.write(st.session_state.run)
        time.sleep(2)
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id,
            run_id=st.session_state.run.id,
        )
        st.markdown("## THIRD time retrieving status")
        st.write(st.session_state.run)
        retrieve_answer()


    elif hasattr(st.session_state.run, 'status') and st.session_state.run.status == "completed":
        message = client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content="My name is " + user_name + ". Who are you?"
        )
        send_prompt()
        retrieve_answer()
        #st.session_state.messages = client.beta.threads.messages.list(
        #    thread_id=st.session_state.thread.id
        #)
        #for message in reversed(st.session_state.messages.data):
        #    if message.role in ["user", "assistant"]:
        #        with st.chat_message(message.role):
        #            for content_part in message.content:
        #                message_text = content_part.text.value
        #                st.markdown(message_text)
        #st.write("Third")
        #st.write(st.session_state)
        #output = client.beta.threads.messages.list(
        #    thread_id=st.session_state.thread.id
        #    )
        # The API response includes a list of messages. The latest message is typically at the end of this list.
        # Check if there are any messages first
        #if output and 'data' in output and output['data']:
        #    latest_message = output['data'][-1]  # Get the last message from the list
            # Now, extract the content of the message
        #    if 'content' in latest_message:
        #        latest_message_content = latest_message['content']
        #        st.write(latest_message_content)
        #    else:
        #        st.write("Latest message has no content.")
        #else:
        #    st.write("No messages found in the thread.")

# Chat input and message creation with file ID
#if prompt := st.chat_input("How can I help you?"):
#    with st.chat_message('user'):
#        st.write(prompt)

#    message_data = {
#        "thread_id": st.session_state.thread.id,
#        "role": "user",
#        "content": prompt
#    }


#    st.session_state.messages = client.beta.threads.messages.create(**message_data)

#    st.session_state.run = client.beta.threads.runs.create(
#        thread_id=st.session_state.thread.id,
#        assistant_id=st.session_state.assistant.id,
#    )
    if st.session_state.retry_error < 3:
        time.sleep(1)
    #    st.rerun()

# Handle run status
if hasattr(st.session_state.run, 'status'):
    if st.session_state.run.status == "running":
        with st.chat_message('assistant'):
            st.write("Thinking ......")
        if st.session_state.retry_error < 3:
            time.sleep(1)
            #st.rerun()

    elif st.session_state.run.status == "failed":
        st.session_state.retry_error += 1
        with st.chat_message('assistant'):
            if st.session_state.retry_error < 3:
                st.write("Run failed, retrying ......")
                time.sleep(3)
            #    st.rerun()
            else:
                st.error("FAILED: The OpenAI API is currently processing too many requests. Please try again later ......")

    elif st.session_state.run.status != "completed":
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id,
            run_id=st.session_state.run.id,
        )
        if st.session_state.retry_error < 3:
            time.sleep(3)
            #st.rerun()
