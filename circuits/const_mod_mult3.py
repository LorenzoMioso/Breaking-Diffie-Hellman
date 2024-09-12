from mod_addr3 import mod_addr3
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import Sampler
from utils import run_circuit


def double_controlled_exp_prep(a, k):
    """
    Prepare the register REG with a controlled-controlled number a^k
    First 2 qubits are the control qubits, the last 3 are the target qubits

    Inputs:
    - a: the base of the exponentiation, 0 <= a <= 3
    - k: the exponent, 0 <= k <= 2
    - REGS: the quantum registers to prepare
    """

    assert 0 <= a <= 3, "a must be a number between 0 and 3"
    assert 0 <= k <= 2, "k must be a number between 0 and 2"

    qc = QuantumCircuit(5, name=f"cc_{a}*{2**k}")
    if a == 0:
        return qc

    if a == 1 and k == 0:  # 1
        qc.ccx(0, 1, 2)
    elif a == 1 and k == 1:  # 2
        qc.ccx(0, 1, 3)
    elif a == 1 and k == 2:  # 4
        qc.ccx(0, 1, 4)
    elif a == 2 and k == 0:  # 2
        qc.ccx(0, 1, 3)
    elif a == 2 and k == 1:  # 4
        qc.ccx(0, 1, 4)
    elif a == 2 and k == 2:  # 8
        raise NotImplementedError(f"{a}^{2**k} not implemented yet")
    elif a == 3 and k == 0:  # 3
        qc.ccx(0, 1, 2)
        qc.ccx(0, 1, 3)
    elif a == 3 and k == 1:  # 6
        qc.ccx(0, 1, 3)
        qc.ccx(0, 1, 4)
    elif a == 3 and k == 2:  # 12
        raise NotImplementedError(f"{a}^{2**k} not implemented yet")
    else:
        raise NotImplementedError(f"{a}^{2**k} not implemented yet")

    return qc


def double_controlled_exp_prep_inv(a, k):
    assert 0 <= a <= 3, "a must be a number between 0 and 3"
    assert 0 <= k <= 2, "k must be a number between 0 and 2"

    qc = QuantumCircuit(5, name=f"cc_{a}*{2**k}_inv")
    if a == 0:
        return qc

    if a * 2**k == 1 or a * 2**k == 2 or a * 2**k == 4:
        return double_controlled_exp_prep(a, k)
    elif a * 2**k == 3:
        qc.ccx(0, 1, 3)
        qc.ccx(0, 1, 2)
    elif a * 2**k == 6:
        qc.ccx(0, 1, 4)
        qc.ccx(0, 1, 3)

    return qc


def controlled_copy3(C, A, B):
    """
    Copy the content of register A to register B if C is 0

    """

    qc = QuantumCircuit(C, A, B, name="controlled_copy3")

    qc.x(C)
    for i in range(3):
        qc.ccx(C, A[i], B[i])
    qc.x(C)

    return qc


def const_mod_mult3(C, X, A, B, CARRY, N, T, n, a):
    """
    CMODMULT3 circuit
    CMODMULT3(n)|c,x,0,0> = {
        |c,x,0,ax mod n> if c=1,
        |c,x,0,0>        if c=0

    Inputs:
    - C: 1-bit input register, control
    - X: 3-bit input register, the first operand
    - A: 3-bit input register, support register for the multiplication
    - B: 3-bit input register, support register for the multiplication
    - C: 4-bit input register, carry for the addition
    - N: 3-bit input register, modulus
    - T: 1-bit input register, temporary qubit for the modular addition
    - n: number base 10, 1 <= n <= 7, is the modulus
    - a: number base 10, 0 <= a <= 3, is the multiplier, max a = 2^(nbit-1)-1 = 3
    """
    qc = QuantumCircuit(C, X, A, B, CARRY, N, T, name="const_mod_mult3")

    for i, qx in enumerate(X):
        qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
        qc.append(mod_addr3(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:])
        qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

    qc.append(controlled_copy3(C, X, B), C[:] + X[:] + B[:])

    # Apply the adder with modulus

    return qc


def main():
    # Create the circuit
    C = QuantumRegister(1, "control")
    X = QuantumRegister(3, "x")
    A = QuantumRegister(3, "a")
    B = QuantumRegister(3, "b")
    CARRY = QuantumRegister(4, "carry")
    N = QuantumRegister(3, "n")
    T = QuantumRegister(1, "t")
    RESX = ClassicalRegister(3, "res_x")
    RESA = ClassicalRegister(3, "res_a")
    RESB = ClassicalRegister(4, "res_b")
    RESN = ClassicalRegister(3, "res_n")
    REST = ClassicalRegister(1, "res_t")

    a = 1

    # test all possible inputs
    for n in range(1, 8):
        # n = 7
        for x in range(8):
            # x = 4
            if x >= n or a >= n:
                continue
            qc = QuantumCircuit(C, X, A, B, CARRY, N, T, RESX, RESA, RESB, RESN, REST)
            # set C to 1
            qc.x(C)
            for i in range(3):
                if x & (1 << i):
                    qc.x(X[i])
                if n & (1 << i):
                    qc.x(N[i])

            try:
                qc.append(
                    const_mod_mult3(C, X, A, B, CARRY, N, T, n, a),
                    C[:] + X[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
                )
            except Exception as e:
                print("skipping due to error", e)
                continue

            qc.measure(X, RESX)
            qc.measure(A, RESA)
            qc.measure(B[0], RESB[0])
            qc.measure(B[1], RESB[1])
            qc.measure(B[2], RESB[2])
            qc.measure(CARRY[3], RESB[3])
            qc.measure(N, RESN)
            qc.measure(T, REST)
            # print(qc.decompose().draw())
            # print(qc.decompose().decompose().draw())
            res = run_circuit(qc)

            res_t = int(res[0], 2)
            res_n = int(res[1:4], 2)
            # res_b = twos_complement_to_signed_int(res[4:8])
            res_b = int(res[4:8], 2)
            res_a = int(res[8:11], 2)
            res_x = int(res[11:], 2)

            # print(f"x : {res_x} ({res[11:]})")
            # print(f"a : {res_a} ({res[8:11]})")
            # print(f"b : {res_b} ({res[4:8]})")
            # print(f"n : {res_n} ({res[1:4]})")
            # print(f"t : {res_t} ({res[0]})")

            print(f"{a} * {x} % {n} = {res_b}", end=" ")
            if res_b != (a * x) % n:
                print("ERROR")
            else:
                print("SUCCESS")
            # break
        # break


if __name__ == "__main__":
    main()
