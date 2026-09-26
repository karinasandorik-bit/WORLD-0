import hashlib,json,random,statistics
from dataclasses import dataclass
from enum import Enum

class Arm(str,Enum):
    MARKET="MARKET"; FREE="FREE"; NO_ACQUIRE="NO_ACQUIRE"; SHUFFLED="SHUFFLED_VALUE"

SPEC={
 "trial":"WORLD-1/TRIAL-1","agents":3,"train_seeds":[0,199],"oos_seeds":[1000,1199],
 "ticks":200,"regimes":["LOCAL","DISTRIBUTED","DECOY"],
 "acquire_cost":0.15,"correct_reward":1.0,"wrong_reward":-1.0,
 "alpha":0.12,"gamma":0.0,"epsilon_train":0.12,"epsilon_eval":0.0,
 "arms":[a.value for a in Arm]
}
SPEC_JSON=json.dumps(SPEC,sort_keys=True,separators=(",",":"))
SPEC_HASH=hashlib.sha256(SPEC_JSON.encode()).hexdigest()

@dataclass(frozen=True)
class Case:
    regime:str; truth:int; local:int; offers:tuple

def cases(seed,ticks=200):
    r=random.Random(seed); out=[]
    for _ in range(ticks):
        regime=r.choice(("LOCAL","DISTRIBUTED","DECOY")); truth=r.getrandbits(1)
        if regime=="LOCAL":
            local=truth; useful=r.getrandbits(1)
        elif regime=="DISTRIBUTED":
            local=r.getrandbits(1); useful=truth
        else:
            local=r.getrandbits(1); useful=r.getrandbits(1)
        decoy=r.getrandbits(1)
        # useful source position varies, so source identity itself must be learned from outcomes.
        if r.getrandbits(1): offers=(useful,decoy)
        else: offers=(decoy,useful)
        out.append(Case(regime,truth,local,offers))
    return out

class QAgent:
    def __init__(self,seed):
        self.q={}; self.r=random.Random(seed)
    def choose(self,key,actions,eps):
        if self.r.random()<eps:return self.r.choice(actions)
        vals=[self.q.get((key,a),0.0) for a in actions]; m=max(vals)
        return actions[vals.index(m)]
    def update(self,key,action,reward,alpha=.12):
        old=self.q.get((key,action),0.0); self.q[(key,action)]=old+alpha*(reward-old)

def shuffled_offers(cs,seed):
    cols=[[c.offers[j] for c in cs] for j in range(2)]
    for j,col in enumerate(cols): random.Random(seed*7919+j+17).shuffle(col)
    return [tuple(cols[j][t] for j in range(2)) for t in range(len(cs))]

def episode(agent,seed,arm,train=True):
    cs=cases(seed); sh=shuffled_offers(cs,seed) if arm==Arm.SHUFFLED else None
    eps=SPEC["epsilon_train"] if train else 0.0; cost=0 if arm==Arm.FREE else SPEC["acquire_cost"]
    total=0; acquired=0; byreg={r:[0,0] for r in SPEC["regimes"]}
    for t,c in enumerate(cs):
        key=("acq",c.local)
        actions=("SKIP",) if arm==Arm.NO_ACQUIRE else ("SKIP","BUY0","BUY1")
        a=agent.choose(key,actions,eps); value=None
        if a!="SKIP":
            acquired+=1; byreg[c.regime][0]+=1
            j=int(a[-1]); value=(sh[t][j] if sh is not None else c.offers[j])
        byreg[c.regime][1]+=1
        actkey=("act",c.local,a,value)
        pred=int(agent.choose(actkey,(0,1),eps))
        utility=(1.0 if pred==c.truth else -1.0)-(cost if a!="SKIP" else 0)
        total+=utility
        if train:
            agent.update(actkey,pred,utility)
            agent.update(key,a,utility)
    return {"utility":total/len(cs),"acq_rate":acquired/len(cs),
      "regime_acq":{r:x[0]/x[1] if x[1] else 0 for r,x in byreg.items()}}

def train_agents(arm):
    agents=[QAgent(9000+i) for i in range(3)]
    for seed in range(200):
        for a in agents: episode(a,seed,arm,True)
    return agents

def bootstrap(ds,seed=20260926,n=5000):
    r=random.Random(seed); m=len(ds); xs=[]
    for _ in range(n): xs.append(statistics.mean(ds[r.randrange(m)] for _ in range(m)))
    xs.sort(); return [xs[int(.025*n)],xs[int(.975*n)]]
