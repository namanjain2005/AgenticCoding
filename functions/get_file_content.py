import os
import config
from google.genai import types

def get_file_content(working_directory, file_path):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(abs_working_dir, file_path))
        if os.path.commonpath([abs_working_dir, target_file]) != abs_working_dir:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        if not  os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_file, "r") as f:
            content = f.read(config.MAX_CHARS)

            #After reading the first MAX_CHARS...
            if f.read(1): # this needs to be under f open 
                content += f'[...File "{file_path}" truncated at {config.MAX_CHARS} characters]'
        return content
    except Exception as e:
        return f"Error : getting file content ---  {e}"

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Get Content of File with given file_path in specified working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file relative to the working directory.",
            ),
        },
        required=["file_path"]
    ),
)