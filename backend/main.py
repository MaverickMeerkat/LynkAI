from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import os
import re
from git import Repo

repo_path = "/app/repo"

# Git integration
def commit_and_push_yaml(repo_path, file_path, commit_message):
    repo = Repo(repo_path)
    repo.git.add(file_path)
    repo.index.commit(commit_message)
    origin = repo.remote(name='origin')
    origin.push()

# Global state (simple)
last_yaml = {
    "yaml": None,
    "pending_commit": False
}

# def test_git():
#     repo_path = "/app/repo"
#     repo = Repo(repo_path)

#     # Create a dummy file
#     dummy_file_path = os.path.join(repo_path, "test_dummy_file.txt")
#     with open(dummy_file_path, "w") as f:
#         f.write("This is a test dummy file.\n")

#     # Stage the file
#     repo.git.add("test_dummy_file.txt")

#     # Commit the file
#     repo.index.commit("Add test dummy file via GitPython")

#     # Push the commit to the remote
#     origin = repo.remote(name='origin')
#     origin.push()

#     print("✅ Dummy file committed and pushed!")


app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

class Message(BaseModel):
    text: str

# @app.post("/chat")
# async def chat(message: Message):
#     # if message.text == "git":
#     #     test_git()
#     #     return {"response": "Dummy file committed and pushed!"}
#     # Load static context from Context.txt
#     with open("Context.txt", "r", encoding="utf-8") as f:
#         context = f.read()

#     # Build prompt with user input
#     prompt = f"""You are a Lynk feature creation assistant. 
#         Base your response on the documentation provided below.
#         If information is missing, ask for clarification.

#         Documentation:
#         {context}

#         User query: {message.text}
#     """

#     # Send to Gemini
#     response = client.models.generate_content(
#         model='gemini-2.5-flash-preview-05-20',
#         contents=prompt
#     )
    
#     return {"response": response.text}



@app.post("/chat")
async def chat(message: Message):
    global last_yaml

    user_input = message.text.strip().lower()

    # Check for commit trigger
    if user_input in ["yes", "yeah", "yep", "ok", "git"] and last_yaml["pending_commit"]:
        repo_path = "/app/repo"
        # Extract filename from the YAML content (e.g., "# customer.yml")
        filename_match = re.search(r"#\s*(\S+\.yml)", last_yaml["yaml"])
        if filename_match:
            filename = filename_match.group(1)
        else:
            filename = "generated_feature.yml"  # fallback if no header

        file_path = os.path.join(repo_path, "features", filename)

        # Ensure the features directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write YAML to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(last_yaml["yaml"])

        # Commit and push
        commit_and_push_yaml(repo_path, file_path, "Add generated feature from AI agent")
        last_yaml = {"yaml": None, "pending_commit": False}
        return {"response": "✅ Feature committed and pushed to GitHub!"}

    # Load context
    with open("Context.txt", "r", encoding="utf-8") as f:
        context = f.read()

    # Build prompt
    prompt = f"""You are a Lynk feature creation assistant.
        Base your response on the documentation provided below.
        Assume the database is using TPCH schema. So some of the entities are:
        Order, Customer, Line Item. 
        If you have enough information to generate the YAML, do so and **ask the user** if they want to commit it to Git.
        If more details are needed, ask follow-up questions.

        Documentation:
        {context}

        User query: {message.text}
        """

    # Query Gemini
    response = client.models.generate_content(
        model='gemini-2.5-flash-preview-05-20',
        contents=prompt
    )

    response_text = response.text

    # Extract YAML block (if present)
    yaml_match = re.search(r"```yaml\n([\s\S]*?)```", response_text)
    if yaml_match:
        yaml_code = yaml_match.group(1)
        last_yaml = {
            "yaml": yaml_code,
            "pending_commit": True
        }
        response_text += "\n\nWould you like me to commit this to Git? (yes/yeah/ok/git)"

    return {"response": response_text}
