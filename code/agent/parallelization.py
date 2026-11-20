from concurrent.futures import ThreadPoolExecutor
from typing import List
from util import llm_call

def parallel(prompt: str, inputs: List[str], n_workers: int = 3) -> List[str]:
    """Process multiple inputs simultaneously with the same prompt."""
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(llm_call, f"{prompt}\nInput: {x}") for x in inputs]
        return [f.result() for f in futures]

stakeholders = [
    """Customers:
    - Price sensitive
    - Want better technology
    - Environmental concerns""",

    """Employees:
    - Job security concerns
    - Need to learn new skills
    - Want clear direction""",

    """Investors:
    - Expect growth
    - Want cost control
    - Risk concerns""",

    """Suppliers:
    - Capacity constraints
    - Price pressure
    - Technology transition"""
]

impact_results = parallel(
    """Analyze the impact of market changes on this stakeholder group.
    Provide specific impacts and recommended actions.
    Format with clear sections and priorities.""",
    stakeholders
)

for result in impact_results:
    print(result)
    print("\n" + "=" * 60 + "\n")
