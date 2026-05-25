#!/usr/bin/env python3
"""
Debug script to diagnose why RAGAS scores are all 0
"""

import asyncio
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / "../../.env", override=False)


async def test_rag_api():
    """Test LightRAG API response structure"""
    rag_api_url = os.getenv("LIGHTRAG_API_URL", "http://localhost:9621")
    api_key = os.getenv("LIGHTRAG_API_KEY")

    print("=" * 70)
    print("🔍 Testing LightRAG API Response")
    print("=" * 70)

    question = "表架弧形板 (BK100) 的物料版本和创建时间是什么？"

    payload = {
        "query": question,
        "mode": "mix",
        "include_references": True,
        "response_type": "Multiple Paragraphs",
        "top_k": 10,
    }

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(
                f"{rag_api_url}/query",
                json=payload,
                headers=headers if headers else None,
            )
            response.raise_for_status()
            result = response.json()

            print(f"\n✅ API Response Status: {response.status_code}")
            print(f"\n📦 Response Keys: {list(result.keys())}")
            print(f"\n💬 Answer (first 200 chars):")
            print(f"   {result.get('response', 'N/A')[:200]}...")

            references = result.get("references", [])
            print(f"\n📚 References Count: {len(references)}")

            if references:
                print(f"\n🔍 First Reference Structure:")
                first_ref = references[0]
                print(f"   Keys: {list(first_ref.keys())}")

                content = first_ref.get("content", [])
                print(f"   Content Type: {type(content).__name__}")

                if isinstance(content, list):
                    print(f"   Content Length: {len(content)} chunks")
                    if content:
                        print(f"   First Chunk (100 chars): {str(content[0])[:100]}...")
                elif isinstance(content, str):
                    print(f"   Content (100 chars): {content[:100]}...")
                else:
                    print(f"   ⚠️  Content is neither list nor string!")
            else:
                print("   ❌ No references returned!")

        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()


def check_ragas_config():
    """Check RAGAS configuration"""
    print("\n" + "=" * 70)
    print("🔧 Checking RAGAS Configuration")
    print("=" * 70)

    eval_llm_model = os.getenv("EVAL_LLM_MODEL", "gpt-4o-mini")
    eval_llm_host = os.getenv("EVAL_LLM_BINDING_HOST")
    eval_llm_key = os.getenv("EVAL_LLM_BINDING_API_KEY") or os.getenv("OPENAI_API_KEY")
    eval_embedding_model = os.getenv("EVAL_EMBEDDING_MODEL", "text-embedding-3-large")
    eval_embedding_host = os.getenv("EVAL_EMBEDDING_BINDING_HOST") or eval_llm_host

    print(f"\n🤖 LLM Model: {eval_llm_model}")
    print(f"   Endpoint: {eval_llm_host or 'OpenAI Official API'}")
    print(f"   API Key Set: {'✅ Yes' if eval_llm_key else '❌ No'}")

    print(f"\n📊 Embedding Model: {eval_embedding_model}")
    print(f"   Endpoint: {eval_embedding_host or 'OpenAI Official API'}")

    # Try to import ragas
    try:
        from ragas import evaluate
        from ragas.metrics import Faithfulness, AnswerRelevancy, ContextRecall, ContextPrecision
        print(f"\n✅ RAGAS is installed and importable")
    except ImportError as e:
        print(f"\n❌ RAGAS import failed: {e}")


if __name__ == "__main__":
    print("\n🚀 RAGAS Debug Script")
    print("=" * 70)

    # Check configuration
    check_ragas_config()

    # Test API
    asyncio.run(test_rag_api())

    print("\n" + "=" * 70)
    print("✅ Debug Complete")
    print("=" * 70)