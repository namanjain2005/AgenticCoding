from dotenv import load_dotenv
import os
import argparse

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
    resp = client.models.generate_content(model='gemini-2.5-flash',contents=messages)
    if resp is None:
        raise RuntimeError("failed to get resp")
    
    if resp.usage_metadata is None:
        raise RuntimeError("Empty usage metadata")

    print(resp.text)
    if args.verbose:
        print(f"UserPrompt: {messages}\nPrompt tokens : {resp.usage_metadata.prompt_token_count}\nResponse tokens : {resp.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    main()

