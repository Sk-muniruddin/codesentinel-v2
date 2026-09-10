from openai import OpenAI
from codesentinel.models import CodeReview


SYSTEM_PROMPT = """
You are CodeSentinel, an expert software code reviewer.

Review the provided GitHub pull request diff using the repository
context retrieved from Foundry IQ.

Identify only meaningful:
- correctness issues
- error handling problems
- security issues
- maintainability problems

Do not report harmless style changes.

Use the repository context to understand:
- existing architecture
- related functions and classes
- existing dependencies
- configuration
- interfaces
- surrounding implementation

Do not assume that retrieved repository context is part of the PR.
The PR diff is the code being reviewed.

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
    repository_context: str,
) -> CodeReview:
    prompt = f"""
{SYSTEM_PROMPT}

====================
PULL REQUEST DIFF
====================

{code}

====================
REPOSITORY CONTEXT
====================

{repository_context}

====================
REVIEW INSTRUCTIONS
====================

Review the pull request diff using the repository context above.

Only report meaningful findings that affect correctness,
error handling, security, or maintainability.

Return the structured CodeReview result.
"""

    response = client.responses.parse(
        model=model,
        input=prompt,
        text_format=CodeReview,
    )

    return response.output_parsed