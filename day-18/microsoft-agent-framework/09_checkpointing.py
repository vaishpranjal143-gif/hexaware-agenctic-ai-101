from typing import Never
from agent_framework import Executor, InMemoryCheckpointStorage, WorkflowBuilder, WorkflowContext, handler
from _maf import banner, run

banner("File -09 Checkpointing")

DONE: list[str] = []

class Validate(Executor):
    @handler
    async def go(self, order_id: str, ctx: WorkflowContext[str]) -> None:
        DONE.append("validate"); await ctx.send_message(order_id)

class Price(Executor):
    @handler
    async def go(self, order_id: str, ctx: WorkflowContext[Never, str]) -> None:
        DONE.append("price"); await ctx.yield_output(f"{order_id}: refund INR 10,000")

async def main():
    storage = InMemoryCheckpointStorage()
    validate, price = Validate(id="validate"), Price(id="price")
    workflow = (WorkflowBuilder(start_executor=validate, output_from=[price],
                               name="refund-run",
                               checkpoint_storage=storage)
                               .add_edge(validate, price).build())
    result = await workflow.run("HX-90455")
    print(f" steps that ran     : {DONE}")
    print(f" final result       : {result.get_outputs()}")

    saved = await storage.list_checkpoints(workflow_name="refund-run")
    print(f" saved checkpoints  : {len(saved)} saved - each one a resume point")
    for checkpoint in saved:
        print(f" {checkpoint.checkpoint_id} after step {checkpoint.iteration_count}")

run(main())