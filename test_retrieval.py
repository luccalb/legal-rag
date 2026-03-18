"""Test retrieval quality and see what documents are being retrieved"""
from src.rag_engine import BGBQueryEngine

# Initialize engine
engine = BGBQueryEngine()
engine.initialize()

# Test retrieval directly
query = "Wer erbt, wenn es kein Testament gibt?"
print(f"Query: {query}\n")

# Get documents from retriever
retriever = engine.vectorstore.as_retriever(search_kwargs={"k": 4})
docs = retriever.get_relevant_documents(query)

print(f"Retrieved {len(docs)} documents:\n")
for i, doc in enumerate(docs, 1):
    print(f"\n{'='*80}")
    print(f"Document {i}:")
    print(f"Section: {doc.metadata.get('section', 'Unknown')}")
    print(f"Title: {doc.metadata.get('title', 'Unknown')}")
    print(f"Content preview: {doc.page_content[:300]}...")
    print('='*80)

# Now test the full RAG chain
print("\n\n" + "="*80)
print("TESTING FULL RAG CHAIN")
print("="*80)
result = engine.query(query)
print("\nAnswer:")
print(result['answer'])
print("\nSources:")
for source in result['sources']:
    print(f"- {source['section']}: {source['title']}")
