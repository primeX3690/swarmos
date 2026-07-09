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



def validate_chain(chain):
    """Poori chain ki hash-integrity verify karta hai — agar koi block
    tamper hua hai (hash match nahi karta), chain invalid hai."""
    for i in range(1, len(chain)):
        block = chain[i]
        prev = chain[i - 1]
        if block['prev_hash'] != prev['hash']:
            return False
        if hash_block(block) != block['hash']:
            return False
    return True


def hacker_inject_fake_command(drone):
    """
    Simulated hacker attack — ek corrupted/unauthorized block force-inject
    karta hai jiska hash intentionally mismatch karega, taaki mesh isse
    consensus se pakad sake.
    """
    last = drone.ledger[-1]
    fake_block = {
        'index': last['index'] + 1,
        'timestamp': 0,
        'event': 'UNAUTHORIZED_CMD',
        'prev_hash': last['hash'],
    }
    fake_block['hash'] = 'TAMPERED0000'  # jaan-bujh ke galat hash — real cheez detect karegi
    drone.ledger.append(fake_block)        