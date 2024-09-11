from addr4 import addr4
from mod_addr4 import control_prepare_4
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from subtr3 import twos_complement_to_signed_int
from subtr4 import subtr4
from utils import run_circuit


def mod_subtr4(A, B, C, N, T, n):
    """
    4-bit VBE subtractor circuit
    |a,b> -> |a,b-a>, 0 <= a,b < n

    Inputs:
    - A: 4-bit input register, the first operand
    - B: 4-bit input register, the second operand
    - C: 5-bit input register, carry for the addition
    - N: 4-bit input register, modulus
    - T: 1-bit input register, temporary qubit for the modular addition
    - n: number base 10, 1 <= n <= 15, is the modulus
    """
    b_3 = B[3]
    c_4 = C[4]
    t = T

    qc = QuantumCircuit(A, B, C, N, T, name="mod_subtr4")

    # Apply the subtractor with modulus
    qc.barrier()
    # b - a
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])
    qc.barrier()
    qc.cx(c_4, t)
    qc.barrier()
    # (b - a) + a
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
    qc.swap(A, N)
    qc.append(control_prepare_4(n), A[:] + [t])
    # (b - a) + a - n if overflow
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])
    qc.append(control_prepare_4(n), A[:] + [t])
    qc.barrier()
    qc.x(c_4)
    qc.cx(c_4, t)
    qc.x(c_4)
    # (b - a) + a - n + n if overflow
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
    qc.swap(A, N)
    #
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])

    # this modulator is not working b

    return qc


def main():
    # Create the circuit
    A = QuantumRegister(4, "a")
    B = QuantumRegister(4, "b")
    C = QuantumRegister(5, "c")
    N = QuantumRegister(4, "n")
    T = QuantumRegister(1, "t")
    RESA = ClassicalRegister(4, "res_a")
    RESB = ClassicalRegister(5, "res_b")
    RESN = ClassicalRegister(4, "res_n")
    REST = ClassicalRegister(1, "res_t")

    # test all possible inputs
    for n in range(1, 2**4):
        # print(f"Modulus: {n} ############################")
        for a in range(2**4):
            for b in reversed(range(2**4)):
                if b >= n or a >= n:
                    continue
                qc = QuantumCircuit(A, B, C, N, T, RESA, RESB, RESN, REST)
                for i in range(4):
                    if a & (1 << i):
                        qc.x(A[i])
                    if b & (1 << i):
                        qc.x(B[i])
                    if n & (1 << i):
                        qc.x(N[i])

                qc.append(
                    mod_subtr4(A, B, C, N, T, n), A[:] + B[:] + C[:] + N[:] + T[:]
                )

                # print(qc.decompose().draw())
                qc.measure(A, RESA)
                qc.measure(B[0], RESB[0])
                qc.measure(B[1], RESB[1])
                qc.measure(B[2], RESB[2])
                qc.measure(B[3], RESB[3])
                qc.measure(C[4], RESB[4])
                qc.measure(N, RESN)
                qc.measure(T, REST)
                # print(qc.decompose().draw())
                res = run_circuit(qc)

                res_t = int(res[0], 2)
                res_n = int(res[1:5], 2)
                res_b = twos_complement_to_signed_int(res[5:10])
                res_a = int(res[10:], 2)

                print(
                    f"{b} - {a} % {n} = {res_b}, {'OK' if (b - a) % n == res_b else 'FAIL'}"
                )

                # break
            # break
        # break


if __name__ == "__main__":
    main()
