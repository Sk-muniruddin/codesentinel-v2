from agents import Runner

from codesentinel.agent import code_sentinel_agent


async def run_code_review(
    pull_request_diff: str,
    repository_context: str,
):
    prompt = f"""
Review this GitHub Pull Request.

====================
PULL REQUEST DIFF
====================

{pull_request_diff}

====================
REPOSITORY CONTEXT
====================

{repository_context}

Use the repository context to understand the existing codebase
before reviewing the Pull Request diff.

Return the final structured CodeReview.
"""

    result = await Runner.run(
        code_sentinel_agent,
        prompt,
    )

    return result.final_output