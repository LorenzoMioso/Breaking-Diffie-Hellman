from addr3 import addr3
from addr4 import addr4
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import Sampler
from subtr3 import subtr3, twos_complement_to_signed_int
from subtr4 import subtr4


def control_prepare_4(x):
    qc = QuantumCircuit(5)
    if x & 1:
        qc.cx(4, 0)
    if x & 2:
        qc.cx(4, 1)
    if x & 4:
        qc.cx(4, 2)
    if x & 8:
        qc.cx(4, 3)
    return qc


def mod_addr4(A, B, C, N, T, n):
    """
    4-bit VBE adder circuit
    |a,b> -> |a,a+b>, 0 <= a,b < n

    Inputs:
    - A: 4-bit input register, the first operand
    - B: 4-bit input register, the second operand
    - C: 5-bit input register, carry for the addition
    - N: 4-bit input register, modulus
    - T: 1-bit input register, temporary qubit for the modular addition
    - n: number base 10, 1 <= n <= 15, is the modulus
    """
    c_4 = C[4]
    t = T

    qc = QuantumCircuit(A, B, C, N, T, name="mod_addr4")

    # Apply the adder with modulus
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
    qc.swap(A, N)
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])
    qc.x(c_4)
    qc.cx(c_4, t)
    qc.x(c_4)
    qc.barrier()
    qc.append(control_prepare_4(n), A[:] + [t])
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
    qc.append(control_prepare_4(n), A[:] + [t])
    qc.swap(A, N)
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])
    qc.barrier()
    qc.cx(c_4, t)
    qc.barrier()
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
    qc.barrier()

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

    sampler = Sampler()

    # test all possible inputs
    for n in range(1, 2**4):
        print(f"Modulus: {n} ############################")
        for a in range(2**4):
            for b in range(2**4):
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

                qc.append(mod_addr4(A, B, C, N, T, n), A[:] + B[:] + C[:] + N[:] + T[:])
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
                job = sampler.run(qc, shots=1)
                result = job.result()
                res = next(iter(result.quasi_dists[0].binary_probabilities()))

                res_t = int(res[0], 2)
                res_n = int(res[1:5], 2)
                # res_b = twos_complement_to_signed_int(res[4:8])
                res_b = int(res[6:10], 2)
                res_a = int(res[10:], 2)

                #print(f"res_t = {res_t} ({res[0]})")
                #print(f"res_n = {res_n} ({res[1:5]})")
                #print(f"res_b = {res_b} ({res[6:10]})")
                #print(f"res_a = {res_a} ({res[10:]})")

                print(f"{a} + {b} % {n} = {res_b}, {"OK" if (a + b) % n == res_b else "FAIL"}")
                # print(
                #    f"bits_a = {res[8:]}, bits_b = {res[4:8]}, bits_n = {res[1:4]}, bits_t = {res[0]}"
                # )
                # print(
                #    f"res_a = {res_a}, res_b = {res_b}, res_n = {res_n}, res_t = {res_t}"
                # )
                # break
            # break
        # break


if __name__ == "__main__":
    main()
