from codesentinel.retrieve.foundry_iq import (
    retrieve_repository_context,
)
from codesentinel.review.runner import run_code_review


def main():
    code = """
def divide(a, b):
    return a / b
"""

    retrieval_query = """
Find repository code, functions, classes, tests, configuration,
and dependencies that are relevant to reviewing this pull request.

Pull request diff:

def divide(a, b):
    return a / b
"""

    repository_context = retrieve_repository_context(
        retrieval_query
    )

    print("Repository Context:")
    print(repository_context)

    review_input = f"""
Review the following pull request using the repository context.

====================
PULL REQUEST DIFF
====================

{code}

====================
REPOSITORY CONTEXT
====================

{repository_context}

====================
REVIEW REQUIREMENTS
====================

Identify only meaningful issues involving:
- correctness
- error handling
- security
- maintainability

Do not report harmless style changes.
"""

    import asyncio

    review = asyncio.run(
        run_code_review(review_input)
    )

    print("\nCode Review:")
    print(review.model_dump_json(indent=2))


if __name__ == "__main__":
    main()