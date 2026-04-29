import os
import argparse
import json
import re
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
    
    def convert_schema(s):
        if s is None:
            return None
        
        # Determine the type string
        res = {}
        if s.type:
            res["type"] = s.type.lower() if hasattr(s.type, 'lower') else str(s.type).lower()
        
        if s.description:
            res["description"] = s.description
            
        if res.get("type") == "object" and s.properties:
            res["properties"] = {k: convert_schema(v) for k, v in s.properties.items()}
            if s.required:
                res["required"] = s.required
                
        if res.get("type") == "array" and s.items:
            res["items"] = convert_schema(s.items)
            
        return res

    return {
        "type": "function",
        "function": {
            "name": gemini_schema.name,
            "description": gemini_schema.description,
            "parameters": convert_schema(gemini_schema.parameters)
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

        # Handle empty or errored response
        if not response.choices:
            print(f"Error: API returned no choices. Response: {response}")
            break

        assistant_msg = response.choices[0].message
        
        # Preserve reasoning_details if available (specific to OpenRouter)
        reasoning_details = getattr(assistant_msg, "reasoning_details", None)
        if not reasoning_details and hasattr(assistant_msg, "model_extra"):
            reasoning_details = assistant_msg.model_extra.get("reasoning_details")

        # --- LOGGING: Show what the model is doing ---
        print(f"\n[Iteration {iteration + 1}]")
        if reasoning_details:
            print("--- Thought ---")
            if isinstance(reasoning_details, list):
                for item in reasoning_details:
                    if isinstance(item, dict) and 'text' in item:
                        print(item['text'])
                    else:
                        print(str(item))
            else:
                print(str(reasoning_details))
            print("---------------")
        elif assistant_msg.content and "<thought>" in assistant_msg.content:
            # Handle models that put thoughts in content
            thought = re.search(r'<thought>(.*?)</thought>', assistant_msg.content, re.DOTALL)
            if thought:
                print(f"--- Thought ---\n{thought.group(1).strip()}\n---------------")
        
        if assistant_msg.tool_calls:
            print(f"Agent is calling {len(assistant_msg.tool_calls)} function(s):")
        elif assistant_msg.content:
            print(f"Agent response: {assistant_msg.content[:200]}...")

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
            # Sanitize function name (fixes model hallucinations like <|channel|>)
            func_name = tool_call.function.name.split('<')[0].split('?')[0].split(' ')[0].strip()
            
            try:
                func_args = json.loads(tool_call.function.arguments)
            except Exception:
                func_args = {}
            
            print(f" > Call: {func_name}({func_args})")

            # Inject the working directory into the arguments as required by functions
            func_args['working_directory'] = WORKING_DIRECTORY
            
            try:
                if func_name in function_map:
                    result = function_map[func_name](**func_args)
                else:
                    result = f"Error: Unknown function {func_name}"
            except Exception as e:
                result = f"Error executing function: {e}"

            print(f" < Result: {str(result)[:500]}{'...' if len(str(result)) > 500 else ''}")

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