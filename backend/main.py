from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import os
import re
from git import Repo
from prompts import LYNK_ASSISTANT_PROMPT
from dotenv import load_dotenv

repo_path = "/app/repo"

load_dotenv()  # loads variables from .env into os.environ

# Git integration
def commit_and_push_yaml(repo_path, file_path, commit_message):
    repo = Repo(repo_path)
    repo.git.add(file_path)
    repo.index.commit(commit_message)
    origin = repo.remote(name='origin')
    origin.push()

# Global state
last_yaml = {
    "yaml": None,
    "pending_commit": False
}

# Message history
message_history = []

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

class Message(BaseModel):
    text: str


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
        
        print(filename)

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
    with open("Context.md", "r", encoding="utf-8") as f:
        context = f.read()

    # Build prompt
    prompt = LYNK_ASSISTANT_PROMPT.format(
            context=context,
            message=message,
            conversation_history="\n".join([f"{msg['role']}: {msg['content']}" for msg in message_history])
        )

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

    message_history.append({"role": "user", "content": user_input})

    return {"response": response_text}
