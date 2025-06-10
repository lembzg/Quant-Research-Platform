from simulate_order import SimulatedOrder
from trade import Trade

class SimulatedOrderTracker():
    
    def __init__(self):
        self.sim_orders = {}
    
    def register(self, sim_order: SimulatedOrder):
        self.sim_orders[sim_order.order_id] = sim_order
        return sim_order
    
    def update_fills(self, trade : Trade):
        if trade.is_self:
            sim_order = self.sim_orders.get(trade.take_order_ID)
            if sim_order:
                sim_order.record_fill(quantity=trade.quantity, timestamp=trade.timestamp, price=trade.price)
    
    