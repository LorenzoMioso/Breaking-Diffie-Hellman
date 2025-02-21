from math import pi

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

S_simulator = AerSimulator()


class QPE:
    def __init__(self, angle=None):
        self.simulator = AerSimulator()
        self.angle = angle

    def set_angle(self, angle):
        self.angle = angle

    def qft_inverse(self, qc, n):
        for qubit in range(n // 2):
            qc.swap(qubit, n - qubit - 1)
        for j in range(n):
            for m in range(j):
                qc.cp(-pi / float(2 ** (j - m)), m, j)
            qc.h(j)

    def make_circuit(self, n):
        if self.angle is None:
            raise ValueError("Angle must be set before creating circuit")
        m = n + 1
        qc = QuantumCircuit(m, n)
        # Prep
        for qubit in range(n):
            qc.h(qubit)
        qc.x(n)
        # CU1 gates
        reps = 1
        for counting_qubit in range(n):
            for i in range(reps):
                qc.cp(self.angle, counting_qubit, n)
            reps *= 2
            qc.barrier()

        self.qft_inverse(qc, n)
        qc.barrier()
        for n in range(n):
            qc.measure(n, n)
        return qc

    def get_results(self, q, n):
        m = n - 1
        q_compiled = transpile(q, backend=self.simulator)
        results = self.simulator.run(q_compiled).result()
        histo = results.get_counts()
        higher = max(histo.values())
        newhisto = dict([(value, key) for key, value in histo.items()])
        answer = int(newhisto[higher], 2)
        return answer / (2**m)

    def get_phase_estimation(self, phase, precision):
        self.set_angle(phase)
        circuit = self.make_circuit(precision)
        result = self.get_results(circuit, precision)
        return result, circuit


def get_user_input():
    while True:
        try:
            print("\nEnter phase (in radians, or expressions like '3/2*pi', 'pi/4'): ")
            phase_input = input().strip()
            if "pi" in phase_input.lower():
                phase = eval(phase_input.lower().replace("pi", str(pi)))
            else:
                phase = eval(phase_input)

            print("Enter precision (number of qubits): ")
            precision_input = input().strip()

            if (
                precision_input == ""
                or not precision_input.isdigit()
                or int(precision_input) < 0
            ):
                raise ValueError("Precision must be positive integer greater than 0")

            return phase, int(precision_input)

        except (ValueError, SyntaxError, NameError) as e:
            print(f"Invalid input: {e}. Please try again.")


def main():
    qpe = QPE()

    phase, precision = get_user_input()

    estimated_phase, circuit = qpe.get_phase_estimation(phase, precision)
    print("\nQuantum Circuit:")
    print(circuit)
    print(f"\nResults:")
    print(f"True phase: {phase/(2*pi)}")
    print(f"Estimated phase: {estimated_phase}")
    print(f"Absolute error: {abs(phase/(2*pi) - estimated_phase)}")


if __name__ == "__main__":
    main()
