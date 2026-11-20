from util import llm_call, extract_xml

MAX_ROUNDS = 4  # safety cap so the loop can't run forever

def generate(prompt: str, task: str, context: str = "") -> tuple[str, str]:
    """Generate and improve a solution based on feedback."""
    full_prompt = f"{prompt}\n{context}\nTask: {task}" if context else f"{prompt}\nTask: {task}"
    response = llm_call(full_prompt)
    thoughts = extract_xml(response, "thoughts")
    result = extract_xml(response, "response")

    print("\n=== GENERATION START ===")
    print(f"Thoughts:\n{thoughts}\n")
    print(f"Generated:\n{result}")
    print("=== GENERATION END ===\n")

    return thoughts, result

def evaluate(prompt: str, content: str, task: str) -> tuple[str, str]:
    """Evaluate if a solution meets requirements."""
    full_prompt = f"{prompt}\nOriginal task: {task}\nContent to evaluate: {content}"
    response = llm_call(full_prompt)
    evaluation = extract_xml(response, "evaluation")
    feedback = extract_xml(response, "feedback")

    print("=== EVALUATION START ===")
    print(f"Status: {evaluation}")
    print(f"Feedback: {feedback}")
    print("=== EVALUATION END ===\n")

    return evaluation, feedback

def loop(task: str, evaluator_prompt: str, generator_prompt: str) -> tuple[str, list[dict]]:
    """Keep generating and evaluating until requirements are met."""
    memory = []
    chain_of_thought = []

    thoughts, result = generate(generator_prompt, task)
    memory.append(result)
    chain_of_thought.append({"thoughts": thoughts, "result": result})

    for _ in range(MAX_ROUNDS):
        evaluation, feedback = evaluate(evaluator_prompt, result, task)
        if evaluation.strip() == "PASS":
            return result, chain_of_thought

        context = "\n".join([
            "Previous attempts:",
            *[f"- {m}" for m in memory],
            f"\nFeedback: {feedback}"
        ])

        thoughts, result = generate(generator_prompt, task, context)
        memory.append(result)
        chain_of_thought.append({"thoughts": thoughts, "result": result})

    print(f"Stopped after {MAX_ROUNDS} rounds without PASS.")
    return result, chain_of_thought

evaluator_prompt = """
Evaluate the following code implementation against these criteria:
1. Code correctness
2. Time complexity
3. Style and best practices

Only evaluate, do not attempt to solve the task.
Only output "PASS" if all criteria are met and there are no improvement suggestions.
Output your evaluation in this format:

<evaluation>PASS, NEEDS_IMPROVEMENT, or FAIL</evaluation>
<feedback>
What needs improvement and why.
</feedback>
"""

generator_prompt = """
Your goal is to complete the task based on <user input>. If there is feedback
from previous generations, you should incorporate it to improve the solution.

Output your answer in this format:

<thoughts>
[Understanding of task and feedback, improvement plan]
</thoughts>

<response>
[Code implementation]
</response>
"""

task = """
<user input>
Implement a stack with:
1. push(x)
2. pop()
3. getMin()
All operations should be O(1).
</user input>
"""

loop(task, evaluator_prompt, generator_prompt)
