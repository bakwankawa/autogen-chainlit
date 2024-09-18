import json
from config import redis_client, SELECTED_VALUE, gpt4_config
import chainlit as cl
import autogen

async def ask_helper(func, **kwargs):
    res = await func(**kwargs).send()
    while not res:
        res = await func(**kwargs).send()
    return res

async def load_conversation_history(pn_rm, pair_count):
    conversation_key = f"conversation_history_{pn_rm}"
    # Load all conversation history from Redis
    history = redis_client.lrange(conversation_key, 0, -1)  # Removed await

    # print(f"[DEBUG] Raw history data from Redis for {pn_rm}: {history}")
    
    loaded_history = []
    for item in history:
        try:
            loaded_item = json.loads(item)
            # print(f"[DEBUG] Loaded item from Redis: {loaded_item}")
            # If the loaded item is a list, extend the loaded_history list
            if isinstance(loaded_item, list):
                loaded_history.extend(loaded_item)
            else:
                loaded_history.append(loaded_item)
        except json.JSONDecodeError as e:
            # print(f"[ERROR] JSON decode error: {e}, item: {item}")
            continue

    # print(f"[DEBUG] Loaded history after parsing: {loaded_history}")

    # Filter only 'Admin' and 'Spokesman' messages
    admin_messages = [message for message in loaded_history if message.get('name') == 'Admin']
    spokesman_messages = [message for message in loaded_history if message.get('name') == 'Spokesman']

    # print(f"[DEBUG] Admin messages: {admin_messages}")
    # print(f"[DEBUG] Spokesman messages: {spokesman_messages}")

    # Get the last N pairs of messages from 'Admin' and 'Spokesman'
    admin_messages = admin_messages[-pair_count:]
    spokesman_messages = spokesman_messages[-pair_count:]

    # print(f"[DEBUG] Filtered Admin messages: {admin_messages}")
    # print(f"[DEBUG] Filtered Spokesman messages: {spokesman_messages}")

    # Interleave the messages
    filtered_history = []
    for admin_msg, spokesman_msg in zip(admin_messages, spokesman_messages):
        filtered_history.append(admin_msg)
        filtered_history.append(spokesman_msg)
    
    # print(f"[DEBUG] Final interleaved conversation history: {filtered_history}")
    return filtered_history


@cl.on_chat_start
async def on_chat_start():
    try:
        from app.agent import admin, manager, spokesman, researcher_internal, researcher_external, analyst, executor
        cl.user_session.set("admin", admin)
        cl.user_session.set("manager", manager)
        cl.user_session.set("spokesman", spokesman)
        cl.user_session.set("researcher_internal", researcher_internal)
        cl.user_session.set("researcher_external", researcher_external)
        cl.user_session.set("analyst", analyst)
        cl.user_session.set("executor", executor)
        
        # # Check if history is already loaded
        # if not cl.user_session.get("history_loaded"):
        #     # Load the last 5 conversation histories
        #     conversation_history = await load_conversation_history(SELECTED_VALUE, 3)
            
        #     if conversation_history:
        #         for message in conversation_history:
        #             # print(f"[DEBUG] Processing message: {message}")
        #             # Determine the author based on the message's name
        #             if message.get('name') == 'Admin':
        #                 author = 'You'
        #             elif message.get('name') == 'Spokesman':
        #                 author = 'Assistant'
        #             else:
        #                 author = message.get('name', 'Unknown')  # Default to 'Unknown' if neither Admin nor Spokesman
                    
        #             # print(f"[DEBUG] Sending message with content: {message.get('content')} and author: {author}")
        #             await cl.Message(content=message.get('content', ''), author=author).send()
        #         cl.user_session.set("history_loaded", True)
        #     else:
        #         msg = cl.Message(content=f"Hello! What task would you like to get done today?", author="Admin")
        #         await msg.send()
        msg = cl.Message(content=f"Hello! What task would you like to get done today?", author="Admin")
        await msg.send()
    except Exception as e:
        print("Error: ", e)

@cl.on_message
async def run_conversation(message: cl.Message):
    try:
        CONTEXT = message.content
        MAX_ITER = 20

        admin = cl.user_session.get("admin")
        manager = cl.user_session.get("manager")
        spokesman = cl.user_session.get("spokesman")
        researcher_internal = cl.user_session.get("researcher_internal")
        researcher_external = cl.user_session.get("researcher_external")
        analyst = cl.user_session.get("analyst")
        executor = cl.user_session.get("executor")

        disallowed_transition = {
            manager: [admin],
            admin: [researcher_external, researcher_internal, analyst],
            researcher_external: [manager, spokesman, admin],
            researcher_internal: [manager, spokesman, admin],
            analyst: [manager, admin]
        }

        group_chat = cl.user_session.get("group_chat")
        if group_chat is None:
            group_chat = autogen.GroupChat(
                agents=[admin, manager, spokesman, researcher_external, researcher_internal, analyst, executor],
                allowed_or_disallowed_speaker_transitions=disallowed_transition,
                speaker_transitions_type='disallowed',
                messages=[],
                max_round=MAX_ITER,
                speaker_selection_method="auto"
            )
            cl.user_session.set("group_chat", group_chat)

        chat_manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=gpt4_config,
            system_message="You are a Chat Manager, responsible for managing chat between multiple Agents. If the user asks a complex query that needs collaboration from other Agents to answer, please ask the Manager. If the user asks a simple query or small talk, please ask the Spokesman."
        )

        if len(group_chat.messages) == 0:
            # # Preload conversation history
            # conversation_history = await load_conversation_history(SELECTED_VALUE, 3)
            # # print(f"[DEBUG] Preloaded conversation history: {conversation_history}")
            # history_content = " ".join([msg.get('content', '') for msg in conversation_history])
            # message_content = f"Previous chat history:{history_content} \n\nCurrent question: {CONTEXT}"
            message_content = CONTEXT
            
            await cl.make_async(admin.initiate_chat)(chat_manager, message=message_content)

            # Save only the new context to the conversation history
            group_chat.messages.append({"name": "Admin", "content": CONTEXT})
        elif len(group_chat.messages) < MAX_ITER:
            await cl.make_async(admin.send)(chat_manager, message=CONTEXT)
        elif len(group_chat.messages) == MAX_ITER:
            await cl.make_async(admin.send)(chat_manager, message="exit")

    except Exception as e:
        print(f"[DEBUG] Error in run_conversation: {e}")