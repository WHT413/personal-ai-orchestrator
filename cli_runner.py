"""
CLI Runner — Test the Orchestrator Phase 1 pipeline locally via command line.
"""

import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from guardrails.validator import Validator, ValidationError
from core.orchestrator import Orchestrator
from routing.embeddings import EmbeddingsProvider
from routing.intent_router import HybridIntentRouter
from core.tool_registry import ToolRegistry
from tools.tool_dispatcher import ToolDispatcher
from services.finance.storage import ExpenseStorage
from services.finance.finance_service import FinanceService
from tools.finance.finance_tools import FinanceTools
from services.calendar.storage import CalendarStorage
from services.calendar.calendar_service import CalendarService
from tools.calendar.calendar_tools import CalendarTools
from llm_runtime.llama_cpp_runtime import LlamaCppRuntime
from llm_runtime.llama_runner import LlamaRunner


def setup_orchestrator() -> Orchestrator:
    """Wire up all Phase 1 components."""
    print("Initializing system components...")
    
    # 1. Setup Services & Storage
    data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
    finance_storage = ExpenseStorage(os.path.join(data_dir, "expenses.json"))
    finance_service = FinanceService(finance_storage)
    finance_tools = FinanceTools(finance_service)
    
    calendar_storage = CalendarStorage(os.path.join(data_dir, "events.json"))
    calendar_service = CalendarService(calendar_storage)
    calendar_tools = CalendarTools(calendar_service)

    # 2. Setup Tool Registry & Dispatcher
    registry = ToolRegistry()
    registry.register("finance.add_expense", finance_tools.add_expense)
    registry.register("finance.query_expenses", finance_tools.query_expenses)
    registry.register("calendar.create_event", calendar_tools.create_event)
    registry.register("calendar.list_events", calendar_tools.list_events)
    
    dispatcher = ToolDispatcher(registry)

    # 3. Setup LLM Runtime (for fallback conversation)
    # Using the subprocess-based llama.cpp wrapper as per ADR-0001
    models_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "models")
    llm_model = os.path.join(models_dir, "Qwen3.5-4B-Q4_K_M.gguf")
    
    # We assume 'llama-completion' is available inPATH
    runner = LlamaRunner(
        llama_binary_path="~/WORKSPACE/HieuNT/benchmark/llama.cpp/build/bin/llama-completion",
        model_path=llm_model,
        context_size=256,
        gpu_layers=0, # Force CPU to avoid CUDA OOM when both router/fallback run simultaneously
    )
    llm = LlamaCppRuntime(runner)

    # 4. Setup Hybrid Router
    embeddings = EmbeddingsProvider()
    router = HybridIntentRouter(embeddings, llm)

    # 5. Assemble Orchestrator
    orchestrator = Orchestrator(router, dispatcher, llm)
    
    print("Initialization complete!\n")
    return orchestrator


def main():
    print("=== Personal AI Orchestrator (CLI Test Mode) ===")
    print("Type 'exit' or 'quit' to stop.\n")
    
    try:
        orc = setup_orchestrator()
    except Exception as e:
        print(f"Failed to initialize orchestrator: {e}")
        print("Tip: Make sure the GGUF model exists in the 'models' directory.")
        return

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.strip().lower() in ("exit", "quit"):
                break
                
            if not user_input.strip():
                continue

            # Step 1: Guardrails
            try:
                Validator.validate(user_input)
            except ValidationError as e:
                print(f"Bot (Guardrails blocked): {e}")
                continue
                
            # Step 2: Route
            route_result = orc._router.route(user_input)

            # Step 3: Dispatch or Converse
            if route_result.intent == "conversation":
                response = orc._handle_conversation(user_input)
            else:
                result = orc._dispatcher.dispatch(route_result.intent, route_result.params)
                response = orc._format_tool_result(route_result.intent, result)

            print(f"\nBot: \n{response}\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"System Error: {e}")


if __name__ == "__main__":
    main()
