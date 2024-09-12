from addr3 import addr3
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import Sampler
from subtr3 import subtr3, twos_complement_to_signed_int


def control_prepare_3(x):
    qc = QuantumCircuit(4)
    if x & 1:
        qc.cx(3, 0)
    if x & 2:
        qc.cx(3, 1)
    if x & 4:
        qc.cx(3, 2)
    return qc


def mod_addr3(A, B, C, N, T, n):
    """
    3-bit VBE adder circuit
    |a,b> -> |a,a+b>, 0 <= a,b < n

    Inputs:
    - A: 3-bit input register, the first operand
    - B: 3-bit input register, the second operand
    - C: 4-bit input register, carry for the addition
    - N: 3-bit input register, modulus
    - T: 1-bit input register, temporary qubit for the modular addition
    - n: number base 10, 1 <= n <= 7, is the modulus
    """
    c_3 = C[3]
    t = T

    qc = QuantumCircuit(A, B, C, N, T, name="mod_addr3")

    # Apply the adder with modulus
    qc.append(addr3(A, B, C), A[:] + B[:] + C[:])
    qc.swap(A, N)
    qc.append(subtr3(A, B, C), A[:] + B[:] + C[:])
    qc.x(c_3)
    qc.cx(c_3, t)
    qc.x(c_3)
    qc.append(control_prepare_3(n), A[:] + [t])
    qc.append(addr3(A, B, C), A[:] + B[:] + C[:])
    qc.append(control_prepare_3(n), A[:] + [t])
    qc.swap(A, N)
    qc.append(subtr3(A, B, C), A[:] + B[:] + C[:])
    qc.cx(c_3, t)
    qc.append(addr3(A, B, C), A[:] + B[:] + C[:])

    return qc


def main():
    # Create the circuit
    A = QuantumRegister(3, "a")
    B = QuantumRegister(3, "b")
    C = QuantumRegister(4, "c")
    N = QuantumRegister(3, "n")
    T = QuantumRegister(1, "t")
    RESA = ClassicalRegister(3, "res_a")
    RESB = ClassicalRegister(4, "res_b")
    RESN = ClassicalRegister(3, "res_n")
    REST = ClassicalRegister(1, "res_t")

    sampler = Sampler()

    # test all possible inputs
    for n in range(1, 8):
        print(f"Modulus: {n} ############################")
        for a in range(8):
            for b in range(8):
                if b >= n or a >= n:
                    continue
                qc = QuantumCircuit(A, B, C, N, T, RESA, RESB, RESN, REST)
                for i in range(3):
                    if a & (1 << i):
                        qc.x(A[i])
                    if b & (1 << i):
                        qc.x(B[i])
                    if n & (1 << i):
                        qc.x(N[i])

                qc.append(mod_addr3(A, B, C, N, T, n), A[:] + B[:] + C[:] + N[:] + T[:])
                # print(qc.decompose().draw())
                qc.measure(A, RESA)
                qc.measure(B[0], RESB[0])
                qc.measure(B[1], RESB[1])
                qc.measure(B[2], RESB[2])
                qc.measure(C[3], RESB[3])
                qc.measure(N, RESN)
                qc.measure(T, REST)
                # print(qc.decompose().draw())
                job = sampler.run(qc, shots=2048)
                result = job.result()
                res = next(iter(result.quasi_dists[0].binary_probabilities()))

                res_t = int(res[0], 2)
                res_n = int(res[1:4], 2)
                # res_b = twos_complement_to_signed_int(res[4:8])
                res_b = int(res[5:8], 2)
                res_a = int(res[8:], 2)

                # print(f"res_t = {res_t} ({res[0]})")
                # print(f"res_n = {res_n} ({res[1:4]})")
                # print(f"res_b = {res_b} ({res[5:8]})")
                # print(f"res_a = {res_a} ({res[8:]})")

                print(f"{a} + {b} % {n} = {res_b}")
                if res_b != (a + b) % n:
                    print("ERROR ##########################")
                # break
            # break
        # break


if __name__ == "__main__":
    main()
