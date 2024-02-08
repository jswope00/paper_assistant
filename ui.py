import streamlit as st


# Fixed questions
fixed_questions = [
    "What is the paper about?",
    "What is/are the causes of obesity outlined by the authors?",
    "What is the main conclusion of the paper?",
    "What are the limitations of the study?",
    # Add more fixed questions as needed
]

user_name = st.session_state.user_name if 'user_name' in st.session_state else None
current_question_index = st.session_state.current_question_index if 'current_question_index' in st.session_state else 0

def get_user_answer(question):
    user_ans = st.text_area(label=f"Student: {question}", key=question)
    return user_ans

def question_generator():
    for question in fixed_questions:
        yield question

def on_submit():
    st.session_state.current_question_index += 1


def handle_question_answer():
    # Initialize session state variables if they don't exist
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0

    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}

    while st.session_state.current_question_index < len(fixed_questions):
        current_question_index = st.session_state.current_question_index
        current_question = fixed_questions[current_question_index]
        st.session_state.user_answers = get_user_answer(current_question)

        submit_ans = st.button(f"Submit Answer", on_click=on_submit)

        if submit_ans == True or st.session_state.user_answers != "":
            break
        else:
            break  # Break the loop if submit button is not pressed or user_ans is empty
        break


################ Main App #######################     
st.write(st.session_state)
if user_name is None:
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
    if st.button("Submit") and user_name:
        st.session_state.user_name = user_name

elif current_question_index < len(fixed_questions):
    handle_question_answer()

else:
    st.write("All questions answered")
