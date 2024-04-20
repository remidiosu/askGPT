import streamlit as st 
from openai import OpenAI

# set page title 
st.set_page_config(page_title="askGPT")

# hide streamlit footer
hide_streamlit_footer = """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

# connect to OPENAI API
# set up OPENAI key through streamlit secrets 
gpt = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# read mentor files 
vector_store = gpt.beta.vector_stores.create(name="Mentors")
file_paths = ["mentor_bios/Dr._Aaron_Lee_-_Economics_Bio.docx", "mentor_bios/Dr._Emily_Tran_-_Biotechnology_Bio.docx",
              "mentor_bios/Mr._Jordan_Castillo_-_Software_Engineering_Bio.docx", 
              "mentor_bios/Ms._Angela_Meyer_-_Environmental_Science_Bio.docx", 
              "mentor_bios/Ms._Sonia_Patel_-_Entrepreneurship_Bio.docx"]

file_streams = [open(path, "rb") for path in file_paths]
file_batch = gpt.beta.vector_stores.file_batches.upload_and_poll(vector_store_id=vector_store.id, files=file_streams)


# creating assistant 
assistant = gpt.beta.assistants.create(
  name="Mentor Helper",
  instructions="""Context: You are assistant helping mentees to find the best match mentor. 
    You need to first ask user's relevant personal information and based on this match the best mentor for the user, from 'Mentors' files
    Please use information in the 'Mentors' files to form the best criteria, ask questions and match accordingly""",
  model="gpt-3.5-turbo",
  tools=[{"type": "file_search"}],
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

st.session_state.assistant_id = assistant.id
# set up default openai model 
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"


# define initial message 
initial_message = {'role':'assistant', 'content':"""Hello! I am your assistant in finding the best match mentor! 
                   To maximize my performance, please provide following information about yoursef: 
                Name, age, Background (university or school), Location, Main interests, Experience """}


# main function 
def mainChat():
    # add streamlit title
    st.title('myMentor')
    # initialize session variable messages to store chat history
    # messages is a list of dicts {role:'', content:''} 
    # add initial message
    
    if "messages" not in st.session_state:
        st.session_state.messages = [initial_message] 

    # display chat history to the page
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
    

    # chack if user has provided input prompt
    prompt = st.chat_input("...")
    
    if prompt:
        if 'thread_id' not in st.session_state:
            thread = gpt.beta.threads.create(
                messages=st.session_state.messages
            )
            st.session_state.thread_id = thread.id

        # display prompt on the screen
        with st.chat_message("user"):
            st.markdown(prompt)
        # add the prompt to the history
        st.session_state.messages.append({'role':'user', 'content':prompt})
        message = gpt.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role='user',
            content=prompt
        )
        gpt.beta.threads.messages.update(
            thread_id=st.session_state.thread_id,
            message_id=message.id
        )

        # display response on the screen
        with st.chat_message("assistant"):
            # create a run on a thread
            run = gpt.beta.threads.runs.create_and_poll(
                thread_id=st.session_state.thread_id,
                assistant_id=st.session_state.assistant_id,
                instructions="Help user to find the best mentor from the given files"
            ) 
            m = list(gpt.beta.threads.messages.list(thread_id=st.session_state.thread_id, run_id=run.id))
            response = m[0].content[0].text.value
            st.write(response)
            
            # add response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        

if __name__ == '__main__':
    # call main function
    mainChat()
