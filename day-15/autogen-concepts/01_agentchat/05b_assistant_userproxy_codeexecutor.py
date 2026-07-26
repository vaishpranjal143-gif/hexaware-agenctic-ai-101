# autogen-concepts/01_agentchat/05b_assistant_userproxy_codeexecutor.py
# AssistantAgent: thinkks & write the code
# UserProxyAgent: ai asks us and waits and we as humans users provide input to the agent
# CodeExecutorAgent: runs the code and returns the output to the agent

import asyncio
import tempfile
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent, CodeExecutorAgent
from autogen_agentchat.agents._code_executor_agent import ApprovalRequest, ApprovalResponse
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from _model import get_client

REFUNDS = [1299, 8999, 2450, 4999, 9999, 14999, 19999, 1299, 2345, 5999]

TASK = (
    f"Hex Retail's refunds this week were: {REFUNDS}\n"
    "Write and run python that prints the total, the mean, and how many exceeds 5000."
    "Once you have the real printed numbers, state them plainly."
)

def approve_code(request: ApprovalRequest) -> ApprovalResponse:
    """Show the human exact code about to run, and let them allow or block it"""
    print("\n" + "!" * 80 + "\n")
    print("Approval Required. The executive will run this until you say so.")
    print("\n" + "!" * 80 + "\n")
    print(request.code)
    print("\n" + "!" * 80 + "\n")
    answer = input("Do you approve this code to run? (y/n): ").strip().lower()

    if answer in ("yes", "y"):
        return ApprovalResponse(approved=True, reason="Approved by the on-duty engineer.")
    reason = input("Please provide a reason for disapproval: ").strip()
    return ApprovalResponse(
        approved=False,
        reason=reason or "Disapproved by the on-duty engineer.",
    )

async def main():
    with tempfile.TemporaryDirectory() as work_dir:
        client = get_client()

        assistant = AssistantAgent(
            name="assistant",
            model_client=client,
            system_message=(
                "you write Python for hex retail put code in ```Python block."
                "you cannot run code - the executor does that and reports back."
                "if your code is rejected by the reviewer, read their reason rewrite the code to satisfy it and send the new version"
                "once you have a real printed output, state the numbers and say FINISHED"
            )
        )

        executor = CodeExecutorAgent(
            name="executor",
            code_executor=LocalCommandLineCodeExecutor(work_dir=work_dir),
            approval_func=approve_code,
        )

        reviewer = UserProxyAgent(
            name="engineer",
            input_func=input,
        )

        team = RoundRobinGroupChat(
            [assistant, executor, reviewer],
            termination_condition=TextMentionTermination("FINISHED")
            | MaxMessageTermination(12),
        )

        print("\n" + "=" * 80 + "\n")
        print("three agents three duties")
        print("assistant writes the code but cannot run it")
        print("executor runs the code but only after human approval")
        print("engineer is a human proxy that approves or rejects the code")
        print(" 1. 'Run this code? (yes/no)' <- the approval gate")
        print(" 2. 'Enter your response:'    <- if human's turn as a teammate")
        print(" (type 'looks good' to continue, or ask for changes)")
        print("\n" + "=" * 80 + "\n")

        await Console(team.run_stream(task=TASK))
        await client.close()

asyncio.run(main())