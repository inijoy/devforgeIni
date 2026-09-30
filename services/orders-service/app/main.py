from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="DevForge Orders Service",
    description="Orders microservice for the DevForge Internal Developer Platform",
    version="0.1.0",
)


class OrderCreate(BaseModel):
    product: str
    quantity: int
    customer: str


class OrderResponse(BaseModel):
    id: int
    product: str
    quantity: int
    customer: str


orders: list[OrderResponse] = []


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "orders-service",
        "version": "0.1.0",
    }


@app.get("/")
def root():
    return {
        "service": "orders-service",
        "message": "DevForge Orders Service is running",
    }


@app.get("/orders", response_model=list[OrderResponse])
def get_orders():
    return orders


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    if order_id < 1 or order_id > len(orders):
        raise HTTPException(status_code=404, detail="Order not found")

    return orders[order_id - 1]


@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate):
    new_order = OrderResponse(
        id=len(orders) + 1,
        product=order.product,
        quantity=order.quantity,
        customer=order.customer,
    )

    orders.append(new_order)

    return new_order