from typing import List
from util import llm_call

def chain(input: str, prompts: List[str]) -> str:
    """Chain multiple LLM calls sequentially, passing results between steps."""
    result = input
    for i, prompt in enumerate(prompts, 1):
        print(f"\nStep {i}:")
        result = llm_call(f"{prompt}\nInput: {result}")
        print(result)
    return result

data_processing_steps = [
    """Extract numerical values and related metrics from the text.
    Write each on a new line in 'value: metric' format.
    Example format:
    92: Customer Satisfaction
    45%: Revenue Growth""",

    """Convert all possible numerical values to percentages.
    Convert to decimal if not a percentage or points (e.g., 92 points -> 92%).
    Keep one number per line.
    Example format:
    92%: Customer Satisfaction
    45%: Revenue Growth""",

    """Sort all lines by numerical value in descending order.
    Maintain the 'value: metric' format for each line.
    Example:
    92%: Customer Satisfaction
    87%: Employee Satisfaction""",

    """Format the sorted data as a markdown table like this:
    | Metric | Value |
    |:--|--:|
    | Customer Satisfaction | 92% |"""
]

report = """
Q3 Performance Summary:
Customer satisfaction score increased to 92 points this quarter.
Revenue grew 45% year over year.
Market share in key markets is now 23%.
Customer churn decreased from 8% to 5%.
Customer acquisition cost is $43 per user.
Product adoption rate increased to 78%.
Employee satisfaction is at 87 points.
Operating margin improved to 34%.
"""

print("\nInput text:")
print(report)
formatted_result = chain(report, data_processing_steps)
