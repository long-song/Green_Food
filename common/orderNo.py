import time

# 生成订单号
def get_order_code():
    order_no = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))+ str(time.time()).replace('.', '')[-7:]
    # print('time.time()=',time.time())
    # print(order_no)
    return order_no

if __name__ == '__main__':
    get_order_code()