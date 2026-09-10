from agents import Runner

from codesentinel.review.agent import code_sentinel_agent
from codesentinel.review.model_client import (
    configure_azure_openai_client,
)


configure_azure_openai_client()


async def run_code_review(
    review_input: str,
):
    result = await Runner.run(
        code_sentinel_agent,
        input=review_input,
    )

    review = result.final_output

    return review