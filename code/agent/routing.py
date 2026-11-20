from typing import Dict
from util import llm_call, extract_xml

def route(input: str, routes: Dict[str, str]) -> str:
    """Use content classification to route input to specialized prompts."""
    print(f"\nAvailable routes: {list(routes.keys())}")
    selector_prompt = f"""
    Analyze the input and select the most appropriate support team from these options: {list(routes.keys())}
    First explain your reasoning, then provide your selection in this XML format:

    <reasoning>
    Brief explanation of why this ticket should be routed to a specific team.
    Consider key terms, user intent, and urgency level.
    </reasoning>

    <selection>
    Selected team name
    </selection>

    Input: {input}""".strip()

    route_response = llm_call(selector_prompt)
    reasoning = extract_xml(route_response, 'reasoning')
    route_key = extract_xml(route_response, 'selection').strip().lower()

    print("Routing Analysis:")
    print(reasoning)
    print(f"\nSelected route: {route_key}")

    selected_prompt = routes[route_key]
    return llm_call(f"{selected_prompt}\nInput: {input}")

support_routes = {
    "billing": """You are a billing support specialist. Follow these guidelines:
    1. Always start with "Billing Support Response:"
    2. First acknowledge the specific billing issue
    3. Clarify any charges or discrepancies
    4. List specific next steps with timeline
    5. Close with payment options if relevant

    Maintain a professional yet friendly tone.

    Input: """,

    "technical": """You are a technical support engineer. Follow these guidelines:
    1. Always start with "Technical Support Response:"
    2. List exact steps for problem resolution
    3. Include system requirements if relevant
    4. Provide workarounds for common issues
    5. Close with escalation path if needed

    Use clear numbered steps and technical details.

    Input: """,

    "account": """You are an account security specialist. Follow these guidelines:
    1. Always start with "Account Support Response:"
    2. Prioritize account security and authentication
    3. Provide clear steps for account recovery/changes
    4. Include security tips and warnings
    5. Set clear expectations for resolution time

    Maintain a serious, security-focused tone.

    Input: """,

    "product": """You are a product specialist. Follow these guidelines:
    1. Always start with "Product Support Response:"
    2. Focus on feature education and best practices
    3. Include specific usage examples
    4. Provide links to relevant documentation sections
    5. Suggest related features that might help

    Maintain an educational and encouraging tone.

    Input: """
}

tickets = [
    """Subject: Cannot access account
    Message: Hi, I've been trying to log in for the past hour but keep getting 'incorrect password' errors.
    I'm certain I'm using the correct password. Can you help me regain access? This is urgent as I need to
    submit a report before end of business today.
    - John""",

    """Subject: Unexpected charge on card
    Message: Hello, I just noticed a charge of $49.99 from your company on my credit card, but I thought
    I was on the $29.99 plan. Could you explain this charge and adjust it if it's a mistake?
    Thanks,
    Sarah""",

    """Subject: How to export data?
    Message: I need to export all my project data to Excel. I've looked through the documentation but
    can't find how to do a bulk export. Is this possible? If so, could you walk me through the steps?
    Thanks,
    Mike"""
]

print("Processing support tickets...\n")
for i, ticket in enumerate(tickets, 1):
    print(f"\nTicket {i}:")
    print("-" * 40)
    print(ticket)
    print("\nResponse:")
    print("-" * 40)
    response = route(ticket, support_routes)
    print(response)
