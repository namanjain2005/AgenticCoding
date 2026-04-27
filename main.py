from dotenv import load_dotenv
import os
import argparse
import config
from prompts import system_prompt
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from functions.call_function import call_function

load_dotenv()

gemini_api_key =  os.environ.get('GEMINI_API_KEY')
if gemini_api_key is None:
    raise RuntimeError

from google import genai
from google.genai import types

client = genai.Client(api_key=gemini_api_key)

def main():

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    # Now we can access `args.user_prompt`

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])] # for now just user prompt

    available_functions = [
        types.Tool(function_declarations=[schema_get_files_info],),
        types.Tool(function_declarations=[schema_get_file_content],),
        types.Tool(function_declarations=[schema_run_python_file],),
        types.Tool(function_declarations=[schema_write_file],),
    ]   

    resp = client.models.generate_content(
        model=config.MORE_PER_DAY_MODEL,
        contents=messages,
        config=types.GenerateContentConfig(tools = available_functions,system_instruction=system_prompt),
    )

    if resp is None:
        raise RuntimeError("failed to get resp")
    
    if resp.usage_metadata is None:
        raise RuntimeError("Empty usage metadata")

    print(f"response text is {resp.text}")
    function_results = []
    if resp.function_calls:
        for function_call in resp.function_calls:
            # print(f"Calling function: {function_call.name}({function_call.args})")
            function_call_result = call_function(function_call,args.verbose)
            if not function_call_result.parts:
                raise Exception
            if function_call_result.parts[0].function_response == None:
                raise Exception
            if function_call_result.parts[0].function_response.response == None:
                raise Exception
            function_results.append(function_call_result.parts[0].function_response.response)
            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")
            
            
    if args.verbose:
        print(f"UserPrompt: {messages}\nPrompt tokens : {resp.usage_metadata.prompt_token_count}\nResponse tokens : {resp.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    main()

