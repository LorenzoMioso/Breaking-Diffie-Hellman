import math

from const_mod_mult4 import (
    const_mod_mult4,
    controlled_copy4,
    double_controlled_exp_prep,
    double_controlled_exp_prep_inv,
)
from mod_subtr4 import mod_subtr4
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from subtr4 import twos_complement_to_signed_int
from utils import run_circuit


def const_mod_mult4_inv(C, X, A, B, CARRY, N, T, n, a):
    """
    CMODMULT4 circuit
    CMODMULT4(n)|c,x,0,0> = {
        |c,x,0,x/a mod n> if c=1,
        |c,x,0,0>         if c=0

    Inputs:
    - C: 1-bit input register, control
    - X: 4-bit input register, the first operand
    - A: 4-bit input register, support register for the division
    - B: 4-bit input register, support register for the division
    - C: 5-bit input register, carry for the addition
    - N: 4-bit input register, modulus
    - T: 1-bit input register, temporary qubit for the modular addition
    - n: number base 10, 1 <= n <= 15, is the modulus
    - a: number base 10, 0 <= a <= 7, is the divisor, max a = 2^(nbit-1)-1 = 7
    """
    qc = QuantumCircuit(C, X, A, B, CARRY, N, T, name=f"inv_mod_mult4_{a}x_mod_{n}")

    qc.append(controlled_copy4(C, X, B), C[:] + X[:] + B[:])

    for i, qx in enumerate(X):
        qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
        qc.append(
            mod_subtr4(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:]
        )
        qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

    return qc


