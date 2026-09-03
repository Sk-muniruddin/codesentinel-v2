from openai import OpenAI
from codesentinel.models import CodeReview


SYSTEM_PROMPT = """
You are CodeSentinel, an expert software code reviewer.

Review the provided GitHub pull request diff carefully.

Identify only meaningful:
- correctness issues
- error handling problems
- security issues
- maintainability problems

Do not report harmless style changes.

For every finding provide:
- severity
- category
- file
- line
- problem
- impact
- recommendation
"""


def review_code(
    client: OpenAI,
    model: str,
    code: str,
) -> CodeReview:
    prompt = f"""
{SYSTEM_PROMPT}

Review this GitHub pull request diff:

{code}
"""

    response = client.responses.parse(
        model=model,
        input=prompt,
        text_format=CodeReview,
    )

    return response.output_parsed