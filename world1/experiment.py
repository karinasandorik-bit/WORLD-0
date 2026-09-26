import argparse,json,statistics
from pathlib import Path
from .trial import Arm,SPEC,SPEC_HASH,train_agents,episode,bootstrap

def evaluate():
    trained={arm:train_agents(arm) for arm in Arm}; rows=[]
    for seed in range(1000,1200):
        row={"seed":seed}
        for arm in Arm:
            vals=[episode(a,seed,arm,False) for a in trained[arm]]
            row[arm.value]={
              "utility":statistics.mean(v["utility"] for v in vals),
              "acq_rate":statistics.mean(v["acq_rate"] for v in vals),
              "regime_acq":{r:statistics.mean(v["regime_acq"][r] for v in vals) for r in SPEC["regimes"]}
            }
        rows.append(row)
    def delta(a,b): return [r[a]["utility"]-r[b]["utility"] for r in rows]
    d0=delta("MARKET","NO_ACQUIRE"); ds=delta("MARKET","SHUFFLED_VALUE")
    market=[r["MARKET"] for r in rows]
    return {"spec_hash":SPEC_HASH,"oos_seeds":200,
      "utility":{a.value:statistics.mean(r[a.value]["utility"] for r in rows) for a in Arm},
      "market_acq_rate":statistics.mean(x["acq_rate"] for x in market),
      "market_regime_acq":{rg:statistics.mean(x["regime_acq"][rg] for x in market) for rg in SPEC["regimes"]},
      "market_minus_no_acquire":{"mean":statistics.mean(d0),"ci95":bootstrap(d0)},
      "market_minus_shuffled":{"mean":statistics.mean(ds),"ci95":bootstrap(ds)}}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",default="world1_result.json");a=p.parse_args()
    r=evaluate();Path(a.out).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=="__main__":main()
