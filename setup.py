from setuptools import setup, find_packages

setup(
    name="voice-cursor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "SpeechRecognition",
        "PyAudio",
        "langchain",
        "langchain-google-genai",
        "langgraph",
        "langgraph-checkpoint",
        "langgraph-checkpoint-mongodb",
        "pymongo",
        "langfuse"
    ],
    entry_points={
        "console_scripts": [
            "voice-cursor=main:main",
        ],
    },
)