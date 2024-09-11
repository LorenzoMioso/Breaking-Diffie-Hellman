from addr3 import carry3, reverse_carry3, sum3
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from subtr3 import twos_complement_to_signed_int
from utils import run_circuit


def subtr4(A, B, C):
    """
    4-bit VBE subtractor circuit
    |a,b> -> |a,b-a>
    """
    a_0, a_1, a_2, a_3 = A
    b_0, b_1, b_2, b_3 = B
    c_0, c_1, c_2, c_3, c_4 = C

    qc = QuantumCircuit(A, B, C, name="subtr4")

    # Apply the subtractor
    qc.append(sum3(), [c_0, a_0, b_0])
    qc.append(carry3(), [c_0, a_0, b_0, c_1])
    qc.append(sum3(), [c_1, a_1, b_1])
    qc.append(carry3(), [c_1, a_1, b_1, c_2])
    qc.append(sum3(), [c_2, a_2, b_2])
    qc.append(carry3(), [c_2, a_2, b_2, c_3])
    qc.append(sum3(), [c_3, a_3, b_3])
    qc.cx(a_3, b_3)
    qc.append(reverse_carry3(), [c_3, a_3, b_3, c_4])
    qc.append(reverse_carry3(), [c_2, a_2, b_2, c_3])
    qc.append(reverse_carry3(), [c_1, a_1, b_1, c_2])
    qc.append(reverse_carry3(), [c_0, a_0, b_0, c_1])

    return qc


def main():
    # Create the circuit
    A = QuantumRegister(4, "a")
    B = QuantumRegister(4, "b")
    C = QuantumRegister(5, "c")
    RES = ClassicalRegister(5, "res")
    qc = QuantumCircuit(A, B, C, RES)

    # test all possible inputs
    for a in range(2**4):
        for b in range(2**4):
            qc = QuantumCircuit(A, B, C, RES)
            for i in range(2**4):
                if a & (1 << i):
                    qc.x(A[i])
                if b & (1 << i):
                    qc.x(B[i])
            qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])
            qc.measure(B[0], RES[0])
            qc.measure(B[1], RES[1])
            qc.measure(B[2], RES[2])
            qc.measure(B[3], RES[3])
            qc.measure(C[4], RES[4])
            res = run_circuit(qc)
            # res is in two's complement
            if b - a == twos_complement_to_signed_int(res):
                print(f"{b} - {a} = {twos_complement_to_signed_int(res)} : OK")
            else:
                print(f"{b} - {a} = {twos_complement_to_signed_int(res)} : FAIL")


if __name__ == "__main__":
    main()
