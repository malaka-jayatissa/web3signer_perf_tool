import uuid
from config import properties
from dataclasses import dataclass

@dataclass
class Result:
    return_code: int
    payload: str
    latency: int
    def __init__(self, return_code:int, payload: dict, latency: int):
        self.return_code = return_code
        self.payload = payload
        self.latency = latency


class State:
    def __init__(self):
        self.prefix = str(uuid.uuid4())
        self.results = [None] * properties.SAMPLE_SIZE

    def add_result(self, index : int, result: Result):
        self.results[index] = result

    def reset_state(self):
        self.prefix = str(uuid.uuid4())
        self.results = [None] * properties.SAMPLE_SIZE



def hello():
    print("Hello from state")



STATE = State()