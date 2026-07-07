import hashlib
import time as pytime


def hash_block(block):
    """Har block ka unique fingerprint — agar data tamper hua to hash match nahi karega."""
    payload = f"{block['index']}{block['timestamp']}{block['event']}{block['prev_hash']}"
    return hashlib.sha256(payload.encode()).hexdigest()[:12]


def create_genesis_block():
    """Har drone ka ledger isi pehle block se shuru hota hai."""
    block = {
        'index': 0,
        'timestamp': 0,
        'event': 'MISSION_START',
        'prev_hash': '0' * 12,
    }
    block['hash'] = hash_block(block)
    return block


def add_block(chain, event):
    """Naya mission event chain mein jodta hai — pichle block ke hash se linked."""
    prev = chain[-1]
    block = {
        'index': prev['index'] + 1,
        'timestamp': round(pytime.time(), 2),
        'event': event,
        'prev_hash': prev['hash'],
    }
    block['hash'] = hash_block(block)
    chain.append(block)
    return chain


def sync_chains(drone_a, drone_b):
    """
    Do paas-paas ke drones apna ledger replicate karte hain — jiska chain
    lamba hai (zyada updated hai), doosra usi ko copy kar leta hai.
    Isse mission data kisi ek drone tak limited nahi rehta — sab ke paas
    ek jaisi copy ban jaati hai, resilience ke liye.
    """
    if len(drone_b.ledger) > len(drone_a.ledger):
        drone_a.ledger = list(drone_b.ledger)
        drone_a.mission_data = dict(drone_b.mission_data)
    elif len(drone_a.ledger) > len(drone_b.ledger):
        drone_b.ledger = list(drone_a.ledger)
        drone_b.mission_data = dict(drone_a.mission_data)