import random
import time as pytime


class PendingSync:
    """Ek pending mesh-sync jo abhi 'in-flight' hai — real network delay simulate karta hai."""
    def __init__(self, drone_a, drone_b, deliver_at):
        self.drone_a = drone_a
        self.drone_b = drone_b
        self.deliver_at = deliver_at


class NetworkEmulator:
    """
    Real wireless mesh network ke 2 sabse common imperfections simulate
    karta hai: latency (data turant nahi pahunchta) aur packet loss
    (kabhi data corrupt/lost ho jaata hai). Isse mesh-sync 'instant aur
    perfect' na hoke, real network jaisa unpredictable dikhta hai.
    """
    def __init__(self):
        self.pending = []
        self.stats = {'sent': 0, 'delivered': 0, 'lost': 0}

    def request_sync(self, drone_a, drone_b, latency_min, latency_max, loss_chance):
        self.stats['sent'] += 1

        if random.random() < loss_chance:
            self.stats['lost'] += 1
            return  # packet lost — sync is baar hoga hi nahi

        delay = random.uniform(latency_min, latency_max)
        deliver_at = pytime.time() + delay
        self.pending.append(PendingSync(drone_a, drone_b, deliver_at))

    def process(self, sync_function):
        """Har frame check karo kaunse pending syncs ab deliver hone ka time aa gaya."""
        now = pytime.time()
        still_pending = []

        for p in self.pending:
            if now >= p.deliver_at:
                sync_function(p.drone_a, p.drone_b)
                self.stats['delivered'] += 1
            else:
                still_pending.append(p)

        self.pending = still_pending

    def get_reliability_percent(self):
        if self.stats['sent'] == 0:
            return 100.0
        return round((self.stats['delivered'] / self.stats['sent']) * 100, 1)

