"""
dag_consensus.py — SwarmOS Consensus Hardening Layer
=====================================================
Baseline dag_ledger.py (asli repo mein) already ek real Tangle-jaisa DAG
hai — tip-selection, confirmation-weight, hash-integrity check, merge.
Yeh already achha hai, sirf README isse "hash-chain" bol ke undersell
karta hai.

Lekin ek genuine gap hai: `DAGLedger.merge()` kisi bhi incoming node ko
BLINDLY accept kar leta hai — tamper sirf baad mein `validate_full_dag()`
manually call karne pe pakda jaata hai. Ek real consensus system mein
tampered data door pe hi reject honi chahiye, taaki wo mesh mein
propagate hi na ho — "detect after the fact" se "refuse at the door" tak.

Yeh module DAGLedger ko subclass karke teen cheezein add karta hai:
  1. Validate-before-accept merge — hash-invalid node kabhi accept nahi hota
  2. Per-source reputation — jo drone baar-baar invalid data bhejta hai,
     uske future events bhi auto-reject hote hain (quarantine)
  3. Quorum tie-break — agar do drones ek hi mission-critical event ke
     conflicting versions report karte hain, jyada confirmation-weight
     wala version jeetta hai (majority consensus, koi authority nahi)

Existing `drone.compromised` flag (jo boids.py mein already use hota hai
separation ke liye) isi quarantine status se drive ho sakta hai — ek
compromised drone jise consensus ne quarantine kiya, wo boids mein bhi
automatically ignore ho jayega.
"""
from dag_ledger import DAGLedger, DAGNode


class ConsensusDAGLedger(DAGLedger):
    def __init__(self, owner_id=None):
        super().__init__()
        self.owner_id = owner_id
        self.reputation = {}       # source_drone_id -> int (negative = bad)
        self.quarantined = set()   # source_drone_id jinke events ab reject hote hain
        self.rejected_count = 0

    # -- reputation -----------------------------------------------------
    def _penalize(self, source_id, amount=1):
        self.reputation[source_id] = self.reputation.get(source_id, 0) - amount
        if self.reputation[source_id] <= -3:
            self.quarantined.add(source_id)

    def _reward(self, source_id, amount=1):
        self.reputation[source_id] = self.reputation.get(source_id, 0) + amount

    # -- hardened merge ---------------------------------------------------
    def merge(self, other_dag, source_id=None):
        """
        Jaisa baseline merge, LEKIN har incoming node ko accept karne se
        pehle uska hash validate karta hai. Invalid node door pe hi reject
        — kabhi is drone ke DAG mein enter nahi hota, isliye aage propagate
        bhi nahi ho sakta.
        """
        if source_id in self.quarantined:
            self.rejected_count += len(other_dag.nodes)
            return  # quarantined source se kuch bhi accept nahi karte

        accepted, rejected = 0, 0

        for node_id, node in other_dag.nodes.items():
            if node_id in self.nodes:
                continue

            expected_hash = node._compute_hash()
            if expected_hash != node.hash:
                rejected += 1
                self.rejected_count += 1
                if source_id is not None:
                    self._penalize(source_id)
                continue  # <-- yehi hardening: tampered node kabhi add nahi hota

            self.nodes[node_id] = node
            accepted += 1
            for p in node.parent_ids:
                self.tips.discard(p)
            if not any(node_id in n.parent_ids for n in self.nodes.values()):
                self.tips.add(node_id)

        if source_id is not None and rejected == 0 and accepted > 0:
            self._reward(source_id)

        return {"accepted": accepted, "rejected": rejected}

    # -- quorum conflict resolution ---------------------------------------
    def resolve_conflict(self, node_ids):
        """
        Diye gaye node_ids (jo ek hi mission-event ke conflicting versions
        maane jaate hain) mein se jiska confirmation-weight sabse zyada hai
        wahi "winning" version hai — koi central authority decide nahi
        karti, jitna zyada swarm ne (indirectly) us version ko approve
        kiya hai wahi jeetta hai.
        """
        if not node_ids:
            return None
        weights = {nid: self.compute_confirmation_weight(nid) for nid in node_ids if nid in self.nodes}
        if not weights:
            return None
        return max(weights, key=weights.get)


def sync_dags_hardened(drone_a, drone_b):
    """mesh_comms.sync_dags ka drop-in replacement — reputation-aware."""
    drone_a.dag.merge(drone_b.dag, source_id=drone_b.id)
    drone_b.dag.merge(drone_a.dag, source_id=drone_a.id)

    # quarantine consensus se drone.compromised flag update — isse boids.py
    # (jo already drone.compromised check karta hai) automatically
    # quarantined drones ko ignore karega, koi extra wiring nahi chahiye
    drone_a.compromised = drone_a.id in drone_b.dag.quarantined if hasattr(drone_b.dag, "quarantined") else drone_a.compromised
    drone_b.compromised = drone_b.id in drone_a.dag.quarantined if hasattr(drone_a.dag, "quarantined") else drone_b.compromised


# ---------------------------------------------------------------------
# Self-test — baseline (blind-accept) vs hardened (validate-before-accept)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Baseline DAGLedger.merge() — blind accept ===")
    a, b = DAGLedger(), DAGLedger()
    a.add_event("LAUNCH_A")
    b.add_event("LAUNCH_B")

    fake = DAGNode(index=99, event="UNAUTHORIZED_CMD", parent_ids=list(b.tips)[:1])
    fake.hash = "TAMPERED0000"
    b.nodes[fake.id] = fake
    b.tips.add(fake.id)

    a.merge(b)
    print(f"  Nodes in A after merge: {a.size()}  (tampered node included: {'TAMPERED0000' in [n.hash for n in a.nodes.values()]})")
    print(f"  a.validate_full_dag() = {a.validate_full_dag()}  <- only NOW do we notice something's wrong")

    print("\n=== Hardened ConsensusDAGLedger.merge() — validate at the door ===")
    ca, cb = ConsensusDAGLedger(owner_id="drone_A"), ConsensusDAGLedger(owner_id="drone_B")
    ca.add_event("LAUNCH_A")
    cb.add_event("LAUNCH_B")

    fake2 = DAGNode(index=99, event="UNAUTHORIZED_CMD", parent_ids=list(cb.tips)[:1])
    fake2.hash = "TAMPERED0000"
    cb.nodes[fake2.id] = fake2
    cb.tips.add(fake2.id)

    result = ca.merge(cb, source_id="drone_B")
    print(f"  merge() result: {result}")
    print(f"  Nodes in A after merge: {ca.size()}  (tampered node included: {'TAMPERED0000' in [n.hash for n in ca.nodes.values()]})")
    print(f"  ca.validate_full_dag() = {ca.validate_full_dag()}  <- never went invalid, rejected at the door")
    print(f"  drone_B reputation at A: {ca.reputation.get('drone_B')}")

    print("\n=== Repeated offenses -> quarantine ===")
    for i in range(3):
        bad = DAGNode(index=100 + i, event="BAD", parent_ids=list(cb.tips)[:1])
        bad.hash = "TAMPERED"
        cb.nodes[bad.id] = bad
        cb.tips.add(bad.id)
        ca.merge(cb, source_id="drone_B")
    print(f"  drone_B quarantined at A? {'drone_B' in ca.quarantined}")
    print(f"  total rejected at A: {ca.rejected_count}")