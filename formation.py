

from ursina import Vec3
import math
from config import DRONE_SPEED


def get_formation_offsets(shape, count):
    """
    Formation ke local offsets return karta hai (anchor point ke relative,
    jaise anchor origin (0,0) pe ho aur formation aage (+z) ki taraf face kare).
    In offsets ko baad mein anchor ki current position aur heading ke
    hisaab se rotate + translate kiya jaata hai.
    """
    offsets = []

    if shape == 'grid':
        cols = math.ceil(math.sqrt(count))
        spacing = 2.5
        for i in range(count):
            row = i // cols
            col = i % cols
            x = (col - cols / 2) * spacing
            z = (row - cols / 2) * spacing
            offsets.append((x, z))

    elif shape == 'circle':
        radius = 6
        for i in range(count):
            angle = (2 * math.pi / count) * i
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            offsets.append((x, z))

    elif shape == 'v':
        offsets.append((0, 2))  # leader — sabse aage tip pe
        remaining = count - 1
        spacing = 2.0
        for i in range(remaining):
            side = 1 if i % 2 == 0 else -1
            depth = (i // 2 + 1)
            x = side * depth * spacing * 0.7
            z = -depth * spacing * 0.6
            offsets.append((x, z))





    
            

    elif shape == 'expanding_square':
        spacing = 2.0
        offsets.append((0, 0))
        for i in range(1, count):
            side = i % 4
            dist = (i // 4 + 1) * spacing
            if side == 0:
                offsets.append((dist, 0))
            elif side == 1:
                offsets.append((dist, dist))
            elif side == 2:
                offsets.append((-dist, dist))
            else:
                offsets.append((-dist, -dist))

 

        

    

    return offsets


def rotate_offset(offset, heading_rad):
    """Ek local (x, z) offset ko anchor ki current heading direction ke
    hisaab se rotate karta hai — isliye formation hamesha 'aage ki taraf'
    face karta hai, chahe anchor kisi bhi direction mein move kar raha ho."""
    ox, oz = offset
    cos_h = math.cos(heading_rad)
    sin_h = math.sin(heading_rad)
    rx = ox * cos_h - oz * sin_h
    rz = ox * sin_h + oz * cos_h
    return rx, rz





def move_toward_formation(drone, target_position, dt):
    """
    Drone ko target position ki taraf directly, smoothly move karta hai —
    overshoot nahi hoga kyunki move_amount hamesha distance se clamp hota hai.
    """
    from config import FORMATION_SPEED

    diff = target_position - drone.position
    dist = diff.length()

    if dist > 0.05:
        direction = diff.normalized()
        move_amount = min(dist, FORMATION_SPEED * dt)
        drone.position += direction * move_amount
        drone.velocity = direction * FORMATION_SPEED  # orientation ke liye

        if drone.velocity.length() > 0.01:
            drone.look_at(drone.position + drone.velocity)
    else:
        drone.velocity = Vec3(0, 0, 0)


