

import json

def get_order_status(order_id):

    with open("orders.json", "r") as file:
        orders = json.load(file)

    if order_id in orders:
        return orders[order_id]

    else:
        return None




# import json

# def get_order_status(order_id):

#     # Open the order database
#     with open("orders.json", "r") as file:
#         orders = json.load(file)

#     # Check whether order ID exists
#     if order_id in orders:
#         return orders[order_id]

#     else:
#         return None


# # Test the function
# order_id = input("Enter Order ID: ")

# order = get_order_status(order_id)

# if order:
#     print("\nOrder Details:")
#     print(order)

# else:
#     print("\nOrder not found.")
