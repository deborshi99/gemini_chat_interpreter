from google.ai.generativelanguage_v1beta.types import content

ROUTER_PROMPT = "../prompts/router_prompt.txt"
CODE_WRITER = "../prompts/code_writter.txt"
DEBUGGER_PROMPT = "../prompts/debugging_prompt.txt"
GENERAL_CONVERSATION = "../prompts/general_question_answer.txt"

# Create the model
GENERATION_CONFIG = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "code": content.Schema(
        type = content.Type.STRING,
      ),
    },
  ),
  "response_mime_type": "application/json",
}