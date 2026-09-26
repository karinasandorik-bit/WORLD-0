import hashlib,unittest
from world1.trial import SPEC_JSON,SPEC_HASH,Arm,cases,QAgent,episode

class Trial1Tests(unittest.TestCase):
 def test_hash(self):
  self.assertEqual(SPEC_HASH,hashlib.sha256(SPEC_JSON.encode()).hexdigest())
 def test_world_deterministic(self):
  self.assertEqual(cases(4),cases(4))
 def test_no_acquire_is_physical(self):
  a=QAgent(1);r=episode(a,1000,Arm.NO_ACQUIRE,False);self.assertEqual(r["acq_rate"],0)
 def test_market_costs_information(self):
  a=QAgent(1);a.q[(("acq",0),"BUY0")]=10;a.q[(("acq",1),"BUY0")]=10
  r=episode(a,1000,Arm.MARKET,False);self.assertGreater(r["acq_rate"],.95)
 def test_oos_seed_is_disjoint(self):
  self.assertTrue(set(range(200)).isdisjoint(range(1000,1200)))
if __name__=="__main__":unittest.main()
