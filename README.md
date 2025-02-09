# Chat Interpreter

Interactive chatbot using gemini-flash-2.0 and Chainlit.

## Introduction

Chat Interpreter is an interactive chatbot application that leverages gemini-flash-2.0 and Chainlit to provide advanced conversational capabilities. The project is designed to interpret code, handle general conversations, and provide insightful responses based on user queries.

**Note:** The application is not fully functional at the moment. Proper user sessions and code generation (including training a model to avoid generating malicious code) are still under development.



# Chat Interpreter

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/deborshi99/chat_interpreter.git
    cd chat_interpreter
    ```

2. Install Docker on your system:
    - **For Windows:** Follow the instructions [here](https://docs.docker.com/desktop/install/windows-install/).
    - **For macOS:** Follow the instructions [here](https://docs.docker.com/desktop/install/mac-install/).
    - **For Linux:** Follow the instructions [here](https://docs.docker.com/engine/install/).

3. Build the `code_compiler` Docker image:
    ```sh
    docker build -t python_compiler -f dockerfiles/dockerfile.compler .
    ```

4. **Note**: For Future User, build the `chainlit_ui` Docker image:
    ```sh
    docker build -t chainlit_ui -f dockerfiles/dockerfile.chainlitui .
    ```

## Usage

1. Run the `code_compiler` container:
    ```sh
    docker run -i -p 5000:5000 python_compiler
    ```

2. To run the `chainlit_ui`, follow these steps:
    ```sh
    cd src
    pip install -r ../requirements.txt
    chainlit run app.py
    ```

3. Open a web browser and navigate to `http://localhost:8000` to view the UI.

## Docker Compose

In the future, you can use Docker Compose to simplify running both services. The `docker-compose.yml` file is already set up for this purpose. To use Docker Compose, run:

```sh
docker-compose up
```

This command will build and start both the `code_compiler` and `chainlit_ui` services, making it easier to manage and run the application.

## Prompts

The [prompts](http://_vscodecontentref_/15) directory contains various prompt templates used by the application:

- `code_requirements.txt`: Guidelines for code requirements.
- [code_writter.txt](http://_vscodecontentref_/16): Template for generating code based on user queries.
- `debugging_prompt.txt`: Template for debugging code.
- `general_question_answer.txt`: Template for handling general questions.
- `router_prompt.txt`: Template for routing messages.
