from haystack import Pipeline, Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import (SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder)
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret

# Embed documents
def embed_documents(documents):
    document_store = InMemoryDocumentStore()

    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component(
        "doc_embedder", SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
    )
    indexing_pipeline.add_component("doc_writer", DocumentWriter(document_store=document_store))

    indexing_pipeline.connect("doc_embedder.documents", "doc_writer.documents")

    indexing_pipeline.run({"doc_embedder": {"documents": documents}})

    return document_store

documents = [
    Document(content="Coffee shop opens at 9am and closes at 5pm."),
    Document(content="Gym room opens at 6am and closes at 10pm.")
]

document_store = embed_documents(documents)

# Create RAG pipeline
template = """
Answer the questions based on the given context.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}
Question: {{ question }}
Answer:
"""
rag_pipe = Pipeline()
rag_pipe.add_component("embedder", SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"))
rag_pipe.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
rag_pipe.add_component("prompt_builder", PromptBuilder(template=template))
# Note to llm: We are using OpenAIGenerator, not the OpenAIChatGenerator, because the latter only accepts List[str] as input and cannot accept prompt_builder's str output
rag_pipe.add_component("llm", OpenAIGenerator(api_key=Secret.from_env_var("OPENROUTER_API_KEY"),
		api_base_url="https://openrouter.ai/api/v1",
		model="openai/gpt-4-turbo-preview"))

rag_pipe.connect("embedder.embedding", "retriever.query_embedding")
rag_pipe.connect("retriever", "prompt_builder.documents")
rag_pipe.connect("prompt_builder", "llm")

def rag_pipeline_func(query: str):
    result = rag_pipe.run({"embedder": {"text": query}, "prompt_builder": {"question": query}})

    return {"reply": result["llm"]["replies"][0]}
