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

# set up default openai model 
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# main function 
def mainChat():
    # add streamlit title
    st.title('cloneGPT')
    # initialize session variable messages to store chat history
    # messages is a list of dicts {role:'', content:''} 
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display chat history to the page
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # chack if user has provided input prompt
    prompt = st.chat_input("Message ChatGPT...")
    if prompt:
        # display prompt on the screen
        with st.chat_message("user"):
            st.markdown(prompt)
        # add the prompt to the history
        st.session_state.messages.append({'role':'user', 'content':prompt})

        # display response on the screen
        with st.chat_message("assistant"):
            # create response stream for better frontend 
            stream = gpt.chat.completions.create(model=st.session_state['openai_model'],
                                                messages=[{"role": m["role"], "content": m["content"]}
                                                for m in st.session_state.messages], stream=True) # add message history to the prompt
            response = st.write_stream(stream)
            # add response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == '__main__':
    # call main function
    mainChat()