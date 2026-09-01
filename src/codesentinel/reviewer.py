from openai import OpenAI

from codesentinel.models import CodeReview


SYSTEM_PROMPT = """
You are CodeSentinel, an expert software code reviewer.

Review the provided code carefully.

Identify:
- correctness issues
- error handling problems
- security issues
- maintainability problems

Only report meaningful issues.
"""


def review_code(
    client: OpenAI,
    model: str,
    code: str,
) -> CodeReview:

    response = client.responses.parse(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
Review this Python code:

{code}
""",
            },
        ],
        text_format=CodeReview,
    )

    return response.output_parsed