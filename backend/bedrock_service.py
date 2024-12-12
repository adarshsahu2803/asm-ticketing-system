# backend/bedrock_service.py
import boto3
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class BedrockService:
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    def classify_and_guide_ticket(self, content: str) -> Dict[str, Any]:
        prompt = f"""
        Please analyze the following support ticket and provide classification and guidance in the following JSON format:
        {{
            "category": "<Classified/Prioritized/Technical/Account/Billing/Feature Request/Other>",
            "urgency": "<High/Medium/Low>",
            "estimated_time": <number in hours>,
            "justification": "<your reasoning for the classification>",
            "is_generic": <true/false>,
            "self_service_guide": {{
                "can_self_resolve": <true/false>,
                "steps": [list of steps if can_self_resolve is true],
                "resources": [list of suggested resources or documentation],
                "reason": "<explanation of why this can or cannot be self-resolved>"
            }}
        }}

        Rules for classification:
        1. Use "Classified" if the ticket contains sensitive information
        2. Use "Prioritized" if the ticket indicates system downtime or critical impact
        3. For other cases, use the most appropriate category
        4. Mark is_generic as true if the issue is common and can be self-resolved
        5. Provide step-by-step guidance if the issue can be resolved by the user

        Ticket content: {content}
        """
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens_to_sample": 1000,
            "temperature": 0.0,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant: {{" 
        })
        
        try:
            response = self.client.invoke_model(
                modelId='anthropic.claude-v2',
                body=body
            )
            response_body = json.loads(response['body'].read())
            response_text = "{" + response_body.get('completion', '').strip()
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                return {
                    "category": "Other",
                    "urgency": "Medium",
                    "estimated_time": 24,
                    "justification": "Error parsing response",
                    "is_generic": False,
                    "self_service_guide": {
                        "can_self_resolve": False,
                        "steps": [],
                        "resources": [],
                        "reason": "Error processing request"
                    }
                }
        except Exception as e:
            return {
                "category": "Unclassified",
                "urgency": "Medium",
                "estimated_time": 24,
                "justification": f"Error: {str(e)}",
                "is_generic": False,
                "self_service_guide": {
                    "can_self_resolve": False,
                    "steps": [],
                    "resources": [],
                    "reason": "Service error"
                }
            }
        
    def generate_response(self, ticket_content: str) -> str:
        prompt = f"""
        Generate a helpful response for the following support ticket:
        
        {ticket_content}
        
        Provide a professional and detailed response addressing the user's concerns.
        """
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.7,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:"
        })
        
        try:
            response = self.client.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                body=body
            )
            response_body = json.loads(response['body'].read())
            return response_body.get('completion', '').strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"