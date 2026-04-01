import streamlit as st
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
    from langchain_cerebras import ChatCerebras
    from langchain_core.prompts import PromptTemplate
except ImportError:
    st.error("Missing dependencies. Please run `uv add langchain-cerebras langchain-core`")
    st.stop()

# Define the allowed verbs
ALLOWED_VERBS = [
    "Navigate", "Click", "Type", "Select", "Check", "Verify", 
    "Assert", "Wait", "Hover", "Scroll", "Tap", "Login", "Logout"
]

def get_llm(model_name="llama3.1-8b"):
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("CEREBRAS_API_KEY", "")
        except Exception:
            pass

    if not api_key:
        return None
    
    return ChatCerebras(api_key=api_key, model=model_name, temperature=0)

# Set up the prompt template
PROMPT_TEMPLATE = """You are a QA automation expert. 
Your task is to take the following inconsistent QA test text and rewrite it into standard Gherkin format (Feature, Scenario, Given, When, Then, And).
Additionally, you MUST correct any poor English and ensure perfect consistency.

CRITICAL INSTRUCTION: You must strictly use verbs from the following approved vocabulary list for starting action steps (When/Then/And):
{allowed_verbs}

Inconsistent QA Text:
{user_input}

Output ONLY the formatted Gherkin text. Do not include any other conversational text.
"""


def main():
    st.set_page_config(page_title="QA Test Optimizer", page_icon="✨", layout="wide")

    st.markdown('<h1 class="title-text">✨ QA Optimizer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Convert inconsistent textual test cases into concise Gherkin syntax.</p>', unsafe_allow_html=True)

    st.sidebar.header("Configuration")
    
    # Model Selection
    AVAILABLE_MODELS = [
        "llama3.1-8b",
        "gpt-oss-120b",
        "zai-glm-4.7",
        "qwen-3-235b-a22b-instruct-2507"
    ]
    selected_model = st.sidebar.selectbox("Select LLM Model", AVAILABLE_MODELS, index=0)

    # Check if API Key is already configured
    api_key_configured = os.environ.get("CEREBRAS_API_KEY")
    if not api_key_configured:
        try:
            api_key_configured = st.secrets.get("CEREBRAS_API_KEY", "")
        except Exception:
            pass

    if api_key_configured:
        st.sidebar.success("✅ API Key configured securely")
    else:
        api_key_input = st.sidebar.text_input("Cerebras API Key", type="password", help="Enter your CEREBRAS_API_KEY if not set in the environment.")
        if api_key_input:
            os.environ["CEREBRAS_API_KEY"] = api_key_input

    llm = get_llm(selected_model)

    if not llm:
        st.warning("⚠️ Please provide a Cerebras API Key in the sidebar or set `CEREBRAS_API_KEY` in your environment to continue.")

    st.sidebar.subheader("Allowed Verb Vocabulary")
    st.sidebar.info(", ".join(ALLOWED_VERBS))

    st.sidebar.subheader("Sample Test Case")
    st.sidebar.write("Need a sample to test the app? Download this inconsistent use case:")
    st.sidebar.download_button(
        label="📄 Download Sample (.txt)",
        data="""i go to the main screen.
there is a login button on the top right, hit it.
then a popup appears.
put 'test_user' into the username box.
put 'secure_password!@#' inside the pass field.
then pres the sign in button.
wait for it to load.
check if the user profile icon shows up.
if yes, make sure clicking the profile icon shows 'Logout' option.""",
        file_name="sample_inconsistent_test.txt",
        mime="text/plain",
        key="download_sample"
    )

    st.subheader("Input")
    col1= st.columns(2)
    uploaded_file = col1[0].file_uploader("Upload a QA test text file (.txt)", type=["txt", "md"])
    file_content = ""
    if uploaded_file is not None:
        file_content = uploaded_file.getvalue().decode("utf-8")
        st.info("File content loaded into text area.")

    user_input = col1[1].text_area(
        "Or paste your inconsistent QA test text here:",
        height="content", 
        value=file_content, 
        placeholder="e.g. I go to the home page, i see login button. hit it.."
    )

    if st.button("Optimize Test", type="primary", disabled=not bool(llm)):
        if not user_input.strip():
            st.error("Please enter some text to optimize.")
            return

        with st.spinner("Optimizing your test case..."):
            try:
                prompt = PromptTemplate(
                    input_variables=["user_input", "allowed_verbs"],
                    template=PROMPT_TEMPLATE
                )
                
                chain = prompt | llm
                
                response = chain.invoke({
                    "user_input": user_input,
                    "allowed_verbs": ", ".join(ALLOWED_VERBS)
                })

                st.subheader("Result")
                st.code(response.content, language="gherkin")

                st.download_button(
                    label="📥 Download Output (.txt)",
                    data=response.content,
                    file_name="optimized_qa_test.txt",
                    mime="text/plain",
                    type="secondary"
                )

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
