import time
import json
from typing import Optional

class GlobalEventJournal:
    def __init__(self, session_id: str, world_seed: int):
        self.session_id = session_id
        self.world_seed = world_seed
        self.events = []
        # Record initial state
        self.record_event("session_start", "system", {"world_seed": world_seed})

    def record_event(self, event_type: str, actor_id: str, data: dict, plan_id: Optional[str] = None, intention_id: Optional[str] = None, rng_seed: Optional[int] = None):
        print(f"EVENT: {actor_id} - {event_type} - {data}")
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "actor_id": actor_id,
            "data": data,
            "plan_id": plan_id,
            "intention_id": intention_id,
            "rng_seed": rng_seed
        }
        self.events.append(event)
        return event

    def save_session(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "world_seed": self.world_seed,
                "events": self.events
            }, f, indent=2)
        print(f"Session saved to {filepath}")

    def get_recent_events(self, limit: int = 100):
        return self.events[-limit:]

    def log(self, actor_id: str, message: str):
        self.record_event("log", actor_id, {"message": message})
