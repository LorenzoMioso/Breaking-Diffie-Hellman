from const_mod_mult4 import const_mod_mult4
from const_mod_mult4_inv import const_mod_mult4_inv
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from utils import run_circuit


def const_mod_exp4(X, C, X_MULT, A, B, CARRY, N, T, n, a):
    """
    CMODEXP4 circuit
    CMODEXP$(n)|x,1,0> = |x,a^x mod n,0>

    Inputs:
    - X: 4-bit input register, the exponent
    - C: 1-bit input register, control bit
    - X_MULT: 4-bit input register, input for the multiplication, will be set to 1
    - A: 4-bit input register, support register for the multiplication
    - B: 4-bit input register, will contain the result of the multiplication
    - C: 5-bit input register, carry for the addition
    - N: 4-bit input register, modulus
    - T: 1-bit input register, temporary qubit for the modular addition
    - n: number base 10, 1 <= n <= 15, is the modulus
    - a: number base 10, 0 <= a <= 7, is the base, max a = 2^(nbit-1)-1 = 7
    """
    qc = QuantumCircuit(X, C, X_MULT, A, B, CARRY, N, T, name="const_mod_mult4")

    qc.barrier()

    # prepare to |1> X_MULT
    qc.x(X_MULT[0])

    for i, qx in enumerate(X):
        # qx must activate the multiplication by flipping C
        qc.cx(qx, C)
        # apply modular multiplication
        qc.append(
            const_mod_mult4(C, X_MULT, A, B, CARRY, N, T, n, a),
            C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
        )
        # swap B and X_MULT
        qc.swap(X_MULT, B)
        # reset C
        qc.cx(qx, C)
        # apply modular multiplication inverse
        qc.append(
            const_mod_mult4_inv(C, X_MULT, A, B, CARRY, N, T, n, a),
            C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
        )

    # qx_0 = X[0]
    # qx_1 = X[1]
    # qx_2 = X[2]
    # qx_3 = X[3]

    ## first iteration
    # qc.cx(qx_0, C)
    # qc.append(
    #    const_mod_mult4(C, X_MULT, A, B, CARRY, N, T, n, a),
    #    C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
    # )
    # qc.swap(X_MULT, B)
    # qc.append(
    #    const_mod_mult4_inv(C, X_MULT, A, B, CARRY, N, T, n, a),
    #    C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
    # )
    # qc.cx(qx_0, C)
    ## second iteration
    # qc.cx(qx_1, C)
    # qc.append(
    #    const_mod_mult4(C, X_MULT, A, B, CARRY, N, T, n, a),
    #    C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
    # )

    # Apply the adder with modulus
    qc.barrier()

    return qc


def main():
    # Create the circuit
    X = QuantumRegister(4, "x")
    C = QuantumRegister(1, "control")
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
    RESCAR = ClassicalRegister(5, "res_car")
    RESN = ClassicalRegister(4, "res_n")
    REST = ClassicalRegister(1, "res_t")

    a = 3

    # test all possible inputs
    for n in range(2**4):
        # print(f"Modulus: {n} ############################")
        n = 15
        for x in range(2**4):
            x = 1
            # print(f"Multiplier: {a}, Multiplicand: {x} ############################")
            if x >= n or a >= n:
                continue

            qc = QuantumCircuit(
                X,
                C,
                X_MULT,
                A,
                B,
                CARRY,
                N,
                T,
                RESX,
                RESX_MULT,
                RESA,
                RESB,
                RESCAR,
                RESN,
                REST,
            )

            for i in range(4):
                if x & (1 << i):
                    qc.x(X[i])
                if n & (1 << i):
                    qc.x(N[i])

            qc.append(
                const_mod_exp4(X, C, X_MULT, A, B, CARRY, N, T, n, a),
                X[:] + C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
            )

            print(qc.decompose().draw())
            # print(qc.decompose().decompose().draw())
            qc.measure(X, RESX)
            qc.measure(X_MULT, RESX_MULT)
            qc.measure(A, RESA)
            qc.measure(B, RESB)
            qc.measure(CARRY, RESCAR)
            qc.measure(N, RESN)
            qc.measure(T, REST)
            # exit(0)
            res = run_circuit(qc)

            res_t = int(res[0], 2)
            res_n = int(res[1:5], 2)
            res_car = int(res[5:10], 2)
            res_b = int(res[10:14], 2)
            res_a = int(res[14:18], 2)
            res_x_mult = int(res[18:22], 2)
            res_x = int(res[22:], 2)

            print(f"res_t = {res_t} ({res[0]})")
            print(f"res_n = {res_n} ({res[1:5]})")
            print(f"res_car = {res_car} ({res[5:10]})")
            print(f"res_b = {res_b} ({res[10:14]})")
            print(f"res_a = {res_a} ({res[14:18]})")
            print(f"res_x_mult = {res_x_mult} ({res[18:22]})")
            print(f"res_x = {res_x} ({res[22:]})")

            print(f"{a}^{x} mod {n} = {res_b}")
            if pow(a, x, n) == res_b:
                print("Correct")
            else:
                print("Incorrect, should be", pow(a, x, n))

            break
        break


if __name__ == "__main__":
    main()


# 1Iter : Only fist multiplication
# --- 50.765464544296265 seconds ---
# {'0 1111 00000 0011 0000 0001 0001': 1}
# res_t = 0 (0)
# res_n = 15 (1111)
# res_car = 0 (00000)
# res_b = 3 (0011)
# res_a = 0 (0000)
# res_x_mult = 1 (0001)
# res_x = 1 (0001)
# 3^1 mod 15 = 1
# Incorrect

# 1Iter :Swap
# --- 53.4604070186615 seconds ---
# {'0 1111 00000 0001 0000 0011 0001': 1}
# res_t = 0 (0)
# res_n = 15 (1111)
# res_car = 0 (00000)
# res_b = 1 (0001)
# res_a = 0 (0000)
# res_x_mult = 3 (0011)
# res_x = 1 (0001)
# 3^1 mod 15 = 3
# Incorrect

# 1Iter Inverse multiplication
# MULT_INV|c,x,0, ax mod n> = |c,x,0,0>
# MULT_INV|1,3,0,1> = |1,1,0,0>

# --- 96.45589113235474 seconds ---
# {'0 1111 00000 0111 0000 0011 0001': 1}
# res_t = 0 (0)
# res_n = 15 (1111)
# res_car = 0 (00000)
# res_b = 7 (0111)
# res_a = 0 (0000)
# res_x_mult = 3 (0011)
# res_x = 1 (0001)
# 3^1 mod 15 = 3
# Incorrect

# 2Iter : Only multiplication
# --- 141.97481632232666 seconds ---
# {'0 1111 00000 0100 0000 0011 0001': 1}
# res_t = 0 (0)
# res_n = 15 (1111)
# res_car = 0 (00000)
# res_b = 4 (0100)
# res_a = 0 (0000)
# res_x_mult = 3 (0011)
# res_x = 1 (0001)
# 3^1 mod 15 = 3
# Correct
