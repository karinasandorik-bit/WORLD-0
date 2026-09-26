import hashlib, os, tempfile, unittest
from world0.core import Arm, PHYSICS_HASH, SPEC_JSON
from world0.experiment import run, experiment

class World0Tests(unittest.TestCase):
    def test_hash_is_stable(self):
        self.assertEqual(PHYSICS_HASH,hashlib.sha256(SPEC_JSON.encode()).hexdigest())
    def test_on_has_complete_information(self):
        self.assertEqual(run(7,Arm.ON),1.0)
    def test_deterministic(self):
        self.assertEqual(run(42,Arm.OFF),run(42,Arm.OFF))
    def test_frozen_ticks(self):
        with self.assertRaises(ValueError):
            run(1,Arm.ON,99)
    def test_small_ablation_executes(self):
        with tempfile.TemporaryDirectory() as d:
            result=experiment(5,os.path.join(d,"events.sqlite"))
            self.assertEqual(result["nseeds"],5)
            self.assertGreater(result["mean_reward"]["COMM_ON"],result["mean_reward"]["COMM_OFF"])
            self.assertGreater(result["mean_reward"]["COMM_ON"],result["mean_reward"]["COMM_SHUFFLED"])
if __name__=="__main__":
    unittest.main()
