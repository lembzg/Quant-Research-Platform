from dataclasses import dataclass
from sortedcontainers import SortedDict
from collections import deque

"""

Order side representation -
Written by Arryl Tham

Order side represents either the bid or ask side of the order book. It maintains a sorted dictionary of price levels, 
where each price level contains a deque of limit orders. The ascending flag indicates whether the order side is a bid (ascending) or an ask (descending).

Limit orders are represented by the LimitOrder dataclass, 
which contains information about the order such as 
order ID, 
timestamp, 
quantity, 
price, 
side, and whether it is a 
self trade.

SortedDict: A data structure that maintains its keys in sorted order, 
allowing for efficient retrieval of the best price levels.

Deque: FIFO queue. Order placed earlier gets filled first.

"""

@dataclass
class LimitOrder:
    order_id: str
    timestamp: int
    quantity: float
    price: float
    side: str
    is_self: bool
    
    """
    Update quantity of order after it has been created.
    Used during partial fills.
    """
    
    def set_quantity(self, quant: float):
        self.quantity = quant



class OrderSide:
    def __init__(self, ascending: bool):
        self.book = SortedDict()
        self.ascending = ascending

    """
    Insert a new limit order into the order book.
    If the price level does not exist, create an empty queue at that price level.
    """
    
    def insert(self, order: LimitOrder):
        if order.price not in self.book:
            self.book[order.price] = deque()
        self.book[order.price].append(order)

    # Return best price on the order side. For bids, this is the highest price, for asks, this is the lowest price.
    def best_price(self):
        if not self.book:
            return None
        if self.ascending:
            return self.book.peekitem(0)[0]
        return self.book.peekitem(-1)[0]

    # Return total quantity at the best price level.
    def best_orders(self):
        if not self.book:
            return None
        if self.ascending:
            return self.book.peekitem(0)[1]
        return self.book.peekitem(-1)[1]
    
    # Remove order after prices gets filled.
    def pop_best_order(self):
        if not self.book:
            return None
        
        if self.ascending:
            price, orders = self.book.peekitem(0)
            
            # Pop left removes from the front of queue
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
        
        
    

        
        
            

        





                

            



        



