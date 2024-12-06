from flask import Flask, render_template, request, session
from serpapi import GoogleSearch
import openai

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "c8e7db16c44ae0ccf71bb6584ce6d085"

# API Keys
SERPAPI_KEY = "4bc7a54f59218de68c54a2a90747dcb4a39279ffe8cbcf02184af40dc4e6605c"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

# Function to handle different queries
def handle_query(query):
    code_result = ""

    # Check if the query is related to code execution
    if "python" in query.lower() or "code" in query.lower():
        code_result = execute_code(query)
    else:
        # Fetch results from multiple sources
        code_result = get_combined_results(query)

    return code_result[:300]  # Limit output to 300 characters for brevity

# Function to execute Python code dynamically
def execute_code(query):
    try:
        # Extract and safely execute Python code
        code_snippet = extract_code(query)
        exec_globals = {}
        exec(code_snippet, exec_globals)
        return exec_globals.get("result", "No output returned.")
    except Exception as e:
        return f"Error executing code: {str(e)}"

# Function to extract Python code from the query
def extract_code(query):
    return query.lower().replace("run", "").strip()

# Fetch results from multiple sources
def get_combined_results(query):
    serpapi_results = get_serpapi_answer(query)
    openai_results = get_openai_answer(query)

    # Return the most valid output available
    result = serpapi_results if serpapi_results else openai_results if openai_results else "No valid output available."
    return result[:300]  # Limit result to 300 characters

# Fetch answers from SerpApi
def get_serpapi_answer(query):
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": SERPAPI_KEY,
        })
        results = search.get_dict()
        if "organic_results" in results:
            top_result = results["organic_results"][0]
            return top_result.get("snippet", "").strip()
        return ""
    except Exception:
        return ""

# Fetch answers from OpenAI's GPT model
def get_openai_answer(query):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Answer the following query briefly:\n{query}",
            max_tokens=150,  # Ensure concise output
        )
        return response.choices[0].text.strip()
    except Exception:
        return ""

# Save query and result to history
def save_to_history(query, code_result):
    if "history" not in session:
        session["history"] = []
    session["history"].append({"query": query, "code_result": code_result})

@app.route("/", methods=["GET", "POST"])
def index():
    query = request.form.get("query", "").strip()
    code_results = ""

    if query:
        code_results = handle_query(query)
        save_to_history(query, code_results)

    history = session.get("history", [])
    return render_template("index.html", code_results=code_results, history=history)

if __name__ == "__main__":
    app.run(debug=True)
