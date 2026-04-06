import abc
import os
from typing import Any, Dict, Type
from pydantic import BaseModel, Field

class BaseTool(abc.ABC):
    """Abstract base class for all agent tools."""
    name: str
    description: str
    parameters: Type[BaseModel]

    @abc.abstractmethod
    def execute(self, **kwargs) -> str:
        """Executes the tool's core logic and returns a string result."""
        pass

    def get_openai_definition(self) -> Dict[str, Any]:
        """Provides the tool schema in formatted for OpenAI's tool-calling API."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters.model_json_schema()
            }
        }

# --- Concrete Tools ---

class ReadFileArgs(BaseModel):
    filepath: str = Field(description="The absolute or relative path to the file to read.")

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Reads and returns the full content of a specified text file."
    parameters = ReadFileArgs

    def execute(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class WriteFileArgs(BaseModel):
    filepath: str = Field(description="The path where the file should be written.")
    content: str = Field(description="The multi-line string content to write.")

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Creates or overwrites a file with the provided content."
    parameters = WriteFileArgs

    def execute(self, filepath: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to '{filepath}'."
        except Exception as e:
            return f"Error writing file: {str(e)}"

class ListDirectoryArgs(BaseModel):
    directory_path: str = Field(description="The path to the folder to list.")

class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "Returns a list of all files in a specific directory."
    parameters = ListDirectoryArgs

    def execute(self, directory_path: str) -> str:
        if not os.path.isdir(directory_path):
            return f"Error: '{directory_path}' is not a directory."
        try:
            files = os.listdir(directory_path)
            return "\n".join(files) if files else "Directory is empty."
        except Exception as e:
            return f"Error listing directory: {str(e)}"