def test():
    # Create the circuit
    C = QuantumRegister(1, "control")
    X = QuantumRegister(4, "x")
    A = QuantumRegister(4, "a")
    B = QuantumRegister(4, "b")
    CARRY = QuantumRegister(5, "carry")
    N = QuantumRegister(4, "n")
    T = QuantumRegister(1, "t")
    RESX = ClassicalRegister(4, "res_x")
    RESA = ClassicalRegister(4, "res_a")
    RESB = ClassicalRegister(5, "res_b")
    RESCAR = ClassicalRegister(4, "res_car")
    RESN = ClassicalRegister(4, "res_n")
    REST = ClassicalRegister(1, "res_t")

    # a = 7
    # x = 7
    # b = 1
    # n = 15
    a = 7
    x = 0
    b = 0
    n = 15
    apply_function = True

    qc = QuantumCircuit(C, X, A, B, CARRY, N, T, RESX, RESA, RESB, RESCAR, RESN, REST)
    # set C to 1
    if apply_function:
        qc.x(C)
    for i in range(4):
        if x & (1 << i):
            qc.x(X[i])
        if n & (1 << i):
            qc.x(N[i])
        if b & (1 << i):
            qc.x(B[i])

    # qc.append(
    #    const_mod_mult4(C, X, A, B, CARRY, N, T, n, a),
    #    C[:] + X[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
    # )
    qc.append(
        const_mod_mult4_inv(C, X, A, B, CARRY, N, T, n, a),
        C[:] + X[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
    )

    # print(qc.decompose().draw())
    print(qc.decompose().decompose().draw())
    qc.measure(X, RESX)
    qc.measure(A, RESA)
    qc.measure(B[0], RESB[0])
    qc.measure(B[1], RESB[1])
    qc.measure(B[2], RESB[2])
    qc.measure(B[3], RESB[3])
    qc.measure(CARRY[4], RESB[4])
    qc.measure(CARRY[0], RESCAR[0])
    qc.measure(CARRY[1], RESCAR[1])
    qc.measure(CARRY[2], RESCAR[2])
    qc.measure(CARRY[3], RESCAR[3])
    qc.measure(N, RESN)
    qc.measure(T, REST)
    res = run_circuit(qc)

    res_t = int(res[0], 2)
    res_n = int(res[1:5], 2)
    res_car = int(res[5:9], 2)
    res_b = int(res[9:14], 2)
    res_a = int(res[14:18], 2)
    res_x = int(res[18:], 2)

    print(f"t = {res_t}, ({res[0]})")
    print(f"n = {res_n}, ({res[1:5]})")
    print(f"car = {res_car}, ({res[5:9]})")
    print(f"b = {res_b}, ({res[9:14]})")
    print(f"a = {res_a}, ({res[14:18]})")
    print(f"x = {res_x}, ({res[18:]})")

    if apply_function:
        # the result should 0 because the function and its inverse should cancel each other
        print(f"a : {a}, x : {x}, n : {n}, b_res : {res_b} ({res[9:14]})")


def test_all():
    # Create the circuit
    C = QuantumRegister(1, "control")
    X = QuantumRegister(4, "x")
    A = QuantumRegister(4, "a")
    B = QuantumRegister(4, "b")
    CARRY = QuantumRegister(5, "carry")
    N = QuantumRegister(4, "n")
    T = QuantumRegister(1, "t")
    RESX = ClassicalRegister(4, "res_x")
    RESA = ClassicalRegister(4, "res_a")
    RESB = ClassicalRegister(5, "res_b")
    RESCAR = ClassicalRegister(4, "res_car")
    RESN = ClassicalRegister(4, "res_n")
    REST = ClassicalRegister(1, "res_t")

    apply_function = True

    for a in reversed(range(2**3)):
        # test all possible inputs
        for n in reversed(range(1, 2**4)):
            # print(f"Modulus: {n} ############################")
            for x in range(1, 2**4):
                # print(f"Multiplier: {a}, Multiplicand: {x} ############################")
                if x >= n or a >= n:
                    continue

                qc = QuantumCircuit(
                    C, X, A, B, CARRY, N, T, RESX, RESA, RESB, RESCAR, RESN, REST
                )
                # set C to 1
                if apply_function:
                    qc.x(C)
                for i in range(4):
                    if x & (1 << i):
                        qc.x(X[i])
                    if n & (1 << i):
                        qc.x(N[i])

                qc.append(
                    const_mod_mult4(C, X, A, B, CARRY, N, T, n, a),
                    C[:] + X[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
                )
                qc.append(
                    const_mod_mult4_inv(C, X, A, B, CARRY, N, T, n, a),
                    C[:] + X[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
                )

                # print(qc.decompose().draw())
                # print(qc.decompose().decompose().draw())
                qc.measure(X, RESX)
                qc.measure(A, RESA)
                qc.measure(B[0], RESB[0])
                qc.measure(B[1], RESB[1])
                qc.measure(B[2], RESB[2])
                qc.measure(B[3], RESB[3])
                qc.measure(CARRY[4], RESB[4])
                qc.measure(CARRY[0], RESCAR[0])
                qc.measure(CARRY[1], RESCAR[1])
                qc.measure(CARRY[2], RESCAR[2])
                qc.measure(CARRY[3], RESCAR[3])
                qc.measure(N, RESN)
                qc.measure(T, REST)
                res = run_circuit(qc)

                res_t = int(res[0], 2)
                res_n = int(res[1:5], 2)
                res_car = int(res[5:9], 2)
                res_b = int(res[9:14], 2)
                res_a = int(res[14:18], 2)
                res_x = int(res[18:], 2)

                # print(f"t = {res_t}, ({res[0]})")
                # print(f"n = {res_n}, ({res[1:5]})")
                # print(f"car = {res_car}, ({res[5:9]})")
                # print(f"b = {res_b}, ({res[9:14]})")
                # print(f"a = {res_a}, ({res[14:18]})")
                # print(f"x = {res_x}, ({res[18:]})")

                if apply_function:
                    # the result should 0 because the function and its inverse should cancel each other
                    print(
                        f"a : {a}, x : {x}, n : {n}, b_res : {res_b} ({res[9:14]})",
                        end=" ",
                    )
                    # result should be 0
                    if res_b != 0:
                        print("ERROR")
                    else:
                        print("SUCCESS")

            # break


if __name__ == "__main__":
    # test()
    test_all()
