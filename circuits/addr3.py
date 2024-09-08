from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import Sampler


def carry3():
    """
    supp, a, b, c are the input qubits
    """
    qc = QuantumCircuit(4, name="carry3")
    qc.ccx(1, 2, 3)
    qc.cx(1, 2)
    qc.ccx(0, 2, 3)
    return qc


def reverse_carry3():
    """
    c0, a, b, c1 are the input qubits
    """
    qc = QuantumCircuit(4, name="reverse_carry3")
    qc.ccx(0, 2, 3)
    qc.cx(1, 2)
    qc.ccx(1, 2, 3)
    return qc


def sum3():
    """
    a, b, c are the input qubits
    """
    qc = QuantumCircuit(3, name="sum3")
    qc.cx(0, 2)
    qc.cx(1, 2)
    return qc


def addr3(A, B, C):
    """
    3-bit VBE adder circuit
    |a,b> -> |a,a+b>
    """
    a_0, a_1, a_2 = A
    b_0, b_1, b_2 = B
    c_0, c_1, c_2, c_3 = C

    qc = QuantumCircuit(A, B, C, name="addr3")

    # Apply the adder
    qc.append(carry3(), [c_0, a_0, b_0, c_1])
    qc.append(carry3(), [c_1, a_1, b_1, c_2])
    qc.append(carry3(), [c_2, a_2, b_2, c_3])
    qc.cx(a_2, b_2)
    qc.append(sum3(), [c_2, a_2, b_2])
    qc.append(reverse_carry3(), [c_1, a_1, b_1, c_2])
    qc.append(sum3(), [c_1, a_1, b_1])
    qc.append(reverse_carry3(), [c_0, a_0, b_0, c_1])
    qc.append(sum3(), [c_0, a_0, b_0])

    return qc


def main():
    # Create the circuit
    A = QuantumRegister(3, "a")
    B = QuantumRegister(3, "b")
    C = QuantumRegister(4, "c")
    RES = ClassicalRegister(4, "res")
    qc = QuantumCircuit(A, B, C, RES)

    sampler = Sampler()

    # test all possible inputs
    for a in range(8):
        for b in range(8):
            qc = QuantumCircuit(A, B, C, RES)
            for i in range(3):
                if a & (1 << i):
                    qc.x(A[i])
                if b & (1 << i):
                    qc.x(B[i])
            qc.append(addr3(A, B, C), A[:] + B[:] + C[:])
            qc.measure(B[0], RES[0])
            qc.measure(B[1], RES[1])
            qc.measure(B[2], RES[2])
            qc.measure(C[3], RES[3])
            job = sampler.run(qc, shots=10000000)
            result = job.result()

            res = next(iter(result.quasi_dists[0]))
            if a + b == res:
                print(f"{a} + {b} = {res} : OK")
            else:
                print(f"{a} + {b} = {res} : FAIL")


if __name__ == "__main__":
    main()
