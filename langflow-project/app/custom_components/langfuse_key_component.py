from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message
import os

class LangfuseKeyComponent(Component):
    display_name = "Langfuse Secret Key"
    description = "Affiche la clé secrète Langfuse"
    icon = "key"
    name = "LangfuseKey"

    inputs = [
        MessageTextInput(
            name="tool_placeholder",
            display_name="Tool Placeholder",
            tool_mode=True,
            advanced=True,
            info="A placeholder input for tool mode.",
        ),
    ]

    outputs = [
        Output(display_name="Message", name="message", method="build_message"),
    ]

    async def build_message(self) -> Message:
        key = os.getenv("LANGFUSE_SECRET_KEY", "Non définie")
        message = Message(content=key)
        self.status = key
        return message