import os
import subprocess
def run_python_file(working_directory, file_path:str, args=None):
    try : 
        abs_working_dir = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(abs_working_dir, file_path))
        if os.path.commonpath([abs_working_dir, target_file]) != abs_working_dir:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
    
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_file]
        if args : 
            command.extend(args)

        completedProcessResult = subprocess.run(command,cwd=abs_working_dir,text=True,capture_output=True,timeout=30)
        output = []

        if completedProcessResult.returncode != 0:
            output.append(f"Process exited with code {completedProcessResult.returncode}")
        if not completedProcessResult.stdout and not completedProcessResult.stderr:
            output.append("No output produced")
        if completedProcessResult.stdout:
            output.append(f"STDOUT:\n{completedProcessResult.stdout}")
        if completedProcessResult.stderr:
            output.append(f"STDERR:\n{completedProcessResult.stderr}")
        return "\n".join(output)
        

    except Exception as e:
        return f'Error : issue in running python file ---  {e}'