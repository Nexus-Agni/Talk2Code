import os
import subprocess
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.tools import Tool
from langchain_tavily import TavilySearch
from langfuse.decorators import observe
from langchain_core.tools import tool

load_dotenv()

serper_api_key = os.getenv("SERPER_API_KEY")
# tavily_api_key = os.getenv("TAVILY_API_KEY")

search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)


search_tool = Tool(
    name="Search",
    description="Search the internet for information",
    func=search.run,
)

# search_tool = TavilySearch(max_results=2)

@tool
def command_exec(command: str) -> str:
    """Execute a shell command and return its output."""
    print("🔑 ", command)
    
    try:
        result = subprocess.run(command, shell=True, check=True, text=True)
        return result.stdout or "Command executed successfully with no output."
    except subprocess.CalledProcessError as e:
        return f"Error:\n{e.stderr or str(e)}"

@tool   
def read_file(file_path: str) -> str:
    """Read a file."""
    print("🔑 ", file_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"📄 Read file: {file_path}")
            print("📜 Content:")
            print("-" * 40)
            print(content)
            print("-" * 40)
            return content
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                print(f"📄 Read file (latin-1 encoding): {file_path}")
                print("📜 Content:")
                print("-" * 40)
                print(content)
                print("-" * 40)
                return content
        except Exception as e:
            return f"Error reading file: {e}"

@tool
def write_file(file_path: str, content: str) -> str:
    """Write to a file."""
    print("🔑 ", file_path)
    print("🔑 ", content)
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            print(f"📝 Wrote to file: {file_path}")
            return f"File {file_path} written successfully"
    except Exception as e:
        return f"Error writing file: {e}"
    
@tool
def scan_directory(directory: str) -> str:
    """Scan a directory."""
    print("🔑 ", directory)
    try:
        files = os.listdir(directory)
        print(f"📂 Scanned directory: {directory} with files: {files}")
        return files
    except Exception as e:
        return f"Error scanning directory: {str(e)}"
    
@tool
def analyze_code(file_path: str) -> str:
    """Analyze a file."""
    print("🔑 ", file_path)
    with open(file_path, 'r') as file:  
        content = file.read()
        return f"Analyzed code in {file_path}."
    

