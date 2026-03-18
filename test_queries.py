"""Test with different query formulations"""
from src.rag_engine import BGBQueryEngine

# Initialize engine
engine = BGBQueryEngine()
engine.initialize()

queries = [
    "Wer erbt, wenn es kein Testament gibt?",
    "gesetzliche Erbfolge",
    "Erben erster Ordnung",
    "Testament fehlt wer erbt",
    "Abkömmlinge Erbrecht"
]

for query in queries:
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print('='*80)

    retriever = engine.vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(query)

    for i, doc in enumerate(docs, 1):
        print(f"{i}. {doc.metadata.get('section', 'Unknown')}: {doc.metadata.get('title', 'Unknown')}")
