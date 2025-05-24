from sympy import mod_inverse, gcd, lcm
def find_time_to_collision(x1, v_x1, x2, v_x2, y1, v_y1, y2, v_y2, map_size):
    delta_pos_x = (x2-x1) % map_size
    delta_pos_y = (y2-y1) % map_size

    delta_vel_x = (v_x1-v_x2) % map_size
    delta_vel_y = (v_y1-v_y2) % map_size

    if delta_vel_x == 0 and delta_vel_y == 0:
        return None
        
    g1 = gcd(delta_vel_x, map_size)
    g2 = gcd(delta_vel_y, map_size)
 
    # Solve for t using modular inverse
    delta_vel_x //= g1
    delta_vel_y //= g2
    delta_pos_x //= g1
    delta_pos_y //= g2
    size1 = map_size
    size2 = map_size
    size1 //= g1 
    size2 //= g2 
    
    t1 = (mod_inverse(delta_vel_x, size1) * delta_pos_x) % size1
    t2 = (mod_inverse(delta_vel_y, size2) * delta_pos_y) % size2
    delta_t = abs(t2-t1)
    return delta_t, t1

print(find_time_to_collision(2, -2, 10, 3, 4, -1, 2, 1, 12))