import chainlit as cl
import os
import sys
import asyncio

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handler import run_conversation

async def main(message):
    # print(f"[DEBUG] main function called with message: {message}")
    await run_conversation(cl.Message(content=message))

if __name__ == "__main__":
    message = input("Question: ")
    asyncio.run(main(message))