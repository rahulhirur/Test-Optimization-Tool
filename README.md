# ✨ QA Test Optimizer

The QA Test Optimizer is a beautiful web application built with Streamlit and LangChain that automatically converts inconsistent, unformatted, and informal testing instructions into clean, standardized Gherkin syntax. 

🚀 **Try it Live:** [rahulhirur-q-a-test-optimization-tool.streamlit.app](https://rahulhirur-q-a-test-optimization-tool.streamlit.app)

## Features
- **Zero-Fluff Conversion**: Uses LLMs to accurately restructure conversational QA test text.
- **Strict Verb Vocabulary**: Guarantees standard action steps using a rigid verb vocabulary list (e.g., `Navigate, Click, Type, Verify...`).
- **Flexible Inputs**: Upload `.txt` test files or freely paste your test scenarios directly into the app.
- **Deterministic Generation**: Configured strictly with a temperature of `0` to keep scenarios robust, exact, and reproducible.
- **Dynamic Model Selection**: Dropdown capability to switch between capable language models (e.g., LLaMA, Qwen, GLM).
- **Premium UI**: Crafted with dark mode themes, gradient aesthetics, and wide-screen responsiveness.

## Run It Offline (Local Setup)

If you'd rather run the application locally on your machine, follow these steps:

1. **Install Dependencies**
   The project dependencies are managed via `uv`. Make sure packages like `streamlit`, `langchain-cerebras`, and `python-dotenv` are installed.
   ```bash
   uv sync
   ```

2. **API Keys**
   Create a `.env` file at the root of the project and add your API credentials:
   ```env
   CEREBRAS_API_KEY=your_secure_api_key_here
   ```
   *Alternatively, you can manually type this into the Streamlit sidebar after booting the app.*

3. **Start the Server**
   ```bash
   uv run streamlit run main.py
   ```
   Once the server starts, navigate to `http://localhost:8501` in your browser to transform tests securely from your own machine!

---

### 🔑 Bring Your Own Key Party!
To make the magic happen, you'll need the secret sauce—a **Cerebras API key**! 🧠✨ 
Don't have one yet? No worries! Just hop over to Cerebras, sweet-talk their developer page, and snatch your shiny new API key. Your models are hungry for data, so go out there and feed them those sweet, sweet tokens!
