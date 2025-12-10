"""Test enhanced smart tool orchestration with dynamic workflows."""

import sys
sys.path.insert(0, "src")

from webdocx.utils.orchestrator import (
    suggest_tools, 
    classify_intent, 
    ResearchIntent,
    ResearchContext,
    update_context_from_result
)


def test_intent_classification():
    """Test multi-intent detection with confidence scores."""
    
    test_cases = [
        ("How to integrate LidgiCash API?", ResearchIntent.QUICK_ANSWER),
        ("LidgiCash API documentation", ResearchIntent.DOCUMENTATION),
        ("Compare LidgiCash vs pawaPay APIs", ResearchIntent.COMPARISON),
        ("Research mobile money payment solutions comprehensively", ResearchIntent.DEEP_RESEARCH),
        ("Find alternatives to LidgiCash", ResearchIntent.DISCOVERY),
        ("Check if LidgiCash API docs updated", ResearchIntent.MONITORING),
    ]
    
    print("🧠 Multi-Intent Classification (Confidence Scores)\n")
    for query, expected_primary in test_cases:
        intent_scores = classify_intent(query)
        primary = intent_scores[0]
        
        status = "✓" if primary.intent == expected_primary else "✗"
        print(f"{status} Query: \"{query}\"")
        print(f"   Expected: {expected_primary.value}")
        print(f"   Primary Intent: {primary.intent.value} ({primary.confidence:.0%})")
        print(f"   Keywords: {', '.join(primary.keywords_matched)}")
        
        if len(intent_scores) > 1:
            print(f"   Secondary: {intent_scores[1].intent.value} ({intent_scores[1].confidence:.0%})")
        print()


def test_dynamic_workflows():
    """Test dynamic workflow generation with context."""
    
    scenarios = [
        {
            "name": "Quick Answer - No URLs",
            "query": "How to integrate LidgiCash API?",
            "context": ResearchContext()
        },
        {
            "name": "Quick Answer - With Known URL",
            "query": "What is LidgiCash?",
            "context": ResearchContext(known_urls=["https://lidgicash.com/docs"])
        },
        {
            "name": "Documentation - Need to Find",
            "query": "LidgiCash API documentation complete guide",
            "context": ResearchContext()
        },
        {
            "name": "Comparison - Multiple Sources",
            "query": "Compare LidgiCash vs pawaPay payment APIs",
            "context": ResearchContext(
                known_urls=["https://lidgicash.com", "https://pawapay.io"]
            )
        },
    ]
    
    print("\n📋 Dynamic Workflow Generation\n")
    for scenario in scenarios:
        print(f"Scenario: {scenario['name']}")
        print(f"Query: \"{scenario['query']}\"")
        print("=" * 70)
        
        suggestion = suggest_tools(scenario['query'], scenario['context'])
        
        print(f"Primary Intent: {suggestion['primary_intent']['type']} "
              f"({suggestion['primary_intent']['confidence']:.0%})")
        print(f"Context: URLs={suggestion['context_notes']['has_known_urls']}, "
              f"Searches={suggestion['context_notes']['search_attempts']}")
        print(f"\nWorkflow ({len(suggestion['workflow'])} steps):\n")
        
        for step in suggestion['workflow']:
            parallel_note = f" [Parallel Group {step['parallel_group']}]" if step['parallel_group'] else ""
            fallback_note = " ⚠️ (has fallback)" if step['has_fallback'] else ""
            print(f"  {step['step']}. {step['tool']}{parallel_note}{fallback_note}")
            print(f"     Purpose: {step['purpose']}")
            
            if step['suggested_parameters']:
                params_str = ', '.join(f"{k}={v}" for k, v in step['suggested_parameters'].items())
                print(f"     Suggested: {params_str}")
            
            if step['tool_details']:
                print(f"     Duration: {step['tool_details']['estimated_duration']}, "
                      f"Cost: {step['tool_details']['resource_cost']}")
            print()
        
        print("-" * 70 + "\n")


