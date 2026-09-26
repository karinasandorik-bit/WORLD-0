import argparse, json, random, statistics
from pathlib import Path
from .core import Agent, Arm, FROZEN_SPEC, PHYSICS_HASH, HiddenPhysics, Observation, shuffled_messages
from .ledger import Ledger

def run(seed:int,arm:Arm,ticks:int=100,ledger=None):
    if ticks!=FROZEN_SPEC["ticks"]:
        raise ValueError("Trial-0 ticks are frozen at 100")
    physics=HiddenPhysics(seed)
    states=[physics.state() for _ in range(ticks)]
    shuffled=shuffled_messages(states,seed) if arm==Arm.SHUFFLED else None
    agents=[Agent(i) for i in range(3)]
    rewards=[]
    run_id=f"trial0-s{seed}-{arm.value}"
    for tick,state in enumerate(states):
        truth=state[0]^state[1]^state[2]
        for agent in agents:
            obs=Observation(tick,agent.agent_id,state[agent.agent_id])
            if arm==Arm.OFF:
                inbox={}
            elif arm==Arm.ON:
                inbox={j:state[j] for j in range(3) if j!=agent.agent_id}
            else:
                inbox={j:shuffled[tick][j] for j in range(3) if j!=agent.agent_id}
            prediction=agent.act(obs,inbox)
            reward=int(prediction==truth)
            rewards.append(reward)
            if ledger:
                ledger.append(run_id,tick,agent.agent_id,arm.value,"DECISION",
                  {"observation":obs.bit,"inbox":inbox,"prediction":prediction,"truth":truth,"reward":reward},
                  PHYSICS_HASH)
    return sum(rewards)/len(rewards)

def bootstrap_ci(deltas,seed=20260926,n=5000):
    rng=random.Random(seed)
    size=len(deltas)
    means=[statistics.mean(deltas[rng.randrange(size)] for _ in range(size)) for _ in range(n)]
    means.sort()
    return [means[int(.025*n)],means[int(.975*n)]]

def experiment(nseeds=1000,db_path="world0.sqlite"):
    if not 1<=nseeds<=1000:
        raise ValueError("Trial-0 uses a prefix of frozen seeds 0..999")
    ledger=Ledger(db_path)
    rows=[]
    try:
        for seed in range(nseeds):
            row={arm.value:run(seed,arm,100,ledger) for arm in Arm}
            row["seed"]=seed
            rows.append(row)
    finally:
        ledger.close()
    off=[r["COMM_ON"]-r["COMM_OFF"] for r in rows]
    shuffled=[r["COMM_ON"]-r["COMM_SHUFFLED"] for r in rows]
    return {
      "physics_hash":PHYSICS_HASH,"nseeds":nseeds,
      "mean_reward":{arm.value:statistics.mean(r[arm.value] for r in rows) for arm in Arm},
      "on_minus_off":{"mean":statistics.mean(off),"ci95":bootstrap_ci(off)},
      "on_minus_shuffled":{"mean":statistics.mean(shuffled),"ci95":bootstrap_ci(shuffled)}
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seeds",type=int,default=1000)
    p.add_argument("--ticks",type=int,default=100)
    p.add_argument("--db",default="world0.sqlite")
    p.add_argument("--out",default="result.json")
    args=p.parse_args()
    if args.ticks!=100:
        raise SystemExit("Trial-0 is frozen at 100 ticks")
    result=experiment(args.seeds,args.db)
    Path(args.out).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    main()
