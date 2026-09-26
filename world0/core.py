from dataclasses import dataclass
from enum import Enum
import hashlib, json, random

class Arm(str, Enum):
    OFF="COMM_OFF"; ON="COMM_ON"; SHUFFLED="COMM_SHUFFLED"

FROZEN_SPEC={
 "trial":"WORLD-0/TRIAL-0","agents":3,"ticks":100,
 "state":"3 iid fair bits per tick","observation":"agent i sees xi",
 "action":"predict parity(x0,x1,x2)","reward":"1 correct else 0",
 "policy":"xor available bits; missing bits=0",
 "arms":["COMM_OFF","COMM_ON","COMM_SHUFFLED"],
 "seeds":"0..999 confirmatory"
}
SPEC_JSON=json.dumps(FROZEN_SPEC,sort_keys=True,separators=(",",":"))
PHYSICS_HASH=hashlib.sha256(SPEC_JSON.encode()).hexdigest()

@dataclass(frozen=True)
class Observation:
    tick:int
    agent_id:int
    bit:int

class HiddenPhysics:
    def __init__(self,seed:int):
        self.rng=random.Random(seed)
    def state(self):
        return tuple(self.rng.getrandbits(1) for _ in range(3))

class Agent:
    def __init__(self,agent_id:int):
        self.agent_id=agent_id
    def message(self,obs:Observation):
        return obs.bit
    def act(self,obs:Observation,inbox:dict[int,int]):
        bits={self.agent_id:obs.bit,**inbox}
        return bits.get(0,0)^bits.get(1,0)^bits.get(2,0)

def shuffled_messages(states,seed:int):
    out=[[None]*3 for _ in states]
    for sender in range(3):
        values=[s[sender] for s in states]
        rng=random.Random((seed+1)*1009+sender)
        rng.shuffle(values)
        for tick,value in enumerate(values):
            out[tick][sender]=value
    return out
