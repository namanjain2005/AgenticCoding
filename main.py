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

gemini_api_key = os.environ.get('GEMINI_API_KEY')
if gemini_api_key is None:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

from google import genai
from google.genai import types

client = genai.Client(api_key=gemini_api_key)

MAX_ITERATIONS = 20

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    available_functions = [
        types.Tool(function_declarations=[schema_get_files_info]),
        types.Tool(function_declarations=[schema_get_file_content]),
        types.Tool(function_declarations=[schema_run_python_file]),
        types.Tool(function_declarations=[schema_write_file]),
    ]

    for iteration in range(MAX_ITERATIONS):
        resp = client.models.generate_content(
            model=config.MORE_PER_DAY_MODEL,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=available_functions,
                system_instruction=system_prompt
            ),
        )

        if resp is None:
            raise RuntimeError("Failed to get response from model")

        if resp.usage_metadata is None:
            raise RuntimeError("Empty usage metadata")

        if resp.candidates:
            for candidate in resp.candidates:
                
                non_thought_parts = [
                    part for part in candidate.content.parts
                    if not getattr(part, 'thought', False)
                ]
                if non_thought_parts:
                    messages.append(types.Content(
                        role="model",
                        parts=non_thought_parts
                    ))

        if not resp.function_calls:
            print(f"Final response:\n{resp.text}")
            return

        function_responses = []
        for function_call in resp.function_calls:
            if args.verbose:
                print(f" - Calling function: {function_call.name}({function_call.args})")

            function_call_result = call_function(function_call, args.verbose)

            if not function_call_result.parts:
                raise Exception(f"No parts in function call result for {function_call.name}")
            if function_call_result.parts[0].function_response is None:
                raise Exception(f"No function_response in result for {function_call.name}")
            if function_call_result.parts[0].function_response.response is None:
                raise Exception(f"No response body in function_response for {function_call.name}")

            function_responses.append(function_call_result.parts[0])

            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")

        if args.verbose:
            print(f"Iteration {iteration + 1} | Prompt tokens: {resp.usage_metadata.prompt_token_count} | Response tokens: {resp.usage_metadata.candidates_token_count}")

        messages.append(types.Content(role="user", parts=function_responses))


    print(f"Error: Agent did not produce a final response within {MAX_ITERATIONS} iterations.")
    exit(1)

if __name__ == "__main__":
    main()