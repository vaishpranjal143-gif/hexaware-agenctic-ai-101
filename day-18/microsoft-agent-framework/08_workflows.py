from typing import Never
from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler
from _maf import ORDERS, banner, run

banner("MAF - File 08 - workflows - how to build a workflow - you own the execution order")

class CheckOrder(Executor):
    """NODE 1: look the order up and pass a verdict along the edge."""

    @handler
    async def go(self, order_id: str, ctx: WorkflowContext[str]) -> None:
        record = ORDERS.get(order_id)
        verdict = ("unknown order" if record is None
                   else f"{order_id} delievered {record['days']} days ago, faulty={record['faulty']}")
        await ctx.send_message(verdict)

class DecideRefund(Executor):
    """"NODE 2: apply the policy and finish"""

    @handler
    async def go(self, verdict: str, ctx: WorkflowContext[Never, str]) -> None:
        allowed = "faulty=True" in verdict or " 21 days" in verdict
        await ctx.yield_output(f"{verdict} -> {'APPROVE' if allowed else 'REJECT'}")

async def main():
    check, decide = CheckOrder(id="check"), DecideRefund(id="decide")
    workflow = (WorkflowBuilder(start_executor=check, output_from=[decide]).add_edge(check, decide).build())

    for order_id in ("HX-90455", "HX-90456", "HX-90457"):
        result = await workflow.run(order_id)
        print(f" order {order_id} : {result.get_outputs()}")
    print()
    print(" Same graph, three inputs. The PATH never varied - we defined it. The agent never had to decide what to do next - we did that for it.")

run(main())