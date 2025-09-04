# Voice Cursor (NexusCoder)

An interactive voice-enabled AI coding assistant that lets you converse naturally (via speech or text) while it autonomously reasons over your project files, executes shell commands, searches the web, and iterates using a LangGraph workflow. It streams responses token-by-token, supports tool calling, and logs all activity to Langfuse for observability and analytics. Checkpointing is powered by MongoDB so multi-step conversations maintain state.

> "Talk to your codebase" – dictate a request ("scan the repo and refactor the tool loader"), let the agent inspect files, run commands, and explain results in real time.

## Key Features
- Voice + Text Input: Choose microphone-driven speech recognition (Google Speech Recognition via `SpeechRecognition` + `PyAudio`) or traditional typed input.
- Tool-Augmented LLM: Gemini (Google GenAI) model bound with custom tools: file scan, read/write, command execution, web search, and code analysis.
- Autonomous Graph Orchestration: Built with `langgraph` using a state graph that loops LLM ↔ tools until completion.
- Persistent Checkpointing: Conversation + tool state stored via `langgraph` checkpointing in MongoDB.
- Observability & Tracing: Full traces, spans, inputs/outputs captured through Langfuse (self-hostable via provided Docker Compose stack).
- Web Search Integration: Uses Google Serper API (optional Tavily integration placeholder) for up-to-date coding/contextual info.
- Safe Command Execution Wrapper: Executes shell commands and streams outputs (with basic error capture).
- Structured System Persona: Enforced expert full‑stack & algorithms persona ("NexusCoder") with domain guardrails.
- Extensible Tool Layer: Easily add new tools by decorating functions with `@tool` and binding them in `graph.py`.

## Tech Stack
Core Runtime:
- Python 3.13 (project appears compiled under 3.13 judging from cached bytecode)
- LangChain + LangGraph ecosystem (`langgraph`, `langgraph-checkpoint`, `langgraph-checkpoint-mongodb`)
- Google Gemini via `langchain-google-genai`
- Langfuse (worker + web dashboard) for LLM observability
- MongoDB for state checkpointing
- Speech stack: `SpeechRecognition`, `PyAudio`
- Web search: `GoogleSerperAPIWrapper` (Serper API)

Supporting Libraries:
- `python-dotenv` for environment config
- `pymongo` for Mongo connectivity
- `langfuse` Python SDK for callbacks
- `TavilySearch` dependency stubbed (optional)
- Utility libs listed in `requirements.txt` (HTTP clients, typing, serialization)

Dev / Build:
- `setup.py` for packaging & console entry point (`voice-cursor`)
- Tailwind/PostCSS dev dependencies (present in `package.json`; currently unused in Python runtime — future UI?)
- Docker Compose stacks for Langfuse + MongoDB

## Repository Structure
```
voice_cursor/
  main.py                # CLI loop: choose input mode, stream responses
  graph.py               # LangGraph state machine + LLM + tool binding
  tools.py               # Tool implementations (search, scan, read/write, exec, analyze)
  speech_to_text.py      # Microphone capture + Google speech recognition
  docker-compose.langfuse.yml  # Self-host Langfuse telemetry stack
  docker-compose.checkpoint.yml # MongoDB for checkpointing
.env (DO NOT COMMIT REAL SECRETS)
requirements.txt
setup.py
package.json
```

## Architecture Overview
1. User supplies input (voice → text via `speech_to_text()` or direct text).
2. Input wrapped as a message and fed into compiled LangGraph (`graph`).
3. `chatbot` node invokes Gemini model with the system persona + conversation state.
4. If the model emits a tool call, execution flows to the `ToolNode` which dispatches the matching Python function.
5. Tool output appended to state; control returns to `chatbot` until no further tool calls.
6. Streamed responses printed incrementally in `main.py`.
7. All turns + tool invocations logged to Langfuse; checkpoints persisted to Mongo.

## Provided Tools
- Search: Internet search via Serper API.
- scan_directory(dir): Lists entries in a directory.
- read_file(path): Reads and prints file content.
- write_file(path, content): Writes full content to a file.
- command_exec(cmd): Executes a shell command (stdout or error captured).
- analyze_code(path): Placeholder for code analysis (returns a summary stub; extendable).

