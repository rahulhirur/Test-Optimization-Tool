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

    # Ensure there is a chat history container
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! 👋 Paste an inconsistent QA test case below, or upload a `.txt` file using the sidebar, and I'll convert it to perfect Gherkin syntax."}]



    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        # Sanitize corrupt objects in case previous runs stored a ChatInputValue
        if not isinstance(message["content"], str):
            text_prop = getattr(message["content"], "text", "")
            message["content"] = str(text_prop) if text_prop else "[Uploaded File Received]"

        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and idx > 0:
                raw_content = message["content"].replace("```gherkin\n", "").replace("\n```", "")
                st.download_button(
                    label="📥 Download Output (.txt)",
                    data=raw_content,
                    file_name=f"optimized_qa_test_{idx}.txt",
                    mime="text/plain",
                    type="secondary",
                    key=f"download_{idx}"
                )

    # Chat input (Accepts text and files)
    prompt = st.chat_input("Paste text or drop a file...", accept_file="multiple", file_type=["txt", "md"])
    if prompt:
        user_text = ""
        
        # Determine if it's a string (old API) or object/dict (new API)
        if isinstance(prompt, str):
            user_text = prompt
        else:
            # It's an object or dict
            text_part = getattr(prompt, "text", "") or (prompt.get("text", "") if isinstance(prompt, dict) else "")
            
            files_part = []
            if hasattr(prompt, "files"):
                files_part = prompt.files or []
            elif isinstance(prompt, dict):
                files_part = prompt.get("files", [])
            else:
                try:
                    files_part = prompt["files"] or []
                except (KeyError, TypeError, AttributeError):
                    pass
            
            if text_part:
                user_text += str(text_part) + "\n\n"
                
            for uploaded_file in files_part:
                user_text += uploaded_file.getvalue().decode("utf-8") + "\n\n"

        user_text = user_text.strip()
            
        if user_text:
            # Must be str to prevent Streamlit rendering crashes
            st.session_state.messages.append({"role": "user", "content": str(user_text)})
            st.rerun()

    # Process pending user message
    if st.session_state.messages[-1]["role"] == "user":
        if not llm:
            with st.chat_message("assistant"):
                st.error("Please configure your Cerebras API key in the sidebar first!")
            return
            
        with st.chat_message("assistant"):
            with st.spinner("Optimizing your test case..."):
                try:
                    chain_prompt = PromptTemplate(
                        input_variables=["user_input", "allowed_verbs"],
                        template=PROMPT_TEMPLATE
                    )
                    chain = chain_prompt | llm
                    
                    user_text = st.session_state.messages[-1]["content"]
                    response = chain.invoke({
                        "user_input": user_text,
                        "allowed_verbs": ", ".join(ALLOWED_VERBS)
                    })
                    
                    st.session_state.messages.append({"role": "assistant", "content": f"```gherkin\n{response.content}\n```"})
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
