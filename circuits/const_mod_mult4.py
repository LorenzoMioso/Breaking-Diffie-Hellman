import math

from mod_addr4 import mod_addr4
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from utils import run_circuit


def double_controlled_exp_prep(a, k):
    """
    Prepare the register REG with a controlled-controlled number a^k
    First 2 qubits are the control qubits, the last 4 are the target qubits

    Inputs:
    - a: the base of the exponentiation, 0 <= a <= 7
    - k: the exponent, 0 <= k <= 3
    - REGS: the quantum registers to prepare
    """
    # print(f"double_controlled_exp_prep({a}, {k})")

    assert 0 <= a <= 7, "a must be a number between 0 and 7"
    assert 0 <= k <= 3, "k must be a number between 0 and 3"

    result = a * (2**k)

    qc = QuantumCircuit(6, name=f"cc_{a}*{2**k}")

    if result == 0:
        return qc  # No need to do anything for a result of 0

    # if result > 15:
    #    # print(f"Result {a}*{2**k}={result} cannot be represented with 4 bits")
    #    return qc

    # Apply CCX based on the binary representation of result
    for i in range(4 * 2):  # last 4 qubits are the target qubits
        if result & (1 << i):
            qc.ccx(0, 1, 2 + (i % 4))

    return qc


def double_controlled_exp_prep_inv(a, k):
    """
    Prepare the register REG with a controlled-controlled number a^k
    First 2 qubits are the control qubits, the last 4 are the target qubits

    Inputs:
    - a: the base of the exponentiation, 0 <= a <= 7
    - k: the exponent, 0 <= k <= 3
    - REGS: the quantum registers to prepare
    """

    assert 0 <= a <= 7, "a must be a number between 0 and 7"
    assert 0 <= k <= 3, "k must be a number between 0 and 3"

    result = a * (2**k)

    qc = QuantumCircuit(6, name=f"cc_{a}*{2**k}_inv")

    if result == 0:
        return qc  # No need to do anything for a result of 0

    # if result > 15:
    #    # print(f"Result {a}*{2**k}={result} cannot be represented with 4 bits")
    #    return qc

    # Apply CCX based on the binary representation of result
    for i in reversed(range(4 * 2)):  # last 3 qubits are the target qubits
        if result & (1 << i):
            qc.ccx(0, 1, 2 + (i % 4))

    return qc


def controlled_copy4(C, A, B):
    """
    Copy the content of register A to register B if C is 0

    """

    qc = QuantumCircuit(C, A, B, name="controlled_copy4")

    qc.x(C)
    for i in range(4):
        qc.ccx(C, A[i], B[i])
    qc.x(C)

    return qc


def const_mod_mult4(C, X, A, B, CARRY, N, T, n, a):
    """
    CMODMULT4 circuit
    CMODMULT4(n)|c,x,0,0> = {
        |c,x,0,ax mod n> if c=1,
        |c,x,0,0>        if c=0

    Inputs:
    - C: 1-bit input register, control
    - X: 4-bit input register, the first operand
    - A: 4-bit input register, support register for the multiplication
    - B: 4-bit input register, support register for the multiplication
    - C: 5-bit input register, carry for the addition
    - N: 4-bit input register, modulus
    - T: 1-bit input register, temporary qubit for the modular addition
    - n: number base 10, 1 <= n <= 15, is the modulus
    - a: number base 10, 0 <= a <= 7, is the multiplier, max a = 2^(nbit-1)-1 = 7
    """
    qc = QuantumCircuit(C, X, A, B, CARRY, N, T, name=f"mod_mult4_{a}x_mod_{n}")

    for i, qx in enumerate(X):
        # print(f"i = {i}, qx = {qx}")
        # print(f"double_controlled_exp_prep({a}, {i})")
        qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
        qc.append(mod_addr4(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:])
        qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

    # expand the for loop
    # i = 0
    # qx = X[i]
    # qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
    # qc.append(mod_addr4(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:])
    # qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

    # i = 1
    # qx = X[i]
    # qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
    # qc.append(mod_addr4(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:])
    # qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

    # i = 2
    # qx = X[i]
    # qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
    # qc.append(mod_addr4(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:])
    # qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

    # i = 3
    # qx = X[i]
    # qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
    # qc.append(mod_addr4(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:])
    # qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

    qc.append(controlled_copy4(C, X, B), C[:] + X[:] + B[:])

    return qc


def main():
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
    RESC = ClassicalRegister(4, "res_c")
    RESN = ClassicalRegister(4, "res_n")
    REST = ClassicalRegister(1, "res_t")

    apply_multiplier = True

    for n in reversed(range(2**4)):
        # test all possible inputs
        for a in reversed(range(2**3)):
            # print(f"Modulus: {n} ############################")
            for x in range(2**4):
                # print(f"Multiplier: {a}, Multiplicand: {x} ############################")
                if x >= n or a >= n:
                    # if x >= n or a >= n or a * x >= n:
                    # if x >= n or a >= n or ((a * int(2 ** math.log2(x))) > 15):
                    #    print(
                    #        f"Skipping {a} * {x} % {n}, {x} >= {n} : {x >= n}, {a} >= {n} : {a >= n}, {a} * {x} >= {n} : {a * x >= n}"
                    #    )
                    continue
                qc = QuantumCircuit(
                    C, X, A, B, CARRY, N, T, RESX, RESA, RESB, RESC, RESN, REST
                )
                # set C to 1
                if apply_multiplier:
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

                # print(qc.decompose().draw())
                # print(qc.decompose().decompose().draw())

                qc.measure(X, RESX)
                qc.measure(A, RESA)
                qc.measure(B[0], RESB[0])
                qc.measure(B[1], RESB[1])
                qc.measure(B[2], RESB[2])
                qc.measure(B[3], RESB[3])
                qc.measure(CARRY[4], RESB[4])
                qc.measure(CARRY[0], RESC[0])
                qc.measure(CARRY[1], RESC[1])
                qc.measure(CARRY[2], RESC[2])
                qc.measure(CARRY[3], RESC[3])
                qc.measure(N, RESN)
                qc.measure(T, REST)
                res = run_circuit(qc)

                res_t = int(res[0], 2)
                res_n = int(res[1:5], 2)
                res_c = int(res[5:9], 2)
                res_b = int(res[9:14], 2)
                res_a = int(res[14:18], 2)
                res_x = int(res[18:], 2)

                # print(f"t = {res_t}, ({res[0]})")
                # print(f"n = {res_n}, ({res[1:5]})")
                # print(f"c = {res_c}, ({res[5:9]})")
                # print(f"b = {res_b}, ({res[9:14]})")
                # print(f"a = {res_a}, ({res[14:18]})")
                # print(f"x = {res_x}, ({res[18:]})")

                if apply_multiplier:
                    print(f"{a} * {x} % {n} = {res_b}", end=" ")
                    if res_b != (a * x) % n:
                        print("ERROR")
                    else:
                        print("SUCCESS")
                else:
                    # should copy the value of x to b
                    print(f"{x} = {res_b}")
                    if res_b != x:
                        print("ERROR")
                    else:
                        print("SUCCESS")


