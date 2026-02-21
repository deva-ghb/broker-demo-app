"""
AI client wrapping Azure OpenAI and Google Gemini.
"""
import openai
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from typing import List, Optional, Tuple, Any
from pydantic import BaseModel
from settings import settings


class AIClient:
    """Unified AI client for Azure OpenAI and Gemini."""

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
        self.embedding_client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_deployment=settings.AZURE_OPENAI_EMBEDDING_MODEL,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )

    def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4.1-mini",
        tools: Optional[List[ChatCompletionToolParam]] = None,
    ) -> Tuple[str, Any, Any]:
        """Standard chat completion."""
        completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0,
            tools=tools if tools else None,
        )
        response = completion.choices[0].message.content or ""
        # Clean up code fences if present
        response = response.replace("```html", "").replace("```markdown", "").replace("```", "")
        tool_calls = completion.choices[0].message.tool_calls
        usage = completion.usage
        return response, tool_calls, usage

    def structured_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        response_structure: BaseModel = None,
        model: str = "gpt-4.1-mini",
    ) -> str:
        """Completion with structured output (JSON mode)."""
        response = self.client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=response_structure,
            temperature=0,
        )
        return response.choices[0].message.content

    async def completion_stream(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4.1-mini",
        tools: Optional[List[ChatCompletionToolParam]] = None,
    ):
        """Streaming chat completion."""
        stream = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0.2,
            tools=tools if tools else None,
            stream=True,
        )
        return stream

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Azure OpenAI."""
        response = self.embedding_client.embeddings.create(
            input=text,
            model=settings.AZURE_OPENAI_EMBEDDING_MODEL,
        )
        return response.data[0].embedding


# Global singleton
ai_client = AIClient()
