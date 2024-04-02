# Function Calling demo
## What does this application wants to demonstrate
This application is built as an extension to [this](https://haystack.deepset.ai/tutorials/40_building_chat_application_with_function_calling)
1. **Data retrieval**: With both RAG and DB search (via API created from Flask)
2. **Routing**: Use Function Call for autonomous tool choice & invocation
3. **UI** Via Streamlit

## Tech stack
- **Embedding model**: [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Vector Database**: [Haystack's InMemoryDocumentStore](https://docs.haystack.deepset.ai/docs/inmemorydocumentstore)
- **LLM**: [GPT-4 Turbo accessed via OpenRouter](https://openrouter.ai/models/openai/gpt-4-1106-preview). But the flow can be adapted into using other LLMs
- **LLM Framework**: [Haystack](https://haystack.deepset.ai/) for their great documentations, and transparency in pipeline construction. This tutorial is actually an extension to their [fantastic tutorial](https://haystack.deepset.ai/tutorials/40_building_chat_application_with_function_calling) for the same topic

## Running this tool
1. Create and activate a virtual environment, then `pip install -r requirements.txt` to install the required packages
1. Spin up the API server with `python db_api.py`
2. If you are seeking for an initial tutorial for the concept behind, run `rag_plus_db_search.ipynb`. Or proceed to #3 directly
3. Run the streamlit application with the below
```
export OPENROUTER_API_KEY = '@REPLACE WITH YOUR API KEY'
cd sample_applications/01_RAG_plus_DB_search/streamlit
streamlit run app.py
```