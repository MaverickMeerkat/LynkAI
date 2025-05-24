from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import re
from git import Repo
from prompts import LYNK_ASSISTANT_PROMPT
from dotenv import load_dotenv

commit_and_push_function = types.FunctionDeclaration(
    name="commit_and_push_yaml",
    description="Commits the generated YAML to the Git repository and pushes it to GitHub.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "filename": types.Schema(type=types.Type.STRING, description="The name of the YAML file to save."),
            "content": types.Schema(type=types.Type.STRING, description="The YAML content to save."),
        },
        required=["filename", "content"]
    )
)

tools = [types.Tool(function_declarations=[commit_and_push_function])]
config = types.GenerateContentConfig(tools=tools)

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
        contents=prompt,
        config=config
    )

    # response_text = response.text
    candidate = response.candidates[0]

    if candidate.content.parts[0].function_call:
        function_call = candidate.content.parts[0].function_call
        function_name = function_call.name
        function_args = function_call.args

        if function_name == "commit_and_push_yaml":
            filename = function_args["filename"]
            yaml_content = function_args["content"]

            repo_path = "/app/repo"
            file_path = os.path.join(repo_path, "features", filename)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml_content)

            commit_and_push_yaml(repo_path, file_path, "Add generated feature from AI agent")

            response_text = f"✅ Feature `{filename}` committed and pushed to GitHub!"
        else:
            response_text = f"⚠️ Gemini suggested unknown function: {function_name}"
    else:
        # Fallback to normal text reply
        response_text = "".join(
            part.text for part in candidate.content.parts if hasattr(part, "text")
        )

    # Save conversation history
    message_history.append({"role": "user", "content": message.text.strip().lower()})

    return {"response": response_text}
