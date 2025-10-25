"""
This module contains the interfaces to external LLMs;
There's an abstract base class LLM that can be subclassed to provide an interface to a model.
The class method LLM.for_model_name creates an instance of a subclass to interact with the API
This module should have no knowledge of the game itself.
"""

import os
from abc import ABC
from typing import Any, Dict, Self, List, Type
from openai import OpenAI
import google.generativeai
import anthropic
from groq import Groq


ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1/"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GROK_BASE_URL = "https://api.x.ai/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OLLAMA_BASE_URL = "http://localhost:11434/v1"


class LLM(ABC):
    """
    An abstract base class for LLMs
    Use LLM.for_model_name() to instantiate the appropriate subclass, then communicate with send()
    """

    model_names = []
    model_name: str
    temperature: float
    client: Any

    def __init__(self, model_name, temperature=1.0):
        self.model_name = model_name
        self.temperature = temperature
        self.setup_client()

    def setup_client(self):
        """
        Implemented by subclasses
        """
        pass

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implemented by subclasses
        :param system_prompt: The system prompt passed to the LLM
        :param user_prompt: The user prompt passed to the LLM
        :param max_tokens: Maximum number of tokens
        :return: the response from the LLM
        """
        pass

    def __repr__(self) -> str:
        """
        :return: A string version of the receiver
        """
        return f"<LLM {self.model_name} with temnp={self.temperature}>"

    @classmethod
    def model_map(cls) -> Dict[str, Type[Self]]:
        """
        Generate a mapping of Model Names to LLM classes, by looking at all subclasses of this one
        :return: a mapping dictionary from model name to LLM subclass
        """
        mapping = {}
        for llm in cls.__subclasses__():
            for model_name in llm.model_names:
                mapping[model_name] = llm
        return mapping

    @classmethod
    def for_model_name(cls, model_name: str, temperature=0.7) -> Self:
        """
        Given a particular model name, instantiate one of the subclasses of the receiver and initialize it
        :param model_name: The name of the model to be communicated with
        :param temperature: The temperature to be used in this model
        :return: an initialized instance of an LLM subclass
        """
        mapping = cls.model_map()
        llm_class = mapping[model_name]
        llm = llm_class(model_name, temperature)
        return llm

    @classmethod
    def all_model_names(cls) -> List[str]:
        """
        :return: a list of names of all the models supported
        """
        return list(cls.model_map().keys())


class GPT(LLM):
    model_names = [
        "gpt-3.5-turbo",
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.1",
        "o4-mini",
        "gpt-5",
        "gpt-5-nano",
        "gpt-5-mini",
    ]

    def setup_client(self):
        self.client = OpenAI()

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implementation for OpenAI / GPT
        :param system_prompt: The system prompt passed to the LLM
        :param user_prompt: The user prompt passed to the LLM
        :param max_tokens: Maximum number of tokens
        :return: the response from the LLM
        """
        effort = "low" if "gpt-5" in self.model_name else None
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            reasoning_effort=effort,
        )
        return completion.choices[0].message.content


class Claude(LLM):
    model_names = [
        "claude-3-5-sonnet-latest",
        # "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-4-sonnet-latest",
        "claude-sonnet-4-0",
        "claude-opus-4-1-20250805",
        "claude-sonnet-4-5",
        "claude-haiku-4-5",
    ]

    def setup_client(self):
        self.client = anthropic.Anthropic()

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implementation for Anthropic / Claude
        :param system_prompt: The system prompt passed to the LLM
        :param user_prompt: The user prompt passed to the LLM
        :param max_tokens: Maximum number of tokens
        :return: the response from the LLM
        """
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=0.5,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
        )
        return message.content[0].text


# class Gemini(LLM):
#     model_names = ["gemini-1.0-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]

#     def setup_client(self):
#         google.generativeai.configure()
#         self.client = google.generativeai.GenerativeModel(self.model_name)

#     def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
#         """
#         Implementation for Google / Gemini
#         :param system_prompt: The system prompt passed to the LLM
#         :param user_prompt: The user prompt passed to the LLM
#         :param max_tokens: Maximum number of tokens
#         :return: the response from the LLM
#         """
#         words = int(max_tokens * 0.75)
#         message = "First, here is a System Message to set context and instructions:\n\n"
#         message += system_prompt + "\n\n"
#         message += f"Now here is the User's Request - please respond in under {words} words:\n\n"
#         message += user_prompt + "\n"
#         response = self.client.generate_content(message)
#         first_candidate = response.candidates[0]

#         if first_candidate.content.parts:
#             myanswer1 = response.candidates[0].content.parts[0].text
#             return myanswer1
#         raise ValueError("Could not parse response from Gemini")


class Grok(LLM):
    model_names = ["grok-3", "grok-4", "grok-4-fast"]

    def setup_client(self):
        self.client = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url=GROK_BASE_URL)

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implementation for OpenAI / GPT
        :param system_prompt: The system prompt passed to the LLM
        :param user_prompt: The user prompt passed to the LLM
        :param max_tokens: Maximum number of tokens
        :return: the response from the LLM
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content


class Gemini(LLM):
    model_names = [
        "gemini-1.0-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ]

    def setup_client(self):
        self.client = OpenAI(api_key=os.getenv("GOOGLE_API_KEY"), base_url=GEMINI_BASE_URL)

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implementation for OpenAI / GPT
        :param system_prompt: The system prompt passed to the LLM
        :param user_prompt: The user prompt passed to the LLM
        :param max_tokens: Maximum number of tokens
        :return: the response from the LLM
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content


class GroqAPI(LLM):
    """
    A class to act as an interface to the remote AI, in this case Groq
    """

    model_names = [
        "deepseek-r1-distill-llama-70b",
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
        "openai/gpt-oss-120b",
    ]

    def setup_client(self):
        self.client = Groq()

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implementation for Groq
        :param system_prompt: The system prompt passed to the LLM
        :param user_prompt: The user prompt passed to the LLM
        :param max_tokens: Maximum number of tokens
        :return: the response from the LLM
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content
