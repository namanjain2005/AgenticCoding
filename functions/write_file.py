import os
from google.genai import types

def write_file(working_directory, file_path, content):
    try : 
        abs_working_dir = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(abs_working_dir, file_path))
        if os.path.commonpath([abs_working_dir, target_file]) != abs_working_dir:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if os.path.isdir(target_file):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        
        os.makedirs(os.path.dirname(target_file),exist_ok=True)

        with open(target_file,'w') as f:
            file_content = f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error : issue in writting fie ---  {e}'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Creates or overwrites a file in the permitted working directory with the provided content.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file relative to the working directory.",
            ),
            "content":types.Schema(
                type=types.Type.STRING,
                description="The full text content to write into the file.",
            ),
        },
        required=["file_path","content"]
    ),
)