## Environment Variables
Create a `.env` file (do NOT share real keys publicly). Required keys:
```
GOOGLE_API_KEY=your_google_genai_api_key
SERPER_API_KEY=your_serper_api_key
# Optional if enabling Tavily
TAVILY_API_KEY=your_tavily_key

# Langfuse observability (after launching docker-compose.langfuse.yml)
LANGFUSE_PUBLIC_KEY=pk_...
LANGFUSE_SECRET_KEY=sk_...
LANGFUSE_HOST=http://localhost:3000

# Mongo (if using external cluster)
MONGODB_URI=mongodb://localhost:27017
```
Replace any placeholder values. Never commit real secrets. The sample `.env` in the repo currently includes real-looking keys—rotate them immediately.

## Local Setup
### 1. Clone & Enter
```
git clone <repo-url>
cd Voice_Cursor
```

### 2. Python Environment
Use `pyenv` or `venv` (example with venv):
```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. (Optional) Install Editable Package
```
pip install -e .
```
This exposes the console script `voice-cursor` described in `setup.py`.

### 4. Start Supporting Services
MongoDB for checkpointing:
```
docker compose -f voice_cursor/docker-compose.checkpoint.yml up -d
```
Langfuse stack (observability + tracing):
```
docker compose -f voice_cursor/docker-compose.langfuse.yml up -d
```
After Langfuse boots, visit http://localhost:3000 to obtain / configure project keys.

### 5. Configure `.env`
Create / edit `.env` in `voice_cursor/` with your rotated keys.

### 6. Microphone Permissions (macOS)
Grant terminal (or VS Code) microphone access under System Settings > Privacy & Security > Microphone.

### 7. Test Audio Dependency
If PyAudio install fails on macOS:
```
brew install portaudio
pip install --no-cache-dir PyAudio
```

## Running the Assistant
Option A (module entry):
```
python -m voice_cursor.main
```
Option B (console script after editable install):
```
voice-cursor
```
Then choose input method:
```
Choose input method (type/voice): voice
```
Say something or type. Exit with: `quit`, `exit`, `q`, `bye`, `goodbye`.

## Adding a New Tool
1. Define function in `tools.py` decorated with `@tool`.
2. Import and append to the `tools` list in `graph.py`.
3. Re-run the program—LangGraph auto-binds it.

Example skeleton:
```python
@tool
def list_python_files(root: str) -> str:
    return "\n".join([f for f in os.listdir(root) if f.endswith('.py')])
```

## Extensibility Ideas / Roadmap
- Rich code analysis (AST diffs, complexity metrics).
- File-level edit planning before write operations.
- Guardrails for dangerous shell commands (confirmation layer / sandboxing).
- Streaming Web UI (Tailwind + minimal FastAPI server) using existing `package.json` tooling.
- Hybrid search (vector embedding + keyword) for codebase queries.
- Multi-turn agent memory summarization / compression.
- Role-based tool permissioning.

## Security Notes
- Rotate any leaked keys in the current `.env` immediately (they appear committed in history).
- Consider adding `.env` to `.gitignore` (if not already) and using a `.env.example` template.
- Restrict `command_exec` or add an allowlist to prevent destructive operations.

## Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| PyAudio install error | Missing PortAudio headers | `brew install portaudio` then reinstall PyAudio |
| No microphone detected | macOS permissions | Grant mic access in Privacy settings |
| Langfuse not reachable | Container not started / port conflict | Re-run compose; check `docker ps` |
| Mongo connection refused | DB not running | Start checkpoint compose file |
| Empty speech result | Ambient noise | Adjust timeout or use `r.adjust_for_ambient_noise(source)` |
| Tool never triggers | Model didn't call tool | Refine prompt or add explicit user instruction |

## License
Add your chosen license (MIT, Apache-2.0, etc.). Currently not specified.

## Attribution
Built with LangChain, LangGraph, Google Gemini, Langfuse, and open-source Python libraries.

---
Happy building with Voice Cursor / NexusCoder!
