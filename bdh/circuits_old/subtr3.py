from addr3 import carry3, reverse_carry3, sum3
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import Sampler


def subtr3(A, B, C):
    """
    3-bit VBE subtractor circuit
    |a,b> -> |a,b-a>
    """
    a_0, a_1, a_2 = A
    b_0, b_1, b_2 = B
    c_0, c_1, c_2, c_3 = C

    qc = QuantumCircuit(A, B, C, name="subtr3")

    # Apply the subtractor
    qc.append(sum3(), [c_0, a_0, b_0])
    qc.append(carry3(), [c_0, a_0, b_0, c_1])
    qc.append(sum3(), [c_1, a_1, b_1])
    qc.append(carry3(), [c_1, a_1, b_1, c_2])
    qc.append(sum3(), [c_2, a_2, b_2])
    qc.cx(a_2, b_2)
    qc.append(reverse_carry3(), [c_2, a_2, b_2, c_3])
    qc.append(reverse_carry3(), [c_1, a_1, b_1, c_2])
    qc.append(reverse_carry3(), [c_0, a_0, b_0, c_1])

    return qc


def twos_complement_to_signed_int(binary_str):
    n = len(binary_str)
    unsigned_int = int(binary_str, 2)
    if binary_str[0] == "1":
        signed_int = unsigned_int - (1 << n)
    else:
        signed_int = unsigned_int
    return signed_int


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
            qc.append(subtr3(A, B, C), A[:] + B[:] + C[:])
            qc.measure(B[0], RES[0])
            qc.measure(B[1], RES[1])
            qc.measure(B[2], RES[2])
            qc.measure(C[3], RES[3])
            job = sampler.run(qc, shots=10000000)
            result = job.result()

            res = next(iter(result.quasi_dists[0].binary_probabilities()))
            # res is in two's complement
            if b - a == twos_complement_to_signed_int(res):
                print(f"{b} - {a} = {twos_complement_to_signed_int(res)} : OK")
            else:
                print(f"{b} - {a} = {twos_complement_to_signed_int(res)} : FAIL")


if __name__ == "__main__":
    main()
