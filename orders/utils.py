import time

def generate_order_no(user_id):
    order_base = time.time()
    order_number = str(int(order_base)) + str(user_id)
    print("order_number is ",order_number)
    return order_number

