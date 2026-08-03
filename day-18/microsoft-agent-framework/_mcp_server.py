import logging

from mcp.server.fastmcp import FastMCP

logging.disable(logging.INFO)

server = FastMCP("hex-orders")

ORDERS = {"HX-90455": (12, True), "HX-90456": (34, False)}

@server.tool()
def lookup_order(order_id: str) -> str:
    """Look up a Hex Retail order and return its delivery status."""
    record = ORDERS.get(order_id)
    if record is None:
        return f"No order {order_id} exists."
    return f"{order_id}: delivered {record[0]} days ago, faulty={record[1]}"

if __name__ == "__main__":
    server.run(transport="stdio")