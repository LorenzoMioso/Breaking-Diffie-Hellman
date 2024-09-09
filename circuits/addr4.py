from addr3 import carry3, reverse_carry3, sum3
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import Sampler


def addr4(A, B, C):
    """
    4-bit VBE adder circuit
    |a,b> -> |a,a+b>
    """
    a_0, a_1, a_2, a_3 = A
    b_0, b_1, b_2, b_3 = B
    c_0, c_1, c_2, c_3, c_4 = C

    qc = QuantumCircuit(A, B, C, name="addr4")

    # Apply the adder
    qc.append(carry3(), [c_0, a_0, b_0, c_1])
    qc.append(carry3(), [c_1, a_1, b_1, c_2])
    qc.append(carry3(), [c_2, a_2, b_2, c_3])
    qc.append(carry3(), [c_3, a_3, b_3, c_4])

    qc.cx(a_3, b_3)
    qc.append(sum3(), [c_3, a_3, b_3])
    qc.append(reverse_carry3(), [c_2, a_2, b_2, c_3])
    qc.append(sum3(), [c_2, a_2, b_2])
    qc.append(reverse_carry3(), [c_1, a_1, b_1, c_2])
    qc.append(sum3(), [c_1, a_1, b_1])
    qc.append(reverse_carry3(), [c_0, a_0, b_0, c_1])
    qc.append(sum3(), [c_0, a_0, b_0])

    return qc


def main():
    # Create the circuit
    A = QuantumRegister(4, "a")
    B = QuantumRegister(4, "b")
    C = QuantumRegister(5, "c")
    RES = ClassicalRegister(5, "res")
    qc = QuantumCircuit(A, B, C, RES)

    sampler = Sampler()

    # test all possible inputs
    for a in range(2**4):
        for b in range(2**4):
            qc = QuantumCircuit(A, B, C, RES)
            for i in range(4):
                if a & (1 << i):
                    qc.x(A[i])
                if b & (1 << i):
                    qc.x(B[i])
            qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
            qc.measure(B[0], RES[0])
            qc.measure(B[1], RES[1])
            qc.measure(B[2], RES[2])
            qc.measure(B[3], RES[3])
            qc.measure(C[4], RES[4])
            job = sampler.run(qc, shots=10000000)
            result = job.result()

            res = next(iter(result.quasi_dists[0]))
            if a + b == res:
                print(f"{a} + {b} = {res} : OK")
            else:
                print(f"{a} + {b} = {res} : FAIL")


if __name__ == "__main__":
    main()
