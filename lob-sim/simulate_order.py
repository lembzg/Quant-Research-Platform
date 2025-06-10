from dataclasses import dataclass


@dataclass
class SimulatedOrder:
    order_id: str
    timestamp: float
    price: float
    side: str
    quantity: float
    filled_quantity: float = 0.0
    fills: list
    status: str = "open"

    def __post_init__(self):
        self.fills = []

    def record_fill(self, quantity, timestamp, price):
        self.filled_quantity += quantity
        self.fills.append((timestamp, price, quantity))
        if self.filled_quantity == self.quantity:
            self.status = "filled"
        else:
            self.status = "partial"

