from autogen.agentchat import AssistantAgent, UserProxyAgent, Agent
from typing import Dict, Optional, Union
import chainlit as cl
import json
from config import redis_client, SELECTED_VALUE

def save_message_to_redis(pn_rm, message, role, name):
    conversation_key = f"conversation_history_{pn_rm}"
    # Ensure message content is always saved as a string
    if isinstance(message, dict) and "content" in message:
        message_content = message["content"]
    else:
        message_content = message

    new_message = {"content": message_content, "role": role, "name": name}
    redis_client.rpush(conversation_key, json.dumps(new_message))
    print(f"[DEBUG] Attempting to save message for {pn_rm}: {new_message}")

    # Verify the message is saved
    last_message = json.loads(redis_client.lindex(conversation_key, -1))
    if last_message == new_message:
        print(f"[DEBUG] Successfully saved message for {pn_rm}: {new_message}")
    else:
        print(f"[ERROR] Failed to save message for {pn_rm}")

async def ask_helper(func, **kwargs):
    res = await func(**kwargs).send()
    while not res:
        res = await func(**kwargs).send()
    return res

class ChainlitAssistantAgent(AssistantAgent):
    """
    Wrapper for AutoGens Assistant Agent
    """
    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> bool:
        # Only display messages from Spokesman to the user
        if self.name == "Spokesman":
            cl.run_sync(
                cl.Message(
                    content=message if isinstance(message, str) else message.get('content', ''),
                    author="Assistant",
                ).send()
            )

        self.pn_rm = SELECTED_VALUE
        # Save the message to Redis with special handling for initial interaction
        if 'Previous chat history:' in message:
            # Extract the CONTEXT part
            context_part = message.split('\n\nCurrent question: ')[-1]
            save_message_to_redis(self.pn_rm, context_part, "assistant", self.name)
        else:
            save_message_to_redis(self.pn_rm, message, "assistant", self.name)

        print(f"[DEBUG] ChainlitAssistantAgent.send called with message: {message}, recipient: {recipient.name}")
        super(ChainlitAssistantAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )
        return True
    
class ChainlitUserProxyAgent(UserProxyAgent):
    """
    Wrapper for AutoGens UserProxy Agent. Simplifies the UI by adding CL Actions.
    """
    def get_human_input(self, prompt: str) -> str:
        print(f"[DEBUG] ChainlitUserProxyAgent.get_human_input called with prompt: {prompt}")
        # Capture user input without displaying the prompt message
        reply = cl.run_sync(ask_helper(cl.AskUserMessage, content="", timeout=60))
        return reply["output"].strip()

    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        # Only display messages from Spokesman to the user
        if recipient.name == "Spokesman":
            cl.run_sync(
                cl.Message(
                    content=message if isinstance(message, str) else message.get('content', ''),
                    author="Assistant",
                ).send()
            )
        self.pn_rm = '138626'
        # Save the message to Redis with special handling for initial interaction
        if 'Previous chat history:' in message:
            # Extract the CONTEXT part
            context_part = message.split('\n\nCurrent question: ')[-1]
            save_message_to_redis(self.pn_rm, context_part, "user", self.name)
        else:
            save_message_to_redis(self.pn_rm, message, "user", self.name)

        print(f"[DEBUG] ChainlitUserProxyAgent.send called with message: {message}, recipient: {recipient.name}")
        super(ChainlitUserProxyAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )