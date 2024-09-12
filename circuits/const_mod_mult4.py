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

    assert 0 <= a <= 7, "a must be a number between 0 and 7"
    assert 0 <= k <= 3, "k must be a number between 0 and 3"

    result = a * (2**k)

    # if result > 15:
    #    print(f"Result {a}*{2**k}={result} cannot be represented with 4 bits")

    qc = QuantumCircuit(6, name=f"cc_{a}*{2**k}")

    if result == 0:
        return qc  # No need to do anything for a result of 0

    # Apply CCX based on the binary representation of result
    for i in range(4):  # last 4 qubits are the target qubits
        if result & (1 << i):
            qc.ccx(0, 1, 2 + i)

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

    # if result > 15:
    #    print(f"Result {a}*{2**k}={result} cannot be represented with 4 bits")

    qc = QuantumCircuit(6, name=f"cc_{a}*{2**k}_inv")

    if result == 0:
        return qc  # No need to do anything for a result of 0

    # Apply CCX based on the binary representation of result
    for i in reversed(range(4)):  # last 3 qubits are the target qubits
        if result & (1 << i):
            qc.ccx(0, 1, 2 + i)

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
    qc = QuantumCircuit(C, X, A, B, CARRY, N, T, name="const_mod_mult4")

    for i, qx in enumerate(X):
        qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
        qc.append(mod_addr4(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:])
        qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

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
    RESN = ClassicalRegister(4, "res_n")
    REST = ClassicalRegister(1, "res_t")

    a = 2
    apply_multiplier = True

    # test all possible inputs
    for n in range(2**4):
        n = 15
        # print(f"Modulus: {n} ############################")
        for x in range(1, 2**4):
            # print(f"Multiplier: {a}, Multiplicand: {x} ############################")
            # if x >= n or a >= n or a * x >= n:
            if x >= n or a >= n or ((a * int(2 ** math.log2(x))) > 15):
                continue
            qc = QuantumCircuit(C, X, A, B, CARRY, N, T, RESX, RESA, RESB, RESN, REST)
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
            qc.measure(N, RESN)
            qc.measure(T, REST)
            res = run_circuit(qc)

            res_t = int(res[0], 2)
            res_n = int(res[1:5], 2)
            res_b = int(res[5:10], 2)
            res_a = int(res[10:14], 2)
            res_x = int(res[14:], 2)

            # print(f"t = {res_t}, ({res[0]})")
            # print(f"n = {res_n}, ({res[1:5]})")
            # print(f"b = {res_b}, ({res[5:10]})")
            # print(f"a = {res_a}, ({res[10:14]})")
            # print(f"x = {res_x}, ({res[14:]})")

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

        exit(0)


if __name__ == "__main__":
    main()
