# from services.query_rag import QueryFromRAG
from utils.constants import CODE_WRITER, DEBUGGER_PROMPT, GENERATION_CONFIG
from utils.functions import get_df_info_as_dict
import google.generativeai as genai 
import os
import json
import requests
from PIL import Image
from io import BytesIO

from typing import Optional

import pandas as pd
import tempfile
import chainlit as cl


class CodeInterpreter:
    def __init__(self):
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-001', generation_config=GENERATION_CONFIG)
        self.code_writer_prompt = open(CODE_WRITER, "r").read()
        self.debugger_prompt = open(DEBUGGER_PROMPT, "r").read()
        
        
        
    def csv_loader_information(self, file_path: str):
        df = pd.read_csv(file_path, encoding="utf-8")
        schema = get_df_info_as_dict(df)
        file_name = file_path.split("/")[-1]
        
        return schema, file_name
        
    
    def writer(self, query: str, file_name: Optional[str] = None, schema: Optional[str] = None):
        if file_name and schema:
            update_context = self.code_writer_prompt.replace(
                "{User Question}", query
            ).replace("{File Path}", file_name).replace(
                "{DataFrame Column Names and Types}", str(schema)
            )
        else:
            update_context = self.code_writer_prompt.replace(
                "{User Question}", query
            )
        response = self.model.generate_content(update_context)
        self.response = json.loads(response.text)
        return json.loads(response.text)["code"]
    
    def execute(self, code: str, file_name: Optional[str]=None, file_path: Optional[str]=None):
        if file_name and file_path:
            files = {
                'code': (None, code),
                'file': (file_name, open(file_path, 'rb')) # Optional
            }
        else:
            files = {
                'code': (None, code),
            }
        # Send POST request
        response = requests.post(os.environ.get("COMPILER_URL"), files=files)
        return response.json()        
    
    def debugger(self, status: int, query: str, error_message: str, schema: Optional[str] = None):
        if type(status).__name__ != "int" or status != 0:
            if query and error_message and schema:
                debugged_code = self.debugger_prompt.replace("{User Question}", query).replace("{Error Message}", error_message).replace("{DataFrame Column Names and Types}", str(schema))  
            else:
                debugged_code = self.debugger_prompt.replace("{User Question}", query).replace("{Error Message}", error_message)
            response = self.model.generate_content(debugged_code)
            return json.loads(response.text)["code"]
        elif status == 0:
            return 1
    
    def return_images(self, response):
        images = []
        for img_path in response['images']:
            image_url = "http://localhost:5000" + img_path
            img_response = requests.get(image_url)

            
            # Display the image using PIL
            if img_response.status_code == 200:
                img = Image.open(BytesIO(img_response.content))
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    img.save(temp_file, format="PNG")  
                    temp_path = temp_file.name  
                    image = cl.Image(path=temp_path, name=f"image_{img_path}", display="inline")
                    images.append(image)
        return images
        
    def interpreter(self, query: str, file_path: Optional[str]=None):
        if file_path:
            schema, file_name = self.csv_loader_information(file_path)
            code = self.writer(query, file_name, schema)
            execution_result = self.execute(code, file_name, file_path)
            execution_status = execution_result["status"]
            error_message = execution_result["stdout"] + "\n" + execution_result["stderr"]
            if len(execution_result["images"]) > 0:
                images = self.return_images(execution_result)
            else:
                images = []
            debugger = self.debugger(
                status=execution_status,
                query=query,
                error_message=error_message,
                schema=schema,
            )
        else:
            code = self.writer(query)
            execution_result = self.execute(code)
            execution_status = execution_result["status"]
            error_message = execution_result["stdout"] + "\n" + execution_result["stderr"]
            if len(execution_result["images"]) > 0:
                images = self.return_images(execution_result)
            else:
                images = []
            debugger = self.debugger(
                status=execution_status,
                query=query,
                error_message=error_message
            )
        print(debugger)
        if debugger == 1:
            return {
                "status": execution_status,
                "stdout": execution_result["stdout"],
                "code": code,
                "images": images
                
            }
        else:
            return "error"
            