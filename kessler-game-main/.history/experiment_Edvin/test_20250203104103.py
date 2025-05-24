from sympy import mod_inverse, gcd
def find_time_to_collision(x1, v1, x2, v2, map_size):
    delta_pos = (x2-x1) % map_size
    delta_vel = (v1-v2) % map_size

    if delta_vel == 0:
        return 0 if delta_pos == 0 else None
        
    g = gcd(delta_vel, map_size)
        
    # Solve for t using modular inverse
    delta_vel //= g
    delta_pos //= g
    map_size //= g 
    t = (mod_inverse(delta_vel, map_size) * delta_pos) % map_size
    return t

print(find_time_to_collision(2, 3, 11, -1, 12))