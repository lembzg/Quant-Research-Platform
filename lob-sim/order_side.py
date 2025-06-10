from dataclasses import dataclass
from sortedcontainers import SortedDict
from collections import deque


@dataclass
class LimitOrder:
    order_id: str
    timestamp: int
    quantity: float
    price: float
    side: str
    is_self: bool

    def set_quantity(self, quant: float):
        self.quantity = quant

class OrderSide:
    def __init__(self, ascending: bool):
        self.book = SortedDict()
        self.ascending = ascending

    def insert(self, order: LimitOrder):
        if order.price not in self.book:
            self.book[order.price] = deque()
        self.book[order.price].append(order)

    def best_price(self):
        if not self.book:
            return None
        if self.ascending:
            return self.book.peekitem(0)[0]
        return self.book.peekitem(-1)[0]

    def best_orders(self):
        if not self.book:
            return None
        if self.ascending:
            return self.book.peekitem(0)[1]
        return self.book.peekitem(-1)[1]
    
    def pop_best_order(self):
        if not self.book:
            return None
        
        if self.ascending:
            price, orders = self.book.peekitem(0)
            order = orders.popleft()
            if not orders:
                del self.book[price]
            return order
        
        if not self.ascending:
            price, orders = self.book.peekitem(-1)
            order = orders.popleft()
            if not orders:
                del self.book[price]
            return order
    

        
        
            

        





                

            



        



