from dataclasses import dataclass
@dataclass
class Trade:
    timestamp: int
    price: float
    quantity: float
    side: str
    take_order_ID: int #ID of order that just arrived
    make_order_ID: int #ID of order that was resting in the book
    is_self: bool
