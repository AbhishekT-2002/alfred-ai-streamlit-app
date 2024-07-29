import streamlit as st
import spacy
import pandas as pd
import json
import base64
import pdfplumber
import re
from textblob import TextBlob
import requests
from requests.exceptions import RequestException, HTTPError, Timeout

# Load spaCy model with improved error handling
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.error("spaCy model not found. Please run 'python -m spacy download en_core_web_sm' to install it.")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while loading spaCy model: {str(e)}")
    st.stop()

# Initialize session state variables
session_defaults = {
    'message_list': [{"role": "system", "content": "You are a helpful assistant named Alfred AI."}],
    'pdf_message_list': [{"role": "system", "content": "You are a helpful assistant named Alfred AI. Your task is to answer questions based on the provided PDF content."}],
    'pdf_text': "",
    'response_tone': "Neutral",
    'interaction_count': 0,
    'user_name': "",
    'api_url': "https://projected-fellowship-montreal-something.trycloudflare.com/v1",
    'current_page': "welcome"
}
for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

class Conversation:
    def __init__(self, api_url):
        self.api_url = api_url
        self.headers = {"Content-Type": "application/json"}

    def message(self, question, context=""):
        st.session_state.interaction_count += 1
        context_question = f"{context}\n\nUser's question: {question}" if context else question
        tone_instruction = self.get_tone_instruction()

        messages = [
            {"role": "system", "content": f"You are a helpful assistant named Alfred AI. {tone_instruction}"},
            {"role": "user", "content": context_question}
        ]

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"mode": "chat", "character": "Example", "messages": messages},
                verify=False,
                timeout=10  # Added timeout
            )
            response.raise_for_status()  # Raises HTTPError for bad responses
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        except HTTPError as http_err:
            st.error(f"HTTP error occurred: {http_err}")
        except Timeout:
            st.error("The request timed out. Please try again.")
        except RequestException as req_err:
            st.error(f"Request error occurred: {req_err}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
        return None

    def get_tone_instruction(self):
        tone_map = {
            "Neutral": "Respond in a neutral and balanced tone.",
            "Friendly": "Respond in a warm and friendly tone, as if talking to a close friend.",
            "Formal": "Respond in a formal and professional tone, suitable for business communication.",
            "Casual": "Respond in a casual and relaxed tone, using informal language."
        }
        return tone_map.get(st.session_state.response_tone, "")

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += clean_text(page_text)
        return text
    except Exception as e:
        st.error(f"An error occurred while extracting text from the PDF: {str(e)}")
        return None

def extract_entities(text):
    try:
        doc = nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]
    except Exception as e:
        st.error(f"An error occurred while extracting entities: {str(e)}")
        return None

def format_entities_for_display(entities):
    df = pd.DataFrame(entities, columns=['Entity', 'Type'])
    color_map = {
        "PERSON": "orange",
        "CARDINAL": "lightblue",
        "ORG": "blue",
        "GPE": "darkgreen",
        "DATE": "pink",
        "TIME": "brown",
        "MONEY": "green",
        "LOC": "cyan",
        "PRODUCT": "yellow",
        "LANGUAGE": "purple",
        "WORK_OF_ART": "gold"
    }
    df['Color'] = df['Type'].map(color_map).fillna('black')
    return df

def apply_color_map(df):
    return df.style.apply(lambda row: ['background-color: {}'.format(color) for color in row], subset=['Color'], axis=1)

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="named_entities.csv">Download CSV file</a>'

def export_conversation():
    try:
        conversation_data = json.dumps(st.session_state.message_list, indent=2)
        b64 = base64.b64encode(conversation_data.encode()).decode()
        return f'<a href="data:file/json;base64,{b64}" download="conversation_history.json">Download Conversation History</a>'
    except Exception as e:
        st.error(f"An error occurred while exporting conversation history: {str(e)}")
        return ""

def search_text(text, query):
    return [match.start() for match in re.finditer(re.escape(query), text, re.IGNORECASE)]

def display_search_results(text, query):
    indices = search_text(text, query)
    if indices:
        for index in indices:
            snippet = text[max(0, index - 30):index + 30]
            st.write(f"...{snippet}...")
    else:
        st.write("No results found.")

def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        return blob.sentiment
    except Exception as e:
        st.error(f"An error occurred while analyzing sentiment: {str(e)}")
        return TextBlob("")