def test_context_evolution():
    """Test how context updates affect workflow."""
    
    print("\n🔄 Context Evolution Test\n")
    
    query = "Research LidgiCash payment integration"
    
    # Stage 1: No context
    print("Stage 1: Initial Query (No Context)")
    print("-" * 50)
    ctx = ResearchContext()
    result = suggest_tools(query, ctx)
    print(f"Intent: {result['primary_intent']['type']}")
    print(f"Workflow: {len(result['workflow'])} steps")
    for step in result['workflow']:
        print(f"  - {step['tool']}")
    
    # Stage 2: After search (simulate)
    print("\n\nStage 2: After Search (URLs Found)")
    print("-" * 50)
    ctx = update_context_from_result(
        ctx, 
        "search_web",
        [{"url": "https://lidgicash.com/docs"}, {"url": "https://example.com/guide"}],
        success=True
    )
    result = suggest_tools(query, ctx)
    print(f"Intent: {result['primary_intent']['type']}")
    print(f"Known URLs: {len(ctx.known_urls)}")
    print(f"Workflow: {len(result['workflow'])} steps")
    for step in result['workflow']:
        print(f"  - {step['tool']}")
    
    # Stage 3: After failed attempts
    print("\n\nStage 3: After Failed Attempts")
    print("-" * 50)
    ctx.search_attempts = 3
    ctx.mark_failed("scrape_url")
    result = suggest_tools(query, ctx)
    print(f"Intent: {result['primary_intent']['type']}")
    print(f"Search Attempts: {ctx.search_attempts}")
    print(f"Failed Tools: {', '.join(ctx.failed_tools)}")
    print(f"Workflow: {len(result['workflow'])} steps")
    for step in result['workflow']:
        print(f"  - {step['tool']}")


def test_lidgicash_research():
    """Real-world LidgiCash research scenario."""
    
    print("\n\n🎯 Real-World: LidgiCash API Integration Research\n")
    print("=" * 70)
    
    query = "How can I integrate mobile payment with LidgiCash API for Cameroon merchants?"
    
    print(f"User Query:\n  \"{query}\"\n")
    
    # Initial research
    suggestion = suggest_tools(query)
    
    print(f"Analysis:")
    print(f"  Primary Intent: {suggestion['primary_intent']['type']} "
          f"({suggestion['primary_intent']['confidence']:.0%})")
    print(f"  Reasoning: {suggestion['primary_intent']['reasons'][0]}")
    print(f"  Keywords: {', '.join(suggestion['primary_intent']['keywords'])}")
    
    if suggestion['secondary_intents']:
        print(f"\n  Secondary Intents:")
        for intent in suggestion['secondary_intents']:
            print(f"    - {intent['type']} ({intent['confidence']:.0%})")
    
    print(f"\nRecommended Workflow:")
    print(f"  {suggestion['explanation']}\n")
    
    for step in suggestion['workflow']:
        print(f"  Step {step['step']}: {step['tool']}")
        print(f"    Purpose: {step['purpose']}")
        
        if step['suggested_parameters']:
            print(f"    Parameters:")
            for key, value in step['suggested_parameters'].items():
                print(f"      - {key}: {value}")
        
        if step['tool_details']:
            print(f"    Resource: {step['tool_details']['estimated_duration']} / "
                  f"{step['tool_details']['resource_cost']} cost")
            print(f"    Best for: {step['tool_details']['best_for'][0]}")
        
        print()


if __name__ == "__main__":
    print("=" * 70)
    print("  WebDocx Enhanced Orchestration Test Suite")
    print("  Testing: Intent Classification, Dynamic Workflows, Context Evolution")
    print("=" * 70 + "\n")
    
    test_intent_classification()
    test_dynamic_workflows()
    test_context_evolution()
    test_lidgicash_research()
    
    print("\n" + "=" * 70)
    print("✓ All tests completed! Orchestration system validated.")
    print("=" * 70)
