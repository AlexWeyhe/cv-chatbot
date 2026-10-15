import os
from pathlib import Path

import chromadb
import frontmatter
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext


load_dotenv()

DOCUMENTS_DIR = Path(__file__).resolve().parents[1] / "documents"
INDEX_DIR = Path(__file__).resolve().parents[1] / "index_storage"


def get_embedder():
    return OpenAIEmbedding(
        model="text-embedding-3-small",
    )


def load_markdown_documents(folder_path):
    documents = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)

                post = frontmatter.load(file_path)

                document = Document(
                    text=post.content,
                    metadata={
                        **post.metadata,
                        "file_name": file,
                        "file_path": file_path
                    }
                )

                documents.append(document)

    return documents


def create_nodes(documents):
    pipeline = IngestionPipeline(
        transformations=[MarkdownNodeParser()]
        )

    nodes = pipeline.run(documents=documents)
    
    return nodes


def index_store(nodes):
    embedder = get_embedder()
    
    db = chromadb.PersistentClient(path=INDEX_DIR)

    try:
        db.delete_collection("cv_bot_index")
        print("collection deleted.")

    except Exception:
        pass
    
    chroma_collection = db.create_collection("cv_bot_index")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embedder,
        )
        
    return index


def build_index():
    documents = load_markdown_documents(folder_path=DOCUMENTS_DIR)
        
    nodes = create_nodes(documents=documents)
    
    return index_store(nodes=nodes)


if __name__ == "__main__":
    build_index()