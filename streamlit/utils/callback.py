# The write_stream method newly supported in Streamlit does not seem to be usable with Haystack's generator
# So we will use the StreamlitCallbackHandler to stream the responses from the assistant to the UI

# This is adapted from Langchain's StreamlitCallbackHandler 
# https://api.python.langchain.com/en/latest/_modules/langchain_community/callbacks/streamlit/streamlit_callback_handler.html#StreamlitCallbackHandler

from haystack.dataclasses import StreamingChunk

class StreamlitCallbackHandler():
    def __init__(self, response_container):
        self.response_container = response_container
        self.current_text = ''

    # Stream the messages from the assistant to the UI
    def on_llm_new_token(self, chunk: StreamingChunk):
        # Only chat messages from the assistant are shown, because chunks from function/tool calls do not have the content attribute
        self.current_text += chunk.content
        self.response_container.markdown(self.current_text)