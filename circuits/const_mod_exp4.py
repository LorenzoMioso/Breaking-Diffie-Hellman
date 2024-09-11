import time

from const_mod_mult4 import const_mod_mult4
from const_mod_mult4_inv import const_mod_mult4_inv
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from utils import run_circuit


def const_mod_exp4(X, X_MULT, A, B, CARRY, N, T, n, a):
    """
    CMODEXP4 circuit
    CMODEXP$(n)|x,1,0> = |x,a^x mod n,0>

    Inputs:
    - X: 4-bit input register, the exponent
    - X_MULT: 4-bit input register, input for the multiplication, will be set to 1
    - A: 4-bit input register, support register for the multiplication
    - B: 4-bit input register, will contain the result of the multiplication
    - C: 5-bit input register, carry for the addition
    - N: 4-bit input register, modulus
    - T: 1-bit input register, temporary qubit for the modular addition
    - n: number base 10, 1 <= n <= 15, is the modulus
    - a: number base 10, 0 <= a <= 7, is the base, max a = 2^(nbit-1)-1 = 7
    """
    qc = QuantumCircuit(X, X_MULT, A, B, CARRY, N, T, name="const_mod_mult4")

    # prepare to |1> X_MULT
    qc.x(X_MULT[0])

    for i, qx in enumerate(X):
        # apply modular multiplication
        # qx is the control qubit for the multiplication
        qc.append(
            const_mod_mult4([qx], X_MULT, A, B, CARRY, N, T, n, a),
            [qx] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
        )
        # swap B and X_MULT
        qc.swap(X_MULT, B)
        # apply modular multiplication inverse
        qc.append(
            const_mod_mult4_inv([qx], X_MULT, A, B, CARRY, N, T, n, a),
            [qx] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
        )

    # Apply the adder with modulus
    qc.barrier()

    return qc


def main():
    # Create the circuit
    X = QuantumRegister(4, "x")
    X_MULT = QuantumRegister(4, "x_mult")
    A = QuantumRegister(4, "a")
    B = QuantumRegister(4, "b")
    CARRY = QuantumRegister(5, "carry")
    N = QuantumRegister(4, "n")
    T = QuantumRegister(1, "t")
    RESX = ClassicalRegister(4, "res_x")
    RESX_MULT = ClassicalRegister(4, "res_x_mult")
    RESA = ClassicalRegister(4, "res_a")
    RESB = ClassicalRegister(4, "res_b")
    RESN = ClassicalRegister(4, "res_n")
    REST = ClassicalRegister(1, "res_t")

    a = 1

    # test all possible inputs
    for n in range(2**4):
        # print(f"Modulus: {n} ############################")
        for x in range(2**4):
            # print(f"Multiplier: {a}, Multiplicand: {x} ############################")
            if x >= n or a >= n:
                continue
            qc = QuantumCircuit(
                X, X_MULT, A, B, CARRY, N, T, RESX, RESX_MULT, RESA, RESB, RESN, REST
            )

            for i in range(4):
                if x & (1 << i):
                    qc.x(X_MULT[i])
                if n & (1 << i):
                    qc.x(N[i])

            qc.append(
                const_mod_exp4(X, X_MULT, A, B, CARRY, N, T, n, a),
                X[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
            )

            # print(qc.decompose().draw())
            # print(qc.decompose().decompose().draw())
            qc.measure(X_MULT, RESX)
            qc.measure(X_MULT, RESX_MULT)
            qc.measure(A, RESA)
            qc.measure(B, RESB)
            qc.measure(N, RESN)
            qc.measure(T, REST)
            start_time = time.time()
            res = run_circuit(qc)
            print("--- %s seconds ---" % (time.time() - start_time))

            res_t = int(res[0], 2)
            res_n = int(res[1:5], 2)
            res_b = int(res[5:10], 2)
            res_a = int(res[10:14], 2)
            res_x_mult = int(res[14:18], 2)
            res_x = int(res[18:22], 2)

            print(f"res_t = {res_t} ({res[0]})")
            print(f"res_n = {res_n} ({res[1:5]})")
            print(f"res_b = {res_b} ({res[5:10]})")
            print(f"res_a = {res_a} ({res[10:14]})")
            print(f"res_x_mult = {res_x_mult} ({res[14:18]})")
            print(f"res_x = {res_x} ({res[18:22]})")

            print(f"{a}^{x} mod {n} = {res_x_mult}")
            if pow(a, x, n) == res_x_mult:
                print("Correct")
            else:
                print("Incorrect")

            # break
        # break


if __name__ == "__main__":
    main()
