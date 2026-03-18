#!/usr/bin/env python3
"""
BGB Erbrecht RAG - Command Line Interface
Query German Inheritance Law using natural language
"""
import sys
import argparse
from src.rag_engine import BGBQueryEngine


def main():
    parser = argparse.ArgumentParser(
        description="Query German Inheritance Law (BGB Book 5) using RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Wer erbt, wenn es kein Testament gibt?"
  python main.py "Was ist ein Pflichtteil?"
  python main.py "Können Enkel erben?"
        """
    )

    parser.add_argument(
        "query",
        type=str,
        nargs="?",
        help="Your question about German inheritance law"
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive mode"
    )

    args = parser.parse_args()

    # Initialize the RAG engine
    print("Initializing BGB Erbrecht Query Engine...")
    print("(This may take a moment on first run)\n")

    try:
        engine = BGBQueryEngine()
        engine.initialize()
    except Exception as e:
        print(f"✗ Error initializing RAG engine: {e}")
        print("\nPossible causes:")
        print("1. Vector database not built yet - run: python src/build_vectordb.py")
        print("2. Ollama not running - start with: ollama serve")
        print("3. Required models not pulled - run: ollama pull mistral && ollama pull nomic-embed-text")
        sys.exit(1)

    # Interactive mode
    if args.interactive:
        print("=" * 80)
        print("BGB ERBRECHT RAG - Interactive Mode")
        print("=" * 80)
        print("Type your questions about German inheritance law.")
        print("Type 'quit' or 'exit' to end the session.\n")

        while True:
            try:
                query = input("\n🔍 Ihre Frage: ").strip()

                if not query:
                    continue

                if query.lower() in ['quit', 'exit', 'q']:
                    print("\nAuf Wiedersehen!")
                    break

                result = engine.query(query)
                print("\n" + engine.format_response(result))

            except KeyboardInterrupt:
                print("\n\nAuf Wiedersehen!")
                break
            except Exception as e:
                print(f"\n✗ Error processing query: {e}")

    # Single query mode
    elif args.query:
        try:
            result = engine.query(args.query)
            print(engine.format_response(result))
        except Exception as e:
            print(f"✗ Error processing query: {e}")
            sys.exit(1)

    # No arguments provided
    else:
        parser.print_help()
        print("\n" + "=" * 80)
        print("QUICK START")
        print("=" * 80)
        print("Ask a question:")
        print('  python main.py "Wer erbt, wenn es kein Testament gibt?"')
        print("\nStart interactive mode:")
        print("  python main.py -i")
        print("=" * 80)


if __name__ == "__main__":
    main()
