from sympy import mod_inverse, gcd, lcm
def find_time_to_collision(x1, v_x1, x2, v_x2, y1, v_y1, y2, v_y2, map_size):
    delta_pos_x = (x2-x1) % map_size
    delta_vel_x = (v_x1-v_x2) % map_size

    delta_pos_y = (y2-y1) % map_size
    delta_vel_y = (v_y1-v_y2) % map_size

    if delta_vel_x == 0 and delta_vel_y == 0:
        return None
        
    if delta_vel_x != 0 :
        t1 = (mod_inverse(delta_vel_x, map_size) * delta_pos_x) % map_size    
    else:
        t1 = None

    if delta_vel_y != 0 :
        t2 = (mod_inverse(delta_vel_y, map_size) * delta_pos_y) % map_size    
    else:
        t2 = None
    
    if t1 == None or t2 == None:
        return None
    delta_t = abs(t2-t1)
    return delta_t, t1, t2

def find_time_to_collision():
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)

    v_x1, v_x2 = min(v_x1, v_x2), max(v_x1, v_x2)
    v_y1, v_y2 = min(v_y1, v_y2), max(v_y1, v_y2)

    if v_x2-v_x1 == 0 or v_y2-v_y1 == 0:
        return 0
    
    # Hårdkod   
def time_to_collision(x1, x2, v1, v2, map_size):
    if v1 >= 0 and v2 <= 0:
        dist = x2-x1
        return dist/(v1-v2)
    elif v1 <= 0 and v2 >= 0:
        dist = x1 + (map_size-x2)
        return dist/(v2-v1)
    elif (v1 < 0 and v2 < 0) and abs(v1) < abs(v2):
        return (x2-x1)/(v1-v2)
    elif (v1 < 0 and v2 < 0) and abs(v1) > abs(v2):
        x1 += map_size
        return (x2-x1)/(v1-v2)
    
    elif (v1 > 0 and v2 > 0) and abs(v2) < abs(v1):
        return (x2-x1)/(v1-v2)
    elif (v1 > 0 and v2 > 0) and abs(v2) > abs(v1):
        x2 -= map_size
        return (x2-x1)/(v1-v2)

print(time_to_collision(2, 10, 2, 2, 12))