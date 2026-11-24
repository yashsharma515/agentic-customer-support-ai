
def check_refund_eligibility(order_details):

    status = order_details["status"]

    if status.lower() == "delivered":
        return {
            "eligible": True,
            "reason": "Order has been delivered. Refund eligibility can be reviewed."
        }

    else:
        return {
            "eligible": False,
            "reason": f"Order is currently {status}. Refund is not eligible yet under the demo policy."
        }
