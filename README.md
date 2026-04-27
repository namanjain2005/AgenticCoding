# AgenticCodingAgent

A lightweight CLI chatbot powered by Google Gemini AI with agentic loop capabilities for iterative problem-solving.

## Features

- **CLI Interface**: Simple command-line interaction for AI queries.
- **Gemini Integration**: Uses `google-genai` for high-performance language model responses.
- **Modular Functions**: Includes utility functions for file operations (reading content, gathering file info, writing files).
- **Calculator Module**: A sample package demonstrating modular project structure and testing.

## Installation

This project uses `uv` or `pip` for dependency management.

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install .
    ```
    *(Note: Dependencies are listed in `pyproject.toml`)*

3.  Set up your environment variables:
    Create a `.env` file in the root directory and add your Gemini API key:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

## Usage

Run the main chatbot script with a prompt:

```bash
python main.py "How does agentic AI work?"
```

### Options

- `--verbose`: Enable detailed output including token counts and prompt metadata.

## Project Structure

- `main.py`: Entry point for the CLI chatbot.
- `functions/`: Core utility functions for file and system operations.
- `calculator/`: Example logic and package structure.
- `config.py`: Configuration management.

## Testing

Run the included test suite to verify functionality:

```bash
python -m pytest
```
