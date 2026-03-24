import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.ai_systems import TraitSystem
import random

def test_phase11_priors():
    # 1. Test Baseline Priors
    priors = {"aggression": 0.8, "friendliness": 0.1}
    # Create multiple instances with same seed - should be identical
    t1 = TraitSystem(priors, rng=random.Random(1337))
    t2 = TraitSystem(priors, rng=random.Random(1337))
    
    print(f"Agent 1 Traits: {t1.traits}")
    print(f"Agent 2 Traits: {t2.traits}")
    
    assert t1.traits == t2.traits, "Deterministic variance failed!"
    
    # 2. Test Variance
    t3 = TraitSystem(priors, rng=random.Random(1337))
    print(f"Agent 3 Traits: {t3.traits}")
    assert t1.traits != t3.traits, "Individual variance failed (no variance detected)!"
    
    # Check if within expected range (+/- 0.2 of prior)
    agg = t3.traits["aggression"]
    if 0.6 <= agg <= 1.0:
        print(f"PASSED: Aggression {agg:.2f} is within variance range of prior 0.8")
    else:
        print(f"FAILED: Aggression {agg:.2f} out of range!")
        exit(1)

if __name__ == "__main__":
    test_phase11_priors()
