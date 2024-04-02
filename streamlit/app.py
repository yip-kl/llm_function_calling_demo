import os
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage
from utils.funcs.db_interactions import get_categories, get_items, purchase_item
from utils.funcs.rag_pipeline import rag_pipeline_func
from utils.callback import StreamlitCallbackHandler
import json
from haystack.dataclasses import ChatMessage, ChatRole
from haystack.components.generators.chat import OpenAIChatGenerator
import streamlit as st

# Load the API key from the .env file, alternatively declare it in the terminal
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

# Prepare the OpenAIChatGenerator for Streamlit
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get a list of items from the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "ids": {
                        "type": "string",
                        "description": "Comma separated list of item ids to fetch",
                    },
                    "categories": {
                        "type": "string",
                        "description": "Comma separated list of item categories to fetch",
                    },
                },
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "purchase_item",
            "description": "Purchase a particular item",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The given product ID, product name is not accepted here. Please obtain the product ID from the database first.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of items to purchase",
                    },
                },
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rag_pipeline_func",
            "description": "Get information from hotel brochure",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to use in the search. Infer this from the user's message. It should be a question or a statement",
                    }
                },
                "required": ["query"],
            },
        },
    }
]

context = f"""You are an assistant to tourists visiting a hotel.
You have access to a database of items (which includes {get_categories()}) that tourists can buy, you also have access to the hotel's brochure.
If the tourist's question cannot be answered by the database, you can refer to the brochure.
If the tourist's question cannot be answered by the brochure, you can ask the tourist to ask the hotel staff.
"""

available_functions = {"get_items": get_items, "purchase_item": purchase_item,"rag_pipeline_func": rag_pipeline_func}

# Streamlit chat interface
if "messages" not in st.session_state:
    st.session_state["messages"] = [ChatMessage.from_system(context)]

# Only show chat messages from the user and the assistant. Initial system prompt and function calls are hidden.
for message in st.session_state.messages:
    if message.is_from(ChatRole.USER) | message.is_from(ChatRole.ASSISTANT):
        with st.chat_message(message.role.name):
            st.markdown(message.content)

if prompt := st.chat_input("ENTER YOUR MESSAGE 👇"):
    st.session_state.messages.append(ChatMessage.from_user(prompt))
    with st.chat_message("USER"):
        st.markdown(prompt)

    with st.chat_message("ASSISTANT"):
        # Initialize the callback handler, which creates an empty container for the responses to be streamed into
        st_callback = StreamlitCallbackHandler(st.empty())
        # Initialize the chat generator
        chat_generator = OpenAIChatGenerator(
                api_key=Secret.from_env_var("OPENROUTER_API_KEY"),
                api_base_url="https://openrouter.ai/api/v1",
                model="openai/gpt-4-turbo-preview",
                streaming_callback=st_callback.on_llm_new_token)
        while True:
            # Run the chat generator, tool calls will be looped through and executed, until an assistant reply is generated
            response = chat_generator.run(messages=st.session_state.messages, generation_kwargs={"tools": tools})

            if response and response["replies"][0].meta["finish_reason"] == "tool_calls":
                function_calls = json.loads(response["replies"][0].content)

                for function_call in function_calls:
                    ## Parse function calling information
                    function_name = function_call["function"]["name"]
                    function_args = json.loads(function_call["function"]["arguments"])

                    ## Find the correspoding function and call it with the given arguments
                    function_to_call = available_functions[function_name]
                    function_response = function_to_call(**function_args)

                    ## Append function response to the messages list using `ChatMessage.from_function`
                    st.session_state.messages.append(ChatMessage.from_function(content=json.dumps(function_response), name=function_name))
            # Regular conversation
            else:
                # Append assistant messages to the messages list                
                if not st.session_state.messages[-1].is_from(ChatRole.SYSTEM):
                    st.session_state.messages.append(response["replies"][0])
                    break