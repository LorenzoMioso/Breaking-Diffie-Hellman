from fractions import Fraction
from math import gcd
from typing import List, Set

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator


def is_primitive_root(g: int, p: int) -> bool:
    """Check if g is a primitive root modulo p

    >>> is_primitive_root(3, 7)
    True
    >>> is_primitive_root(2, 7)
    False
    """
    if p < 2:
        return False

    # Get prime factors of p-1
    factors: Set[int] = set()
    n = p - 1
    for i in range(2, int(n**0.5) + 1):
        while n % i == 0:
            factors.add(i)
            n //= i
    if n > 1:
        factors.add(n)

    # Check if g is a primitive root
    for factor in factors:
        if pow(g, (p - 1) // factor, p) == 1:
            return False
    return True


def generate_modular_exponentiation_circuit(
    g: int, p: int, n_bits: int
) -> QuantumCircuit:
    """Generate a quantum circuit for modular exponentiation

    Args:
        g: Generator (must be primitive root)
        p: Prime modulus
        n_bits: Number of qubits for each register

    Returns:
        QuantumCircuit implementing |x⟩|0⟩ → |x⟩|g^x mod p⟩
    """
    if not is_primitive_root(g, p):
        raise ValueError(f"{g} is not a primitive root modulo {p}")
    if p >= 2**n_bits:
        raise ValueError(f"n_bits={n_bits} is too small to represent p={p}")

    # Create quantum registers
    x_reg = QuantumRegister(n_bits, "x")
    out_reg = QuantumRegister(n_bits, "out")
    qc = QuantumCircuit(x_reg, out_reg)

    # Fix bit ordering to match conventional representation
    for x in range(p):
        x_bin = format(x, f"0{n_bits}b")[::-1]  # Reverse bits
        result = pow(g, x, p)
        result_bin = format(result, f"0{n_bits}b")[::-1]  # Reverse bits

        # Create control pattern
        ctrl_pattern: List[QuantumRegister] = []
        for i, bit in enumerate(x_bin):
            if bit == "1":
                ctrl_pattern.append(x_reg[i])
            else:
                qc.x(x_reg[i])
                ctrl_pattern.append(x_reg[i])

        # Apply result bits
        for i, bit in enumerate(result_bin):
            if bit == "1":
                qc.mcx(ctrl_pattern, out_reg[i])

        # Cleanup x flips
        for i, bit in enumerate(x_bin):
            if bit == "0":
                qc.x(x_reg[i])

    return qc


def parse_result(counts: dict, n_bits: int) -> (int, int):
    print("Counts:")
    print(counts)
    x = 0
    y = 0
    for key in counts:
        key = key[::-1]  # Reverse bits to match conventional representation
        # Parse bits directly as they are already in correct order from measurement
        x = int(key[:n_bits], 2)
        print(f"x string: {key[:n_bits]}, x: {x}")
        y = int(key[n_bits:], 2)
        print(f"y string: {key[n_bits:]}, y: {y}")
        break

    return (x, y)


# Test the quantum implementation
def test_quantum_mod_exp(x: int = 2):
    g = 3  # Generator
    p = 7  # Prime modulus
    n_bits = 3  # Number of bits needed to represent p

    # Create registers and circuit
    x_reg = QuantumRegister(n_bits, "x")
    y_reg = QuantumRegister(n_bits, "y")
    x_classic = ClassicalRegister(n_bits, "x_classic")
    out_classic = ClassicalRegister(n_bits, "y_classic")

    qc = QuantumCircuit(x_reg, y_reg, x_classic, out_classic)

    x_bin = format(x, f"0{n_bits}b")[::-1]  # Reverse bits to match circuit encoding

    # Prepare input state - use direct indexing since circuit handles bit order
    for i, bit in enumerate(x_bin):
        if bit == "1":
            qc.x(x_reg[i])

    qc.barrier()
    # Generate modular exponentiation circuit
    u_cirq = generate_modular_exponentiation_circuit(g, p, n_bits)
    qc.append(u_cirq, x_reg[:] + y_reg[:])

    # Add measurements - measure in reverse order to match classical interpretation
    qc.barrier()
    for i in range(n_bits):
        qc.measure(x_reg[n_bits - 1 - i], x_classic[i])
        qc.measure(y_reg[n_bits - 1 - i], out_classic[i])

    # Run simulation
    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit).result()
    counts = result.get_counts()
    expected_y = pow(g, x, p)
    print(f"Expected y: {expected_y}")
    res = parse_result(counts, n_bits)
    res_x = res[0]
    res_y = res[1]
    print(f"Result x: {res_x}, y: {res_y}")
    assert res_x == x
    assert res_y == expected_y


if __name__ == "__main__":
    # Test with known primitive root
    g = 3  # 3 is a primitive root modulo 7
    p = 7
    # g^0 mod 7 = 1
    # g^1 mod 7 = 3
    # g^2 mod 7 = 2
    # g^3 mod 7 = 6
    # g^4 mod 7 = 4
    # g^5 mod 7 = 5
    # g^6 mod 7 = 1
    # g^7 mod 7 = 3
    # g^8 mod 7 = 2

    # Test quantum implementation
    test_quantum_mod_exp(7)