def test():
    # test double_controlled_exp_prep
    C = QuantumRegister(2, "control")
    A = QuantumRegister(4, "a")
    RES = ClassicalRegister(4, "res")

    for a in range(8):
        for k in range(4):
            qc = QuantumCircuit(C, A, RES)
            # toggle the control qubits
            qc.x(C)
            print(
                f"double_controlled_exp_prep({a}, {k}) : {a} * {2**k}, result = {a * (2**k)}"
            )
            qc.append(double_controlled_exp_prep(a, k), C[:] + A[:])
            print(qc.decompose().draw())
            qc.measure(A, RES)
            res = run_circuit(qc)
            print(res)
            print(int(res, 2))
            if int(res, 2) != a * (2**k):
                print("ERROR")
            else:
                print("SUCCESS")

            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
    # test()

"""
7 * 0 % 15 = 0 SUCCESS
7 * 1 % 15 = 7 SUCCESS
7 * 2 % 15 = 14 SUCCESS
7 * 3 % 15 = 6 SUCCESS
7 * 4 % 15 = 13 SUCCESS
7 * 5 % 15 = 5 SUCCESS
7 * 6 % 15 = 12 SUCCESS
7 * 7 % 15 = 4 SUCCESS
7 * 8 % 15 = 11 SUCCESS
7 * 9 % 15 = 3 SUCCESS
7 * 10 % 15 = 10 SUCCESS
7 * 11 % 15 = 2 SUCCESS
7 * 12 % 15 = 9 SUCCESS
7 * 13 % 15 = 1 SUCCESS
7 * 14 % 15 = 8 SUCCESS
6 * 0 % 15 = 0 SUCCESS
6 * 1 % 15 = 6 SUCCESS
6 * 2 % 15 = 12 SUCCESS
6 * 3 % 15 = 3 SUCCESS
6 * 4 % 15 = 9 SUCCESS
6 * 5 % 15 = 0 SUCCESS
6 * 6 % 15 = 6 SUCCESS
6 * 7 % 15 = 12 SUCCESS
6 * 8 % 15 = 3 SUCCESS
6 * 9 % 15 = 9 SUCCESS
6 * 10 % 15 = 0 SUCCESS
6 * 11 % 15 = 6 SUCCESS
6 * 12 % 15 = 12 SUCCESS
6 * 13 % 15 = 3 SUCCESS
6 * 14 % 15 = 9 SUCCESS
5 * 0 % 15 = 0 SUCCESS
5 * 1 % 15 = 5 SUCCESS
5 * 2 % 15 = 10 SUCCESS
5 * 3 % 15 = 0 SUCCESS
5 * 4 % 15 = 5 SUCCESS
5 * 5 % 15 = 10 SUCCESS
5 * 6 % 15 = 0 SUCCESS
5 * 7 % 15 = 5 SUCCESS
5 * 8 % 15 = 10 SUCCESS
5 * 9 % 15 = 0 SUCCESS
5 * 10 % 15 = 5 SUCCESS
5 * 11 % 15 = 10 SUCCESS
5 * 12 % 15 = 0 SUCCESS
5 * 13 % 15 = 5 SUCCESS
5 * 14 % 15 = 10 SUCCESS
4 * 0 % 15 = 0 SUCCESS
4 * 1 % 15 = 4 SUCCESS
4 * 2 % 15 = 8 SUCCESS
4 * 3 % 15 = 12 SUCCESS
4 * 4 % 15 = 1 SUCCESS
4 * 5 % 15 = 5 SUCCESS
4 * 6 % 15 = 9 SUCCESS
4 * 7 % 15 = 13 SUCCESS
4 * 8 % 15 = 2 SUCCESS
4 * 9 % 15 = 6 SUCCESS
4 * 10 % 15 = 10 SUCCESS
4 * 11 % 15 = 14 SUCCESS
4 * 12 % 15 = 3 SUCCESS
4 * 13 % 15 = 7 SUCCESS
4 * 14 % 15 = 11 SUCCESS
3 * 0 % 15 = 0 SUCCESS
3 * 1 % 15 = 3 SUCCESS
3 * 2 % 15 = 6 SUCCESS
3 * 3 % 15 = 9 SUCCESS
3 * 4 % 15 = 12 SUCCESS
3 * 5 % 15 = 0 SUCCESS
3 * 6 % 15 = 3 SUCCESS
3 * 7 % 15 = 6 SUCCESS
3 * 8 % 15 = 9 SUCCESS
3 * 9 % 15 = 12 SUCCESS
3 * 10 % 15 = 0 SUCCESS
3 * 11 % 15 = 3 SUCCESS
3 * 12 % 15 = 6 SUCCESS
3 * 13 % 15 = 9 SUCCESS
3 * 14 % 15 = 12 SUCCESS
2 * 0 % 15 = 0 SUCCESS
2 * 1 % 15 = 2 SUCCESS
2 * 2 % 15 = 4 SUCCESS
2 * 3 % 15 = 6 SUCCESS
2 * 4 % 15 = 8 SUCCESS
2 * 5 % 15 = 10 SUCCESS
2 * 6 % 15 = 12 SUCCESS
2 * 7 % 15 = 14 SUCCESS
2 * 8 % 15 = 1 SUCCESS
2 * 9 % 15 = 3 SUCCESS
2 * 10 % 15 = 5 SUCCESS
2 * 11 % 15 = 7 SUCCESS
2 * 12 % 15 = 9 SUCCESS
2 * 13 % 15 = 11 SUCCESS
2 * 14 % 15 = 13 SUCCESS
1 * 0 % 15 = 0 SUCCESS
1 * 1 % 15 = 1 SUCCESS
1 * 2 % 15 = 2 SUCCESS
1 * 3 % 15 = 3 SUCCESS
1 * 4 % 15 = 4 SUCCESS
1 * 5 % 15 = 5 SUCCESS
1 * 6 % 15 = 6 SUCCESS
1 * 7 % 15 = 7 SUCCESS
1 * 8 % 15 = 8 SUCCESS
1 * 9 % 15 = 9 SUCCESS
1 * 10 % 15 = 10 SUCCESS
1 * 11 % 15 = 11 SUCCESS
1 * 12 % 15 = 12 SUCCESS
1 * 13 % 15 = 13 SUCCESS
1 * 14 % 15 = 14 SUCCESS
0 * 0 % 15 = 0 SUCCESS
0 * 1 % 15 = 0 SUCCESS
0 * 2 % 15 = 0 SUCCESS
0 * 3 % 15 = 0 SUCCESS
0 * 4 % 15 = 0 SUCCESS
0 * 5 % 15 = 0 SUCCESS
0 * 6 % 15 = 0 SUCCESS
0 * 7 % 15 = 0 SUCCESS
0 * 8 % 15 = 0 SUCCESS
0 * 9 % 15 = 0 SUCCESS
0 * 10 % 15 = 0 SUCCESS
0 * 11 % 15 = 0 SUCCESS
0 * 12 % 15 = 0 SUCCESS
0 * 13 % 15 = 0 SUCCESS
0 * 14 % 15 = 0 SUCCESS
7 * 0 % 14 = 0 SUCCESS
7 * 1 % 14 = 7 SUCCESS
7 * 2 % 14 = 0 SUCCESS
7 * 3 % 14 = 7 SUCCESS
7 * 4 % 14 = 13 ERROR
7 * 5 % 14 = 6 ERROR
7 * 6 % 14 = 13 ERROR
7 * 7 % 14 = 6 ERROR
7 * 8 % 14 = 11 ERROR
7 * 9 % 14 = 4 ERROR
7 * 10 % 14 = 11 ERROR
7 * 11 % 14 = 4 ERROR
7 * 12 % 14 = 10 ERROR
7 * 13 % 14 = 3 ERROR
6 * 0 % 14 = 0 SUCCESS
6 * 1 % 14 = 6 SUCCESS
6 * 2 % 14 = 12 SUCCESS
6 * 3 % 14 = 4 SUCCESS
6 * 4 % 14 = 9 ERROR
6 * 5 % 14 = 1 ERROR
6 * 6 % 14 = 7 ERROR
6 * 7 % 14 = 13 ERROR
6 * 8 % 14 = 3 ERROR
6 * 9 % 14 = 9 ERROR
6 * 10 % 14 = 1 ERROR
6 * 11 % 14 = 7 ERROR
6 * 12 % 14 = 12 ERROR
6 * 13 % 14 = 4 ERROR
5 * 0 % 14 = 0 SUCCESS
5 * 1 % 14 = 5 SUCCESS
5 * 2 % 14 = 10 SUCCESS
5 * 3 % 14 = 1 SUCCESS
5 * 4 % 14 = 5 ERROR
5 * 5 % 14 = 10 ERROR
5 * 6 % 14 = 1 ERROR
5 * 7 % 14 = 6 ERROR
5 * 8 % 14 = 10 ERROR
5 * 9 % 14 = 1 ERROR
5 * 10 % 14 = 6 ERROR
5 * 11 % 14 = 11 ERROR
5 * 12 % 14 = 1 ERROR
5 * 13 % 14 = 6 ERROR
4 * 0 % 14 = 0 SUCCESS
4 * 1 % 14 = 4 SUCCESS
4 * 2 % 14 = 8 SUCCESS
4 * 3 % 14 = 12 SUCCESS
4 * 4 % 14 = 1 ERROR
4 * 5 % 14 = 5 ERROR
4 * 6 % 14 = 9 ERROR
4 * 7 % 14 = 13 ERROR
4 * 8 % 14 = 2 ERROR
4 * 9 % 14 = 6 ERROR
4 * 10 % 14 = 10 ERROR
4 * 11 % 14 = 0 ERROR
4 * 12 % 14 = 3 ERROR
4 * 13 % 14 = 7 ERROR
3 * 0 % 14 = 0 SUCCESS
3 * 1 % 14 = 3 SUCCESS
3 * 2 % 14 = 6 SUCCESS
3 * 3 % 14 = 9 SUCCESS
3 * 4 % 14 = 12 SUCCESS
3 * 5 % 14 = 1 SUCCESS
3 * 6 % 14 = 4 SUCCESS
3 * 7 % 14 = 7 SUCCESS
3 * 8 % 14 = 9 ERROR
3 * 9 % 14 = 12 ERROR
3 * 10 % 14 = 1 ERROR
3 * 11 % 14 = 4 ERROR
3 * 12 % 14 = 7 ERROR
3 * 13 % 14 = 10 ERROR
2 * 0 % 14 = 0 SUCCESS
2 * 1 % 14 = 2 SUCCESS
2 * 2 % 14 = 4 SUCCESS
2 * 3 % 14 = 6 SUCCESS
2 * 4 % 14 = 8 SUCCESS
2 * 5 % 14 = 10 SUCCESS
2 * 6 % 14 = 12 SUCCESS
2 * 7 % 14 = 0 SUCCESS
2 * 8 % 14 = 1 ERROR
2 * 9 % 14 = 3 ERROR
2 * 10 % 14 = 5 ERROR
2 * 11 % 14 = 7 ERROR
2 * 12 % 14 = 9 ERROR
2 * 13 % 14 = 11 ERROR
1 * 0 % 14 = 0 SUCCESS
1 * 1 % 14 = 1 SUCCESS
1 * 2 % 14 = 2 SUCCESS
1 * 3 % 14 = 3 SUCCESS
1 * 4 % 14 = 4 SUCCESS
1 * 5 % 14 = 5 SUCCESS
1 * 6 % 14 = 6 SUCCESS
1 * 7 % 14 = 7 SUCCESS
1 * 8 % 14 = 8 SUCCESS
1 * 9 % 14 = 9 SUCCESS
1 * 10 % 14 = 10 SUCCESS
1 * 11 % 14 = 11 SUCCESS
1 * 12 % 14 = 12 SUCCESS
1 * 13 % 14 = 13 SUCCESS
0 * 0 % 14 = 0 SUCCESS
0 * 1 % 14 = 0 SUCCESS
0 * 2 % 14 = 0 SUCCESS
0 * 3 % 14 = 0 SUCCESS
0 * 4 % 14 = 0 SUCCESS
0 * 5 % 14 = 0 SUCCESS
0 * 6 % 14 = 0 SUCCESS
0 * 7 % 14 = 0 SUCCESS
0 * 8 % 14 = 0 SUCCESS
0 * 9 % 14 = 0 SUCCESS
0 * 10 % 14 = 0 SUCCESS
0 * 11 % 14 = 0 SUCCESS
0 * 12 % 14 = 0 SUCCESS
0 * 13 % 14 = 0 SUCCESS
7 * 0 % 13 = 0 SUCCESS
7 * 1 % 13 = 7 SUCCESS
7 * 2 % 13 = 1 SUCCESS
7 * 3 % 13 = 8 SUCCESS
7 * 4 % 13 = 0 ERROR
7 * 5 % 13 = 7 ERROR
7 * 6 % 13 = 1 ERROR
7 * 7 % 13 = 8 ERROR
7 * 8 % 13 = 11 ERROR
7 * 9 % 13 = 5 ERROR
7 * 10 % 13 = 12 ERROR
7 * 11 % 13 = 6 ERROR
7 * 12 % 13 = 11 ERROR
6 * 0 % 13 = 0 SUCCESS
6 * 1 % 13 = 6 SUCCESS
6 * 2 % 13 = 12 SUCCESS
6 * 3 % 13 = 5 SUCCESS
6 * 4 % 13 = 9 ERROR
6 * 5 % 13 = 2 ERROR
6 * 6 % 13 = 8 ERROR
6 * 7 % 13 = 1 ERROR
6 * 8 % 13 = 3 ERROR
6 * 9 % 13 = 9 ERROR
6 * 10 % 13 = 2 ERROR
6 * 11 % 13 = 8 ERROR
6 * 12 % 13 = 12 ERROR
5 * 0 % 13 = 0 SUCCESS
5 * 1 % 13 = 5 SUCCESS
5 * 2 % 13 = 10 SUCCESS
5 * 3 % 13 = 2 SUCCESS
5 * 4 % 13 = 5 ERROR
5 * 5 % 13 = 10 ERROR
5 * 6 % 13 = 2 ERROR
5 * 7 % 13 = 7 ERROR
5 * 8 % 13 = 10 ERROR
5 * 9 % 13 = 2 ERROR
5 * 10 % 13 = 7 ERROR
5 * 11 % 13 = 12 ERROR
5 * 12 % 13 = 2 ERROR
4 * 0 % 13 = 0 SUCCESS
4 * 1 % 13 = 4 SUCCESS
4 * 2 % 13 = 8 SUCCESS
4 * 3 % 13 = 12 SUCCESS
4 * 4 % 13 = 1 ERROR
4 * 5 % 13 = 5 ERROR
4 * 6 % 13 = 9 ERROR
4 * 7 % 13 = 0 ERROR
4 * 8 % 13 = 2 ERROR
4 * 9 % 13 = 6 ERROR
4 * 10 % 13 = 10 ERROR
4 * 11 % 13 = 1 ERROR
4 * 12 % 13 = 3 ERROR
3 * 0 % 13 = 0 SUCCESS
3 * 1 % 13 = 3 SUCCESS
3 * 2 % 13 = 6 SUCCESS
3 * 3 % 13 = 9 SUCCESS
3 * 4 % 13 = 12 SUCCESS
3 * 5 % 13 = 2 SUCCESS
3 * 6 % 13 = 5 SUCCESS
3 * 7 % 13 = 8 SUCCESS
3 * 8 % 13 = 9 ERROR
3 * 9 % 13 = 12 ERROR
3 * 10 % 13 = 2 ERROR
3 * 11 % 13 = 5 ERROR
3 * 12 % 13 = 8 ERROR
2 * 0 % 13 = 0 SUCCESS
2 * 1 % 13 = 2 SUCCESS
2 * 2 % 13 = 4 SUCCESS
2 * 3 % 13 = 6 SUCCESS
2 * 4 % 13 = 8 SUCCESS
2 * 5 % 13 = 10 SUCCESS
2 * 6 % 13 = 12 SUCCESS
2 * 7 % 13 = 1 SUCCESS
2 * 8 % 13 = 1 ERROR
2 * 9 % 13 = 3 ERROR
2 * 10 % 13 = 5 ERROR
2 * 11 % 13 = 7 ERROR
2 * 12 % 13 = 9 ERROR
1 * 0 % 13 = 0 SUCCESS
1 * 1 % 13 = 1 SUCCESS
1 * 2 % 13 = 2 SUCCESS
1 * 3 % 13 = 3 SUCCESS
1 * 4 % 13 = 4 SUCCESS
1 * 5 % 13 = 5 SUCCESS
1 * 6 % 13 = 6 SUCCESS
1 * 7 % 13 = 7 SUCCESS
1 * 8 % 13 = 8 SUCCESS
1 * 9 % 13 = 9 SUCCESS
1 * 10 % 13 = 10 SUCCESS
1 * 11 % 13 = 11 SUCCESS
1 * 12 % 13 = 12 SUCCESS
0 * 0 % 13 = 0 SUCCESS
0 * 1 % 13 = 0 SUCCESS
0 * 2 % 13 = 0 SUCCESS
0 * 3 % 13 = 0 SUCCESS
0 * 4 % 13 = 0 SUCCESS
0 * 5 % 13 = 0 SUCCESS
0 * 6 % 13 = 0 SUCCESS
0 * 7 % 13 = 0 SUCCESS
0 * 8 % 13 = 0 SUCCESS
0 * 9 % 13 = 0 SUCCESS
0 * 10 % 13 = 0 SUCCESS
0 * 11 % 13 = 0 SUCCESS
0 * 12 % 13 = 0 SUCCESS
7 * 0 % 12 = 0 SUCCESS
7 * 1 % 12 = 7 SUCCESS
7 * 2 % 12 = 2 SUCCESS
7 * 3 % 12 = 9 SUCCESS
7 * 4 % 12 = 1 ERROR
7 * 5 % 12 = 8 ERROR
7 * 6 % 12 = 3 ERROR
7 * 7 % 12 = 10 ERROR
7 * 8 % 12 = 11 ERROR
7 * 9 % 12 = 6 ERROR
7 * 10 % 12 = 1 ERROR
7 * 11 % 12 = 8 ERROR
6 * 0 % 12 = 0 SUCCESS
6 * 1 % 12 = 6 SUCCESS
6 * 2 % 12 = 0 SUCCESS
6 * 3 % 12 = 6 SUCCESS
6 * 4 % 12 = 9 ERROR
6 * 5 % 12 = 3 ERROR
6 * 6 % 12 = 9 ERROR
6 * 7 % 12 = 3 ERROR
6 * 8 % 12 = 3 ERROR
6 * 9 % 12 = 9 ERROR
6 * 10 % 12 = 3 ERROR
6 * 11 % 12 = 9 ERROR
5 * 0 % 12 = 0 SUCCESS
5 * 1 % 12 = 5 SUCCESS
5 * 2 % 12 = 10 SUCCESS
5 * 3 % 12 = 3 SUCCESS
5 * 4 % 12 = 5 ERROR
5 * 5 % 12 = 10 ERROR
5 * 6 % 12 = 3 ERROR
5 * 7 % 12 = 8 ERROR
5 * 8 % 12 = 10 ERROR
5 * 9 % 12 = 3 ERROR
5 * 10 % 12 = 8 ERROR
5 * 11 % 12 = 1 ERROR
4 * 0 % 12 = 0 SUCCESS
4 * 1 % 12 = 4 SUCCESS
4 * 2 % 12 = 8 SUCCESS
4 * 3 % 12 = 0 SUCCESS
4 * 4 % 12 = 1 ERROR
4 * 5 % 12 = 5 ERROR
4 * 6 % 12 = 9 ERROR
4 * 7 % 12 = 1 ERROR
4 * 8 % 12 = 2 ERROR
4 * 9 % 12 = 6 ERROR
4 * 10 % 12 = 10 ERROR
4 * 11 % 12 = 2 ERROR
3 * 0 % 12 = 0 SUCCESS
3 * 1 % 12 = 3 SUCCESS
3 * 2 % 12 = 6 SUCCESS
3 * 3 % 12 = 9 SUCCESS
3 * 4 % 12 = 0 SUCCESS
3 * 5 % 12 = 3 SUCCESS
3 * 6 % 12 = 6 SUCCESS
3 * 7 % 12 = 9 SUCCESS
3 * 8 % 12 = 9 ERROR
3 * 9 % 12 = 0 ERROR
3 * 10 % 12 = 3 ERROR
3 * 11 % 12 = 6 ERROR
2 * 0 % 12 = 0 SUCCESS
2 * 1 % 12 = 2 SUCCESS
2 * 2 % 12 = 4 SUCCESS
2 * 3 % 12 = 6 SUCCESS
2 * 4 % 12 = 8 SUCCESS
2 * 5 % 12 = 10 SUCCESS
2 * 6 % 12 = 0 SUCCESS
2 * 7 % 12 = 2 SUCCESS
2 * 8 % 12 = 1 ERROR
2 * 9 % 12 = 3 ERROR
2 * 10 % 12 = 5 ERROR
2 * 11 % 12 = 7 ERROR
1 * 0 % 12 = 0 SUCCESS
1 * 1 % 12 = 1 SUCCESS
1 * 2 % 12 = 2 SUCCESS
1 * 3 % 12 = 3 SUCCESS
1 * 4 % 12 = 4 SUCCESS
1 * 5 % 12 = 5 SUCCESS
1 * 6 % 12 = 6 SUCCESS
1 * 7 % 12 = 7 SUCCESS
1 * 8 % 12 = 8 SUCCESS
1 * 9 % 12 = 9 SUCCESS
1 * 10 % 12 = 10 SUCCESS
1 * 11 % 12 = 11 SUCCESS
0 * 0 % 12 = 0 SUCCESS
0 * 1 % 12 = 0 SUCCESS
0 * 2 % 12 = 0 SUCCESS
0 * 3 % 12 = 0 SUCCESS
0 * 4 % 12 = 0 SUCCESS
0 * 5 % 12 = 0 SUCCESS
0 * 6 % 12 = 0 SUCCESS
0 * 7 % 12 = 0 SUCCESS
0 * 8 % 12 = 0 SUCCESS
0 * 9 % 12 = 0 SUCCESS
0 * 10 % 12 = 0 SUCCESS
0 * 11 % 12 = 0 SUCCESS
7 * 0 % 11 = 0 SUCCESS
7 * 1 % 11 = 7 SUCCESS
7 * 2 % 11 = 3 SUCCESS
7 * 3 % 11 = 10 SUCCESS
7 * 4 % 11 = 2 ERROR
7 * 5 % 11 = 9 ERROR
7 * 6 % 11 = 5 ERROR
7 * 7 % 11 = 1 ERROR
7 * 8 % 11 = 0 ERROR
7 * 9 % 11 = 7 ERROR
7 * 10 % 11 = 3 ERROR
6 * 0 % 11 = 0 SUCCESS
6 * 1 % 11 = 6 SUCCESS
6 * 2 % 11 = 1 SUCCESS
6 * 3 % 11 = 7 SUCCESS
6 * 4 % 11 = 9 ERROR
6 * 5 % 11 = 4 ERROR
6 * 6 % 11 = 10 ERROR
6 * 7 % 11 = 5 ERROR
6 * 8 % 11 = 3 ERROR
6 * 9 % 11 = 9 ERROR
6 * 10 % 11 = 4 ERROR
5 * 0 % 11 = 0 SUCCESS
5 * 1 % 11 = 5 SUCCESS
5 * 2 % 11 = 10 SUCCESS
5 * 3 % 11 = 4 SUCCESS
5 * 4 % 11 = 5 ERROR
5 * 5 % 11 = 10 ERROR
5 * 6 % 11 = 4 ERROR
5 * 7 % 11 = 9 ERROR
5 * 8 % 11 = 10 ERROR
5 * 9 % 11 = 4 ERROR
5 * 10 % 11 = 9 ERROR
4 * 0 % 11 = 0 SUCCESS
4 * 1 % 11 = 4 SUCCESS
4 * 2 % 11 = 8 SUCCESS
4 * 3 % 11 = 1 SUCCESS
4 * 4 % 11 = 1 ERROR
4 * 5 % 11 = 5 ERROR
4 * 6 % 11 = 9 ERROR
4 * 7 % 11 = 2 ERROR
4 * 8 % 11 = 2 ERROR
4 * 9 % 11 = 6 ERROR
4 * 10 % 11 = 10 ERROR
3 * 0 % 11 = 0 SUCCESS
3 * 1 % 11 = 3 SUCCESS
3 * 2 % 11 = 6 SUCCESS
3 * 3 % 11 = 9 SUCCESS
3 * 4 % 11 = 1 SUCCESS
3 * 5 % 11 = 4 SUCCESS
3 * 6 % 11 = 7 SUCCESS
3 * 7 % 11 = 10 SUCCESS
3 * 8 % 11 = 9 ERROR
3 * 9 % 11 = 1 ERROR
3 * 10 % 11 = 4 ERROR
2 * 0 % 11 = 0 SUCCESS
2 * 1 % 11 = 2 SUCCESS
2 * 2 % 11 = 4 SUCCESS
2 * 3 % 11 = 6 SUCCESS
2 * 4 % 11 = 8 SUCCESS
2 * 5 % 11 = 10 SUCCESS
2 * 6 % 11 = 1 SUCCESS
2 * 7 % 11 = 3 SUCCESS
2 * 8 % 11 = 1 ERROR
2 * 9 % 11 = 3 ERROR
2 * 10 % 11 = 5 ERROR
1 * 0 % 11 = 0 SUCCESS
1 * 1 % 11 = 1 SUCCESS
1 * 2 % 11 = 2 SUCCESS
1 * 3 % 11 = 3 SUCCESS
1 * 4 % 11 = 4 SUCCESS
1 * 5 % 11 = 5 SUCCESS
1 * 6 % 11 = 6 SUCCESS
1 * 7 % 11 = 7 SUCCESS
1 * 8 % 11 = 8 SUCCESS
1 * 9 % 11 = 9 SUCCESS
1 * 10 % 11 = 10 SUCCESS
0 * 0 % 11 = 0 SUCCESS
0 * 1 % 11 = 0 SUCCESS
0 * 2 % 11 = 0 SUCCESS
0 * 3 % 11 = 0 SUCCESS
0 * 4 % 11 = 0 SUCCESS
0 * 5 % 11 = 0 SUCCESS
0 * 6 % 11 = 0 SUCCESS
0 * 7 % 11 = 0 SUCCESS
0 * 8 % 11 = 0 SUCCESS
0 * 9 % 11 = 0 SUCCESS
0 * 10 % 11 = 0 SUCCESS
7 * 0 % 10 = 0 SUCCESS
7 * 1 % 10 = 7 SUCCESS
7 * 2 % 10 = 4 SUCCESS
7 * 3 % 10 = 23 ERROR
7 * 4 % 10 = 3 ERROR
7 * 5 % 10 = 0 ERROR
7 * 6 % 10 = 7 ERROR
7 * 7 % 10 = 14 ERROR
7 * 8 % 10 = 1 ERROR
7 * 9 % 10 = 8 ERROR
6 * 0 % 10 = 0 SUCCESS
6 * 1 % 10 = 6 SUCCESS
6 * 2 % 10 = 2 SUCCESS
6 * 3 % 10 = 8 SUCCESS
6 * 4 % 10 = 9 ERROR
6 * 5 % 10 = 5 ERROR
6 * 6 % 10 = 1 ERROR
6 * 7 % 10 = 7 ERROR
6 * 8 % 10 = 3 ERROR
6 * 9 % 10 = 9 ERROR
5 * 0 % 10 = 0 SUCCESS
5 * 1 % 10 = 5 SUCCESS
5 * 2 % 10 = 0 SUCCESS
5 * 3 % 10 = 5 SUCCESS
5 * 4 % 10 = 5 ERROR
5 * 5 % 10 = 0 ERROR
5 * 6 % 10 = 5 ERROR
5 * 7 % 10 = 0 ERROR
5 * 8 % 10 = 0 SUCCESS
5 * 9 % 10 = 5 SUCCESS
4 * 0 % 10 = 0 SUCCESS
4 * 1 % 10 = 4 SUCCESS
4 * 2 % 10 = 8 SUCCESS
4 * 3 % 10 = 2 SUCCESS
4 * 4 % 10 = 1 ERROR
4 * 5 % 10 = 5 ERROR
4 * 6 % 10 = 9 ERROR
4 * 7 % 10 = 3 ERROR
4 * 8 % 10 = 2 SUCCESS
4 * 9 % 10 = 6 SUCCESS
3 * 0 % 10 = 0 SUCCESS
3 * 1 % 10 = 3 SUCCESS
3 * 2 % 10 = 6 SUCCESS
3 * 3 % 10 = 9 SUCCESS
3 * 4 % 10 = 2 SUCCESS
3 * 5 % 10 = 5 SUCCESS
3 * 6 % 10 = 8 SUCCESS
3 * 7 % 10 = 1 SUCCESS
3 * 8 % 10 = 9 ERROR
3 * 9 % 10 = 2 ERROR
2 * 0 % 10 = 0 SUCCESS
2 * 1 % 10 = 2 SUCCESS
2 * 2 % 10 = 4 SUCCESS
2 * 3 % 10 = 6 SUCCESS
2 * 4 % 10 = 8 SUCCESS
2 * 5 % 10 = 0 SUCCESS
2 * 6 % 10 = 2 SUCCESS
2 * 7 % 10 = 4 SUCCESS
2 * 8 % 10 = 1 ERROR
2 * 9 % 10 = 3 ERROR
1 * 0 % 10 = 0 SUCCESS
1 * 1 % 10 = 1 SUCCESS
1 * 2 % 10 = 2 SUCCESS
1 * 3 % 10 = 3 SUCCESS
1 * 4 % 10 = 4 SUCCESS
1 * 5 % 10 = 5 SUCCESS
1 * 6 % 10 = 6 SUCCESS
1 * 7 % 10 = 7 SUCCESS
1 * 8 % 10 = 8 SUCCESS
1 * 9 % 10 = 9 SUCCESS
0 * 0 % 10 = 0 SUCCESS
0 * 1 % 10 = 0 SUCCESS
0 * 2 % 10 = 0 SUCCESS
0 * 3 % 10 = 0 SUCCESS
0 * 4 % 10 = 0 SUCCESS
0 * 5 % 10 = 0 SUCCESS
0 * 6 % 10 = 0 SUCCESS
0 * 7 % 10 = 0 SUCCESS
0 * 8 % 10 = 0 SUCCESS
0 * 9 % 10 = 0 SUCCESS
7 * 0 % 9 = 0 SUCCESS
7 * 1 % 9 = 7 SUCCESS
7 * 2 % 9 = 5 SUCCESS
7 * 3 % 9 = 26 ERROR
7 * 4 % 9 = 4 ERROR
7 * 5 % 9 = 2 ERROR
7 * 6 % 9 = 0 ERROR
7 * 7 % 9 = 25 ERROR
7 * 8 % 9 = 2 SUCCESS
6 * 0 % 9 = 0 SUCCESS
6 * 1 % 9 = 6 SUCCESS
6 * 2 % 9 = 3 SUCCESS
6 * 3 % 9 = 23 ERROR
6 * 4 % 9 = 0 ERROR
6 * 5 % 9 = 6 ERROR
6 * 6 % 9 = 3 ERROR
6 * 7 % 9 = 9 ERROR
6 * 8 % 9 = 3 SUCCESS
5 * 0 % 9 = 0 SUCCESS
5 * 1 % 9 = 5 SUCCESS
5 * 2 % 9 = 1 SUCCESS
5 * 3 % 9 = 6 SUCCESS
5 * 4 % 9 = 5 ERROR
5 * 5 % 9 = 1 ERROR
5 * 6 % 9 = 6 ERROR
5 * 7 % 9 = 2 ERROR
5 * 8 % 9 = 1 ERROR
4 * 0 % 9 = 0 SUCCESS
4 * 1 % 9 = 4 SUCCESS
4 * 2 % 9 = 8 SUCCESS
4 * 3 % 9 = 3 SUCCESS
4 * 4 % 9 = 1 ERROR
4 * 5 % 9 = 5 ERROR
4 * 6 % 9 = 0 ERROR
4 * 7 % 9 = 4 ERROR
4 * 8 % 9 = 2 ERROR
3 * 0 % 9 = 0 SUCCESS
3 * 1 % 9 = 3 SUCCESS
3 * 2 % 9 = 6 SUCCESS
3 * 3 % 9 = 0 SUCCESS
3 * 4 % 9 = 3 SUCCESS
3 * 5 % 9 = 6 SUCCESS
3 * 6 % 9 = 0 SUCCESS
3 * 7 % 9 = 3 SUCCESS
3 * 8 % 9 = 0 ERROR
2 * 0 % 9 = 0 SUCCESS
2 * 1 % 9 = 2 SUCCESS
2 * 2 % 9 = 4 SUCCESS
2 * 3 % 9 = 6 SUCCESS
2 * 4 % 9 = 8 SUCCESS
2 * 5 % 9 = 1 SUCCESS
2 * 6 % 9 = 3 SUCCESS
2 * 7 % 9 = 5 SUCCESS
2 * 8 % 9 = 1 ERROR
1 * 0 % 9 = 0 SUCCESS
1 * 1 % 9 = 1 SUCCESS
1 * 2 % 9 = 2 SUCCESS
1 * 3 % 9 = 3 SUCCESS
1 * 4 % 9 = 4 SUCCESS
1 * 5 % 9 = 5 SUCCESS
1 * 6 % 9 = 6 SUCCESS
1 * 7 % 9 = 7 SUCCESS
1 * 8 % 9 = 8 SUCCESS
0 * 0 % 9 = 0 SUCCESS
0 * 1 % 9 = 0 SUCCESS
0 * 2 % 9 = 0 SUCCESS
0 * 3 % 9 = 0 SUCCESS
0 * 4 % 9 = 0 SUCCESS
0 * 5 % 9 = 0 SUCCESS
0 * 6 % 9 = 0 SUCCESS
0 * 7 % 9 = 0 SUCCESS
0 * 8 % 9 = 0 SUCCESS
7 * 0 % 8 = 0 SUCCESS
7 * 1 % 8 = 7 SUCCESS
7 * 2 % 8 = 6 SUCCESS
7 * 3 % 8 = 29 ERROR
7 * 4 % 8 = 5 ERROR
7 * 5 % 8 = 4 ERROR
7 * 6 % 8 = 3 ERROR
7 * 7 % 8 = 26 ERROR
6 * 0 % 8 = 0 SUCCESS
6 * 1 % 8 = 6 SUCCESS
6 * 2 % 8 = 4 SUCCESS
6 * 3 % 8 = 26 ERROR
6 * 4 % 8 = 1 ERROR
6 * 5 % 8 = 7 ERROR
6 * 6 % 8 = 5 ERROR
6 * 7 % 8 = 11 ERROR
5 * 0 % 8 = 0 SUCCESS
5 * 1 % 8 = 5 SUCCESS
5 * 2 % 8 = 2 SUCCESS
5 * 3 % 8 = 7 SUCCESS
5 * 4 % 8 = 5 ERROR
5 * 5 % 8 = 2 ERROR
5 * 6 % 8 = 7 ERROR
5 * 7 % 8 = 4 ERROR
4 * 0 % 8 = 0 SUCCESS
4 * 1 % 8 = 4 SUCCESS
4 * 2 % 8 = 0 SUCCESS
4 * 3 % 8 = 4 SUCCESS
4 * 4 % 8 = 1 ERROR
4 * 5 % 8 = 5 ERROR
4 * 6 % 8 = 1 ERROR
4 * 7 % 8 = 5 ERROR
3 * 0 % 8 = 0 SUCCESS
3 * 1 % 8 = 3 SUCCESS
3 * 2 % 8 = 6 SUCCESS
3 * 3 % 8 = 1 SUCCESS
3 * 4 % 8 = 4 SUCCESS
3 * 5 % 8 = 7 SUCCESS
3 * 6 % 8 = 2 SUCCESS
3 * 7 % 8 = 5 SUCCESS
2 * 0 % 8 = 0 SUCCESS
2 * 1 % 8 = 2 SUCCESS
2 * 2 % 8 = 4 SUCCESS
2 * 3 % 8 = 6 SUCCESS
2 * 4 % 8 = 0 SUCCESS
2 * 5 % 8 = 2 SUCCESS
2 * 6 % 8 = 4 SUCCESS
2 * 7 % 8 = 6 SUCCESS
1 * 0 % 8 = 0 SUCCESS
1 * 1 % 8 = 1 SUCCESS
1 * 2 % 8 = 2 SUCCESS
1 * 3 % 8 = 3 SUCCESS
1 * 4 % 8 = 4 SUCCESS
1 * 5 % 8 = 5 SUCCESS
1 * 6 % 8 = 6 SUCCESS
1 * 7 % 8 = 7 SUCCESS
0 * 0 % 8 = 0 SUCCESS
0 * 1 % 8 = 0 SUCCESS
0 * 2 % 8 = 0 SUCCESS
0 * 3 % 8 = 0 SUCCESS
0 * 4 % 8 = 0 SUCCESS
0 * 5 % 8 = 0 SUCCESS
0 * 6 % 8 = 0 SUCCESS
0 * 7 % 8 = 0 SUCCESS
6 * 0 % 7 = 0 SUCCESS
6 * 1 % 7 = 6 SUCCESS
6 * 2 % 7 = 5 SUCCESS
6 * 3 % 7 = 29 ERROR
6 * 4 % 7 = 2 ERROR
6 * 5 % 7 = 1 ERROR
6 * 6 % 7 = 0 ERROR
5 * 0 % 7 = 0 SUCCESS
5 * 1 % 7 = 5 SUCCESS
5 * 2 % 7 = 3 SUCCESS
5 * 3 % 7 = 26 ERROR
5 * 4 % 7 = 5 ERROR
5 * 5 % 7 = 3 ERROR
5 * 6 % 7 = 1 ERROR
4 * 0 % 7 = 0 SUCCESS
4 * 1 % 7 = 4 SUCCESS
4 * 2 % 7 = 1 SUCCESS
4 * 3 % 7 = 5 SUCCESS
4 * 4 % 7 = 1 ERROR
4 * 5 % 7 = 5 ERROR
4 * 6 % 7 = 2 ERROR
3 * 0 % 7 = 0 SUCCESS
3 * 1 % 7 = 3 SUCCESS
3 * 2 % 7 = 6 SUCCESS
3 * 3 % 7 = 2 SUCCESS
3 * 4 % 7 = 5 SUCCESS
3 * 5 % 7 = 1 SUCCESS
3 * 6 % 7 = 4 SUCCESS
2 * 0 % 7 = 0 SUCCESS
2 * 1 % 7 = 2 SUCCESS
2 * 2 % 7 = 4 SUCCESS
2 * 3 % 7 = 6 SUCCESS
2 * 4 % 7 = 1 SUCCESS
2 * 5 % 7 = 3 SUCCESS
2 * 6 % 7 = 5 SUCCESS
1 * 0 % 7 = 0 SUCCESS
1 * 1 % 7 = 1 SUCCESS
1 * 2 % 7 = 2 SUCCESS
1 * 3 % 7 = 3 SUCCESS
1 * 4 % 7 = 4 SUCCESS
1 * 5 % 7 = 5 SUCCESS
1 * 6 % 7 = 6 SUCCESS
0 * 0 % 7 = 0 SUCCESS
0 * 1 % 7 = 0 SUCCESS
0 * 2 % 7 = 0 SUCCESS
0 * 3 % 7 = 0 SUCCESS
0 * 4 % 7 = 0 SUCCESS
0 * 5 % 7 = 0 SUCCESS
0 * 6 % 7 = 0 SUCCESS
5 * 0 % 6 = 0 SUCCESS
5 * 1 % 6 = 5 SUCCESS
5 * 2 % 6 = 4 SUCCESS
5 * 3 % 6 = 29 ERROR
5 * 4 % 6 = 5 ERROR
5 * 5 % 6 = 4 ERROR
4 * 0 % 6 = 0 SUCCESS
4 * 1 % 6 = 4 SUCCESS
4 * 2 % 6 = 2 SUCCESS
4 * 3 % 6 = 26 ERROR
4 * 4 % 6 = 1 ERROR
4 * 5 % 6 = 5 ERROR
3 * 0 % 6 = 0 SUCCESS
3 * 1 % 6 = 3 SUCCESS
3 * 2 % 6 = 0 SUCCESS
3 * 3 % 6 = 3 SUCCESS
3 * 4 % 6 = 0 SUCCESS
3 * 5 % 6 = 3 SUCCESS
2 * 0 % 6 = 0 SUCCESS
2 * 1 % 6 = 2 SUCCESS
2 * 2 % 6 = 4 SUCCESS
2 * 3 % 6 = 0 SUCCESS
2 * 4 % 6 = 2 SUCCESS
2 * 5 % 6 = 4 SUCCESS
1 * 0 % 6 = 0 SUCCESS
1 * 1 % 6 = 1 SUCCESS
1 * 2 % 6 = 2 SUCCESS
1 * 3 % 6 = 3 SUCCESS
1 * 4 % 6 = 4 SUCCESS
1 * 5 % 6 = 5 SUCCESS
0 * 0 % 6 = 0 SUCCESS
0 * 1 % 6 = 0 SUCCESS
0 * 2 % 6 = 0 SUCCESS
0 * 3 % 6 = 0 SUCCESS
0 * 4 % 6 = 0 SUCCESS
0 * 5 % 6 = 0 SUCCESS
4 * 0 % 5 = 0 SUCCESS
4 * 1 % 5 = 4 SUCCESS
4 * 2 % 5 = 3 SUCCESS
4 * 3 % 5 = 29 ERROR
4 * 4 % 5 = 1 SUCCESS
3 * 0 % 5 = 0 SUCCESS
3 * 1 % 5 = 3 SUCCESS
3 * 2 % 5 = 1 SUCCESS
3 * 3 % 5 = 4 SUCCESS
3 * 4 % 5 = 2 SUCCESS
2 * 0 % 5 = 0 SUCCESS
2 * 1 % 5 = 2 SUCCESS
2 * 2 % 5 = 4 SUCCESS
2 * 3 % 5 = 1 SUCCESS
2 * 4 % 5 = 3 SUCCESS
1 * 0 % 5 = 0 SUCCESS
1 * 1 % 5 = 1 SUCCESS
1 * 2 % 5 = 2 SUCCESS
1 * 3 % 5 = 3 SUCCESS
1 * 4 % 5 = 4 SUCCESS
0 * 0 % 5 = 0 SUCCESS
0 * 1 % 5 = 0 SUCCESS
0 * 2 % 5 = 0 SUCCESS
0 * 3 % 5 = 0 SUCCESS
0 * 4 % 5 = 0 SUCCESS
3 * 0 % 4 = 0 SUCCESS
3 * 1 % 4 = 3 SUCCESS
3 * 2 % 4 = 2 SUCCESS
3 * 3 % 4 = 29 ERROR
2 * 0 % 4 = 0 SUCCESS
2 * 1 % 4 = 2 SUCCESS
2 * 2 % 4 = 0 SUCCESS
2 * 3 % 4 = 2 SUCCESS
1 * 0 % 4 = 0 SUCCESS
1 * 1 % 4 = 1 SUCCESS
1 * 2 % 4 = 2 SUCCESS
1 * 3 % 4 = 3 SUCCESS
0 * 0 % 4 = 0 SUCCESS
0 * 1 % 4 = 0 SUCCESS
0 * 2 % 4 = 0 SUCCESS
0 * 3 % 4 = 0 SUCCESS
2 * 0 % 3 = 0 SUCCESS
2 * 1 % 3 = 2 SUCCESS
2 * 2 % 3 = 1 SUCCESS
1 * 0 % 3 = 0 SUCCESS
1 * 1 % 3 = 1 SUCCESS
1 * 2 % 3 = 2 SUCCESS
0 * 0 % 3 = 0 SUCCESS
0 * 1 % 3 = 0 SUCCESS
0 * 2 % 3 = 0 SUCCESS
1 * 0 % 2 = 0 SUCCESS
1 * 1 % 2 = 1 SUCCESS
0 * 0 % 2 = 0 SUCCESS
0 * 1 % 2 = 0 SUCCESS
0 * 0 % 1 = 0 SUCCESS
"""
