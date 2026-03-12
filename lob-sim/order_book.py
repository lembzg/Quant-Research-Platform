from order_side import OrderSide, LimitOrder
from trade import Trade

"""

Orderbook class holds both sides of the order side,
and handles the matching logic between them.

Order side manages one side in isolation.

"""
class OrderBook:
    def __init__(self):
        self.asks = OrderSide(True)
        self.bids = OrderSide(False)

    """
    
    Check if incoming order is matchable against opposite side.
    
    """
    
    def matchable(self, order):
        if order.side == 'buy':
            if self.asks.best_price() is None:
                return False
            if order.price >= self.asks.best_price():
                return True
            else:
                return False

        else:
            if self.bids.best_price() is None:
                return False
            if order.price <= self.bids.best_price():
                return True
            else:
                return False

    """
    
    Insert unmatched order into order book.
        
    """
    
    def insert_unmatched_order(self, order):
        if order.is_self:
            return
        
        # Insert order into order book if not matchable.
        if not self.matchable(order):
            if order.side == 'buy':
                self.bids.insert(order)
                print(f'Bid @ Price: {order.price} Qty: {order.quantity} inserted')
            else:
                self.asks.insert(order)
                print(f'Ask @ Price: {order.price} Qty: {order.quantity} inserted')
    
    
    """
    
    Helper function to simulate trades for self orders.
        
    """
    
    def _simulate_match(self, order, best_order, trade_quant):      
        return Trade(timestamp=order.timestamp,
                                    price=best_order.price,
                                    quantity=trade_quant,
                                    side=order.side,
                                    take_order_ID=order.order_id,
                                    make_order_ID=best_order.order_id,
                                    is_self=order.is_self
                                    )
    
    
    """
    
    Simuate limit order and return trades generated from the order.
        
    """
    
    def add_limit_order(self, order: LimitOrder):
        trades = []
        
        
        """
        
        Buy Side logic:
        keep matching against best ask until order is fully filled or no more matchable asks.
        
        """
        
        while order.quantity > 0 and self.matchable(order):   
            if order.side == 'buy':
                best_queue = self.asks.best_orders()
                best_order = best_queue[0]

                if best_order.quantity > order.quantity:
                    trade_quant = min(best_order.quantity, order.quantity)
                    if order.is_self == False:
                        best_order.quantity -= trade_quant
                    else:
                        trade = self._simulate_match(order, best_order, trade_quant)
                        trades.append(trade)
                    print(f'Buy order @ {order.price} filled')
                    
                else:
                    trade_quant = min(best_order.quantity, order.quantity)
                    order.quantity -= trade_quant
                    if order.is_self == False:
                        best_order.quantity -= trade_quant
                    else:
                        trade = self._simulate_match(order, best_order, trade_quant)
                        trades.append(trade)
                    print(f'Buy order @ {order.price} fully matched against ask @ {best_order.price}')
                    if order.is_self == False:
                        self.asks.pop_best_order()
            
        
            
            else:
                
                """
            Ask side logic: Identical to sell side.
            
                """
                best_queue = self.bids.best_orders()
                best_order = best_queue[0]
                if best_order.quantity > order.quantity:
                    trade_quant = min(best_order.quantity, order.quantity)
                    if order.is_self == False:
                        best_order.quantity -= trade_quant                   
                    else:
                        trade = self._simulate_match(order, best_order, trade_quant)
                        trades.append(trade)
                    print(f'Sell order @ {order.price} filled')
                
                else:
                    trade_quant = min(best_order.quantity, order.quantity)
                    order.quantity -= trade_quant
                    if order.is_self == False:
                        best_order.quantity -= trade_quant
                    else:
                        trade = self._simulate_match(order, best_order, trade_quant)
                        trades.append(trade)
                    print(f'Sell order @ {order.price} fully matched against bid @ {best_order.price}')
                    if order.is_self == False:
                        self.bids.pop_best_order()

        if order.quantity > 0 and not order.is_self:
            self.insert_unmatched_order(order)

        return trades
    
    def simulate_limit_order(self, order: LimitOrder):
        order.is_self = True
        return self.add_limit_order(order)
        
    
    

            


                


        