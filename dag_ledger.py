import hashlib
import random
import time as pytime


class DAGNode:
    """Ek single event/transaction — DAG mein ek node."""
    def __init__(self, index, event, parent_ids, timestamp=None):
        self.id = f"{index}_{random.randint(1000,9999)}"
        self.index = index
        self.event = event
        self.parent_ids = parent_ids  # list of 2 (ya 0 for genesis) parent node IDs
        self.timestamp = timestamp if timestamp is not None else round(pytime.time(), 3)
        self.hash = self._compute_hash()

    def _compute_hash(self):
        payload = f"{self.index}{self.event}{self.parent_ids}{self.timestamp}"
        return hashlib.sha256(payload.encode()).hexdigest()[:12]


class DAGLedger:
    """
    Tangle-jaisa DAG ledger — har drone apna khud ka DAG maintain karta hai.
    Naya event 2 purane 'tips' (jo abhi tak kisi aur se approve nahi hue)
    ko select karke unse link hota hai. Jitne zyada events kisi purane
    event ko (directly/indirectly) approve karte hain, uska confirmation
    weight utna zyada — koi central authority validate nahi karti.
    """
    def __init__(self):
        self.nodes = {}   # id -> DAGNode
        genesis = DAGNode(0, "MISSION_START", parent_ids=[])
        self.nodes[genesis.id] = genesis
        self.tips = {genesis.id}   # abhi tak koi isse approve nahi karta

    def get_tips_for_new_event(self):
        """2 random tips select karo jo naya event approve karega (Tangle ka tip-selection)."""
        available = list(self.tips)
        if len(available) == 0:
            return []
        if len(available) == 1:
            return [available[0]]
        return random.sample(available, 2)

    def add_event(self, event):
        """Naya event add karo — automatically 2 tips ko approve karega."""
        parents = self.get_tips_for_new_event()
        new_index = max(n.index for n in self.nodes.values()) + 1
        node = DAGNode(new_index, event, parents)
        self.nodes[node.id] = node

        # parents ab tips nahi rahe (unhe approve kar diya gaya)
        for p in parents:
            self.tips.discard(p)
        self.tips.add(node.id)

        return node

    def compute_confirmation_weight(self, node_id):
        """
        Kitne nodes (directly/indirectly) is node ko approve karte hain —
        BFS/graph traversal se. Zyada weight = zyada trustworthy.
        """
        weight = 0
        visited = set()
        stack = [nid for nid, n in self.nodes.items() if node_id in n.parent_ids]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            weight += 1
            node = self.nodes.get(current)
            if node:
                stack.extend(nid for nid, n in self.nodes.items() if current in n.parent_ids)

        return weight

    def validate_node(self, node_id):
        """Hash-integrity check — agar node tamper hua hai to hash recompute karke mismatch milega."""
        node = self.nodes.get(node_id)
        if node is None:
            return False
        expected_hash = node._compute_hash()
        return expected_hash == node.hash

    def validate_full_dag(self):
        """Poore DAG ki integrity check — koi bhi node tamper hua ho to False."""
        for node_id in self.nodes:
            if not self.validate_node(node_id):
                return False
        return True

    def merge(self, other_dag):
        """
        Doosre drone ke DAG ke saath merge karo — Tangle mein consensus
        aise hi build hota hai, jitna zyada nodes share hote hain utna
        zyada network agree karta hai.
        """
        for node_id, node in other_dag.nodes.items():
            if node_id not in self.nodes:
                self.nodes[node_id] = node
                # agar ye node kisi tip ko approve karta hai, wo tip ab tip nahi
                for p in node.parent_ids:
                    self.tips.discard(p)
                if not any(node_id in n.parent_ids for n in self.nodes.values()):
                    self.tips.add(node_id)

    def size(self):
        return len(self.nodes)