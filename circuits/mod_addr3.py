from addr3 import addr3
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import Sampler
from subtr3 import subtr3


def prepare_3(x):
    qc = QuantumCircuit(3)
    if x & 1:
        qc.x(0)
    if x & 2:
        qc.x(1)
    if x & 4:
        qc.x(2)
    return qc


def mod_addr3(A, B, C, N, T, n):
    """
    3-bit VBE adder circuit
    |a,b> -> |a,a+b>
    """
    a_0, a_1, a_2 = A
    b_0, b_1, b_2 = B
    n_0, n_1, n_2 = N
    c_0, c_1, c_2, c_3 = C
    t = T

    qc = QuantumCircuit(A, B, C, N, T, name="mod_addr3")

    # Apply the adder with modulus
    qc.append(addr3(A, B, C), A[:] + B[:] + C[:])
    qc.swap(A, N)
    qc.append(subtr3(A, B, C), A[:] + B[:] + C[:])
    qc.x(c_3)
    qc.cx(c_3, t)
    qc.x(c_3)
    qc.barrier()
    qc.append(prepare_3(n).control(1), [t] + A[:])
    qc.append(addr3(A, B, C), A[:] + B[:] + C[:])
    qc.append(prepare_3(n).control(1), [t] + A[:])
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
    RES = ClassicalRegister(4, "res")
    qc = QuantumCircuit(A, B, C, RES)

    sampler = Sampler()

    # test all possible inputs
    for a in range(8):
        for b in range(8):
            for n in range(8):
                for t in range(2):
                    qc = QuantumCircuit(A, B, C, N, T, RES)
                    for i in range(3):
                        if a & (1 << i):
                            qc.x(A[i])
                        if b & (1 << i):
                            qc.x(B[i])
                        if n & (1 << i):
                            qc.x(N[i])

                    qc.append(
                        mod_addr3(A, B, C, N, T, n), A[:] + B[:] + C[:] + N[:] + T[:]
                    )
                    # print(qc.decompose().draw())
                    qc.measure(C, RES)
                    job = sampler.run(qc, shots=2048)
                    result = job.result()
                    res = next(iter(result.quasi_dists[0]))
                    print(f"{a} + {b} % {n} = {res}")
                    # break
                # break
            # break
        # break


if __name__ == "__main__":
    main()
