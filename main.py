import os
import argparse
import json
from dotenv import load_dotenv
from openai import OpenAI

import config
from prompts import system_prompt
# Import schemas and implementations
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not found in environment or .env file")

# Initialize OpenAI client with OpenRouter base URL
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

MAX_ITERATIONS = 20
WORKING_DIRECTORY = './calculator'

def to_openai_tool(gemini_schema):
    """Converts Gemini FunctionDeclaration to OpenAI tool format automatically."""
    params = gemini_schema.parameters
    props = {}
    for k, v in params.properties.items():
        # Handle types (Gemini uses uppercase/Enums, OpenAI uses lowercase strings)
        prop_type = v.type.lower() if hasattr(v.type, 'lower') else str(v.type).lower()
        props[k] = {"type": prop_type, "description": v.description}
        
    return {
        "type": "function",
        "function": {
            "name": gemini_schema.name,
            "description": gemini_schema.description,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": params.required or []
            }
        }
    }

# Cleanly generate tools list from imported schemas using the helper
tools = [to_openai_tool(s) for s in [
    schema_get_files_info, 
    schema_get_file_content, 
    schema_run_python_file, 
    schema_write_file
]]

# Map function names to actual implementations
function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

def main():
    parser = argparse.ArgumentParser(description="Agentic Chatbot (OpenRouter)")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # Initial message history
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt}
    ]

    for iteration in range(MAX_ITERATIONS):
        # API Call with Reasoning enabled for OpenRouter
        response = client.chat.completions.create(
            model=config.MORE_PER_DAY_MODEL,
            messages=messages,
            tools=tools,
            extra_body={"reasoning": {"enabled": True}}
        )

        assistant_msg = response.choices[0].message
        
        # Preserve reasoning_details if available (specific to OpenRouter)
        reasoning_details = getattr(assistant_msg, "reasoning_details", None)
        if not reasoning_details and hasattr(assistant_msg, "model_extra"):
            reasoning_details = assistant_msg.model_extra.get("reasoning_details")

        # Create assistant message dictionary for history
        assistant_dict = {
            "role": "assistant",
            "content": assistant_msg.content,
        }
        
        if assistant_msg.tool_calls:
            assistant_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in assistant_msg.tool_calls
            ]
        
        # Crucial for continuing reasoning chain on OpenRouter
        if reasoning_details:
            assistant_dict["reasoning_details"] = reasoning_details

        messages.append(assistant_dict)

        # If no tool calls, the model has finished its task
        if not assistant_msg.tool_calls:
            print(f"Final response:\n{assistant_msg.content}")
            return

        # Process Tool Calls
        for tool_call in assistant_msg.tool_calls:
            func_name = tool_call.function.name
            try:
                func_args = json.loads(tool_call.function.arguments)
            except Exception:
                func_args = {}
            
            if args.verbose:
                print(f" - Calling function: {func_name}({func_args})")

            # Inject the working directory into the arguments as required by functions
            func_args['working_directory'] = WORKING_DIRECTORY
            
            try:
                if func_name in function_map:
                    result = function_map[func_name](**func_args)
                else:
                    result = f"Error: Unknown function {func_name}"
            except Exception as e:
                result = f"Error executing function: {e}"

            if args.verbose:
                print(f"-> Result length: {len(str(result))} characters")

            # Append the tool result to history
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        if args.verbose:
            print(f"Iteration {iteration + 1} | Model: {config.MORE_PER_DAY_MODEL}")

    print(f"Error: Agent did not produce a final response within {MAX_ITERATIONS} iterations.")
    exit(1)

if __name__ == "__main__":
    main()