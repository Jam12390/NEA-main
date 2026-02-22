import math

def s(u, g, t) -> float:
    return u*t + 0.5*g*t**2

def v(u, g, t) -> float:
    return u + g*t

def solveV(targetV, u, g) -> float:
    return (targetV-u)/g

def solveS(u, g, point, direction) -> float:
    #equ = 0 = ut + 0.5at^2 - point
    solutions = [
        (-u + math.sqrt(max(0, u**2 - 2*g*-point)))/(2*g),
        (-u - math.sqrt(max(0, u**2 - 2*g*-point)))/(2*g)
    ] #solutions to point

    if direction == "l":
        t = min(solutions)
    else:
        t = max(solutions)
    return t