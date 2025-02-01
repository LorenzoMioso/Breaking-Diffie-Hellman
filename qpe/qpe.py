from fractions import Fraction
from math import *

import matplotlib.pyplot as plt
import numpy as np
from qiskit import *
from qiskit.visualization import plot_histogram
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
        m = n - 1
        qc = QuantumCircuit(n, m)
        # Prep
        for qubit in range(m):
            qc.h(qubit)
        qc.x(m)
        # CU1 gates
        reps = 1
        for counting_qubit in range(m):
            for i in range(reps):
                qc.cp(self.angle, counting_qubit, m)
            reps *= 2
            qc.barrier()

        self.qft_inverse(qc, m)
        qc.barrier()
        for n in range(m):
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
        """
        Performs quantum phase estimation for a given phase and precision

        Args:
            phase (float): The phase to estimate (in radians)
            precision (int): Number of qubits to use (determines precision)

        Returns:
            tuple: (estimated_phase, quantum_circuit)
        """
        self.set_angle(phase)
        circuit = self.make_circuit(precision)
        result = self.get_results(circuit, precision)
        return result, circuit


def main():
    qpe = QPE()  # Now creates QPE instance without angle

    # Example of using the new phase estimation function
    phase = pi / 4  # Example phase
    precision = 5  # Number of qubits

    estimated_phase, circuit = qpe.get_phase_estimation(phase, precision)
    print(f"True phase: {phase/2/pi}")
    print(f"Estimated phase: {estimated_phase}")
    print("\nQuantum Circuit:")
    print(circuit)


if __name__ == "__main__":
    main()
