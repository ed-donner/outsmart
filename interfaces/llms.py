"""
This module contains the interfaces to external LLMs;
There's an abstract base class LLM that can be subclassed to provide an interface to a model.
The class method LLM.for_model_name will create an instance of a subclass to interact with the API
"""

import os
from abc import ABC
from typing import Any, Dict, Self
from openai import OpenAI
import google.generativeai
import anthropic
import requests


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
    def model_map(cls) -> Dict[str, Any]:
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
    def for_model_name(cls, model_name: str, temperature=1.0) -> Self:
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


class GPT(LLM):

    model_names = [
        "gpt-3.5-turbo",
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106",
        "gpt-4o-mini",
    ]

    def setup_client(self):
        self.client = OpenAI()

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implemented by subclasses
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
            temperature=1.0,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content


class Claude(LLM):

    model_names = [
        "claude-3-5-sonnet-20240620",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    def setup_client(self):
        self.client = anthropic.Anthropic()

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implemented by subclasses
        :param system_prompt: The system prompt passed to the LLM
        :param user_prompt: The user prompt passed to the LLM
        :param max_tokens: Maximum number of tokens
        :return: the response from the LLM
        """
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
        )
        return message.content[0].text


class Gemini(LLM):

    model_names = [
        "gemini-pro",
    ]

    def setup_client(self):
        google.generativeai.configure()
        self.client = google.generativeai.GenerativeModel(self.model_name)

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implemented by subclasses
        :param system_prompt: The system prompt passed to the LLM
        :param user_prompt: The user prompt passed to the LLM
        :param max_tokens: Maximum number of tokens
        :return: the response from the LLM
        """
        words = int(max_tokens * 0.75)
        message = "First, here is a System Message to set context and instructions:\n\n"
        message += system_prompt + "\n\n"
        message += f"Now here is the User's Request - please respond in under {words} words:\n\n"
        message += user_prompt + "\n"
        response = self.client.generate_content(message)
        first_candidate = response.candidates[0]

        if first_candidate.content.parts:
            myanswer1 = response.candidates[0].content.parts[0].text
            return myanswer1
        raise ValueError("Could not parse response from Gemini")


class Llama(LLM):

    API_URL = "https://api-inference.huggingface.co/models/meta-llama/"
    model_names = ["Meta-Llama-3-8B"]

    def send(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Implemented by subclasses
        :param system_prompt: The system prompt passed to the LLM
        :param user_prompt: The user prompt passed to the LLM
        :param max_tokens: Maximum number of tokens
        :return: the response from the LLM
        """

        words = int(max_tokens * 0.75)
        message = "First, here is a System Message to set context and instructions:\n\n"
        message += system_prompt + "\n\n"
        message += f"Now here is the User's Request - please respond in under {words} words:\n\n"
        message += user_prompt + "\n"

        api_url = self.API_URL + self.model_name
        headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
        inputs = {"inputs": "message"}
        response = requests.post(api_url, headers=headers, json=inputs)
        result = response.json()
        return result
