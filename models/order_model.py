from pydantic import BaseModel

class Order(BaseModel):
    customer_name: str
    frame_size: str
    wood_type: str
    finish: str
    image_url: str