def main():
    st.set_page_config(page_title="Alfred AI", layout="wide")
    st.title('Alfred AI')

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Welcome", "General Chat", "PDF Analysis", "Settings"])

    if page == "Welcome":
        welcome_page()
    elif page == "General Chat":
        chat_page()
    elif page == "PDF Analysis":
        pdf_analysis_page()
    elif page == "Settings":
        settings_page()

def welcome_page():
    st.header("Welcome to Alfred AI")
    if st.session_state.user_name == "" or st.session_state.api_url == "":
        st.write("Please enter your name and API URL to continue.")
        user_name = st.text_input("Enter your name:")
        api_url = st.text_input("Enter your API BASE_URL:", placeholder="https://never-gonna-give-you-up.com/v1")
        api_url = api_url.strip()
        api_url = api_url + "/chat/completions"
        if st.button("Continue"):
            if user_name and api_url:
                st.session_state.user_name = user_name
                st.session_state.api_url = api_url
                st.success(f"Welcome, {user_name}! API URL set. Please use the sidebar to navigate.")
            else:
                st.error("Name and API BASE_URL cannot be empty.")
    else:
        st.write(f"Welcome back, {st.session_state.user_name}!")
        st.write("Use the sidebar to navigate through different features of Alfred AI.")

def chat_page():
    st.header("General Chat with Alfred AI")
    conversation = Conversation(api_url=st.session_state.api_url)

    for message in st.session_state.message_list:
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.write(f"{st.session_state.user_name}: {message['content']}")
        elif message['role'] == 'assistant':
            with st.chat_message("assistant"):
                st.write(f"Alfred AI: {message['content']}")

    prompt = st.chat_input("Type your message here")
    if prompt:
        with st.spinner('Thinking...'):
            # Add the new user message to the message list
            st.session_state.message_list.append({"role": "user", "content": prompt})

            # Send the context and prompt to get the assistant's response
            context = "\n".join([msg['content'] for msg in st.session_state.message_list if msg['role'] == 'user'])
            answer = conversation.message(prompt, context)

            if answer:
                # Add the assistant's response to the message list
                st.session_state.message_list.append({"role": "assistant", "content": answer})
                st.experimental_rerun()

def pdf_analysis_page():
    st.header("PDF Analysis")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file:
        pdf_text = extract_text_from_pdf(uploaded_file)
        if pdf_text:
            st.session_state.pdf_text = pdf_text
            st.success("PDF text extracted successfully!")

            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Named Entities", "Extracted Text", "Search", "Sentiment Analysis", "Chat with PDF"])

            with tab1:
                entities = extract_entities(st.session_state.pdf_text)
                if entities:
                    df = format_entities_for_display(entities)
                    st.dataframe(apply_color_map(df))
                    st.markdown(get_table_download_link(df), unsafe_allow_html=True)
                else:
                    st.write("No entities found.")

            with tab2:
                st.write(st.session_state.pdf_text)

            with tab3:
                query = st.text_input("Enter search query")
                if query:
                    display_search_results(st.session_state.pdf_text, query)

            with tab4:
                sentiment = analyze_sentiment(st.session_state.pdf_text)
                st.write(f"Sentiment Analysis: {sentiment}")

            with tab5:
                conversation = Conversation(api_url=st.session_state.api_url)
                for message in st.session_state.pdf_message_list:
                    if message['role'] == 'user':
                        with st.chat_message("user"):
                            st.write(f"User: {message['content']}")
                    elif message['role'] == 'assistant':
                        with st.chat_message("assistant"):
                            st.write(f"Alfred AI: {message['content']}")

                prompt = st.chat_input("Ask about the PDF content")
                if prompt:
                    with st.spinner('Thinking...'):
                        st.session_state.pdf_message_list.append({"role": "user", "content": prompt})
                        context = st.session_state.pdf_text
                        answer = conversation.message(prompt, context)

                        if answer:
                            st.session_state.pdf_message_list.append({"role": "assistant", "content": answer})
                            st.experimental_rerun()

def settings_page():
    st.header("Settings")
    tone_options = ["Neutral", "Friendly", "Formal", "Casual"]
    st.session_state.response_tone = st.selectbox("Select Response Tone", tone_options, index=tone_options.index(st.session_state.response_tone))

    st.write("API Settings")
    st.session_state.api_url = st.text_input("API URL", value=st.session_state.api_url)

    st.markdown(export_conversation(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
