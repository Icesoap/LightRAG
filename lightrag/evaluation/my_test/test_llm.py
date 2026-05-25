#!/usr/bin/env python3
"""
Test script for DeepSeek /chat/completions endpoint
Tests the API configuration used by RAGAS evaluation
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"⚠️  .env file not found at: {env_path}")


def test_with_httpx():
    """Test using httpx directly (most basic)"""
    print("\n" + "=" * 70)
    print("🧪 Test 1: Direct HTTP request to /chat/completions")
    print("=" * 70)

    try:
        import httpx
        import json

        api_key = os.getenv("EVAL_LLM_BINDING_API_KEY")
        base_url = os.getenv("EVAL_LLM_BINDING_HOST", "https://api.deepseek.com/v1")
        model = os.getenv("EVAL_LLM_MODEL", "deepseek-chat")

        if not api_key:
            print("❌ Error: EVAL_LLM_BINDING_API_KEY not set in .env")
            return False

        # Construct the full URL
        url = f"{base_url.rstrip('/')}/chat/completions"

        print(f"📍 URL: {url}")
        print(f"🤖 Model: {model}")
        print(f"🔑 API Key: {'*' * 8}{api_key[-4:]}")

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello! Please respond with a brief greeting."
                }
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        print("\n📤 Sending request...")
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)

            print(f"📥 Response Status: {response.status_code}")
            print(f"📥 Response Headers: {dict(response.headers)}")

            if response.status_code == 200:
                result = response.json()
                print("\n✅ Success!")
                print(f"Response:\n{json.dumps(result, indent=2, ensure_ascii=False)}")

                # Extract the actual content
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    print(f"\n💬 Assistant says: {content}")

                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"Response body: {response.text}")
                return False

    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}")
        print(f"Message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_with_langchain():
    """Test using LangChain (same as RAGAS uses)"""
    print("\n" + "=" * 70)
    print("🧪 Test 2: Using LangChain ChatOpenAI (RAGAS method)")
    print("=" * 70)

    try:
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("EVAL_LLM_BINDING_API_KEY")
        base_url = os.getenv("EVAL_LLM_BINDING_HOST", "https://api.deepseek.com/v1")
        model = os.getenv("EVAL_LLM_MODEL", "deepseek-chat")

        if not api_key:
            print("❌ Error: EVAL_LLM_BINDING_API_KEY not set in .env")
            return False

        print(f"📍 Base URL: {base_url}")
        print(f"🤖 Model: {model}")
        print(f"🔑 API Key: {'*' * 8}{api_key[-4:]}")

        # Create LLM instance (same config as eval_rag_quality.py)
        llm_kwargs = {
            "model": model,
            "api_key": api_key,
            "base_url": base_url,
            "max_retries": 3,
            "request_timeout": 60,
        }

        print("\n🔧 Creating ChatOpenAI instance...")
        llm = ChatOpenAI(**llm_kwargs)

        print("📤 Sending test message...")
        response = llm.invoke("Hello! Please respond with a brief greeting.")

        print("\n✅ Success!")
        print(f"💬 Assistant says: {response.content}")
        print(f"📊 Response metadata: {response.response_metadata}")

        return True

    except ImportError:
        print("❌ langchain_openai not installed. Install with: pip install langchain-openai")
        return False
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}")
        print(f"Message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_with_ragas_wrapper():
    """Test using RAGAS LangchainLLMWrapper (exact RAGAS setup)"""
    print("\n" + "=" * 70)
    print("🧪 Test 3: Using RAGAS LangchainLLMWrapper (Exact RAGAS setup)")
    print("=" * 70)

    try:
        from langchain_openai import ChatOpenAI
        from ragas.llms import LangchainLLMWrapper
        from langchain_core.messages import HumanMessage, SystemMessage
        import asyncio

        api_key = os.getenv("EVAL_LLM_BINDING_API_KEY")
        base_url = os.getenv("EVAL_LLM_BINDING_HOST", "https://api.deepseek.com/v1")
        model = os.getenv("EVAL_LLM_MODEL", "deepseek-chat")

        if not api_key:
            print("❌ Error: EVAL_LLM_BINDING_API_KEY not set in .env")
            return False

        print(f"📍 Base URL: {base_url}")
        print(f"🤖 Model: {model}")
        print(f"🔑 API Key: {'*' * 8}{api_key[-4:]}")

        # Create base LLM
        llm_kwargs = {
            "model": model,
            "api_key": api_key,
            "base_url": base_url,
            "max_retries": 3,
            "request_timeout": 60,
        }

        print("\n🔧 Creating ChatOpenAI instance...")
        base_llm = ChatOpenAI(**llm_kwargs)

        print("🔧 Wrapping with LangchainLLMWrapper (bypass_n=True)...")
        eval_llm = LangchainLLMWrapper(
            langchain_llm=base_llm,
            bypass_n=True,  # Same as RAGAS evaluation
        )

        print("📤 Sending test message...")
        
        # Create proper message objects (LangChain format)
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hello! Please respond with a brief greeting.")
        ]
        
        # Method 1: Use the underlying ChatOpenAI directly (simpler)
        print("\n--- Testing via underlying ChatOpenAI ---")
        direct_response = base_llm.invoke(messages)
        print(f"✅ Direct response: {direct_response.content}")
        
        # Method 2: Use LangchainLLMWrapper's async method (what RAGAS uses)
        print("\n--- Testing via LangchainLLMWrapper (async) ---")
        
        async def test_wrapper():
            # agenerate_text expects a PromptValue or string, not a list of messages
            # We need to use agenerate which accepts prompts (list of messages)
            from langchain_core.prompts import ChatPromptTemplate
            
            # Create a prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("human", "Hello! Please respond with a brief greeting.")
            ])
            
            # Format the prompt
            formatted_prompt = prompt_template.format_messages()
            
            # Use agenerate which accepts prompts
            response = await eval_llm.langchain_llm.agenerate(
                messages=[formatted_prompt],
                n=1,
                temperature=0.7,
            )
            return response
        
        wrapper_response = asyncio.run(test_wrapper())
        print(f"✅ Wrapper response: {wrapper_response.generations[0][0].text}")
        
        print("\n✅ All tests passed!")
        return True

    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install ragas langchain-openai")
        return False
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}")
        print(f"Message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("🔍 DeepSeek /chat/completions API Test Suite")
    print("=" * 70)

    results = []

    # Test 1: Direct HTTP
    results.append(("Direct HTTP", test_with_httpx()))

    # Test 2: LangChain
    results.append(("LangChain ChatOpenAI", test_with_langchain()))

    # Test 3: RAGAS Wrapper
    results.append(("RAGAS LangchainLLMWrapper", test_with_ragas_wrapper()))

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} | {name}")

    passed = sum(1 for _, s in results if s)
    total = len(results)

    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your API configuration is correct.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Verify EVAL_LLM_MODEL is 'deepseek-chat' (not 'deepseek-reasoner')")
        print("   2. Check your API key is valid and has sufficient credits")
        print("   3. Ensure EVAL_LLM_BINDING_HOST is 'https://api.deepseek.com/v1'")
        print("   4. Check network connectivity and firewall settings")

    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    # test_with_httpx()
    test_with_ragas_wrapper()
    # sys.exit(main())
