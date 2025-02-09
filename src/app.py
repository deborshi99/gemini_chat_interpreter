import chainlit as cl
from dotenv import load_dotenv
from services.router import Router
from services.code_interpreter import CodeInterpreter
from services.general_conversation import GeneralConv
import logging
from typing import Optional

from utils.functions import get_latest_folder_and_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Initialize services
router = Router()
code_interpreter = CodeInterpreter()
general_conv = GeneralConv()
logger.info("Services initialized")


async def handle_general_conversation(message: str):
    """Handles general conversation requests"""
    response = general_conv.general_response(message)
    await cl.Message(content=response).send()
    logger.info("General response sent")


async def handle_code_interpretation(message: str, file_path: Optional[str]=None):
    """Handles code interpretation requests"""
    if file_path:
        # await cl.Message(content=file_path).send()
        response = code_interpreter.interpreter(message, file_path=file_path)
        if isinstance(response, dict):
            code = response["code"]
            await cl.Message(content=response["code"]).send()
            await cl.Message(content=f"result: {response['stdout']}", elements=response["images"]).send()
        else:
            await cl.Message(content=response).send()
            

    else:
        response = code_interpreter.interpreter(message)
        if isinstance(response, dict):
            code = response["code"]
            await cl.Message(content=response["code"]).send()
            await cl.Message(content=f"result: {response['stdout']}", elements=response["images"]).send()
        else:
            await cl.Message(content=response).send()

    logger.info("Code interpretation response sent")


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    logger.info(f"Received message: {message.content}")
    # await cl.Message(content="outside").send()

    try:
        # await cl.Message(content="inside").send()
        async with cl.Step(name="Routing Message"):
            # await cl.Message(content="inside step").send()
            router_response = router.router_response(message.content)
            logger.info(f"Router response type: {router_response}")
            await cl.Message(content=f"Router response type: {router_response}").send()

            if router_response == "general":
                await handle_general_conversation(message.content)
            
            elif router_response == "aaci":
                base_path = ".files/"
                _, file_path = get_latest_folder_and_file(base_path)
                if file_path is None:
                    await cl.Message(content="No file attached").send()
                    await handle_code_interpretation(message.content)
                else:
                    
                    await handle_code_interpretation(message.content, file_path)
                    

            else:
                await cl.Message(content="Sorry, I couldn't determine how to process your request.").send()
                logger.warning("Unhandled router response")

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        await cl.Message(content=f"An error occurred: {str(e)}. Please try again.").send()


if __name__ == "__main__":
    cl.run()
