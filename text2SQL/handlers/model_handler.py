import os
import yaml
from abc import ABC, abstractmethod

class LLMHandler(ABC):
    @abstractmethod
    def configure(self):
        pass

    @abstractmethod
    def start_chat(self, system_instruction, history=None):
        pass

    @abstractmethod
    def send_message(self, message):
        pass