from fractions import Fraction
from math import gcd

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator

from mod_exp_direct import generate_modular_exponentiation_circuit


def create_dla_circuit(p: int, g: int, h: int) -> QuantumCircuit:
    """
    Creates a quantum circuit to solve the discrete logarithm problem:
    Given p (prime), g (generator), and h, find x where g^x ≡ h (mod p)

    Args:
        p: The prime modulus
        g: The generator element
        h: The target element (g^x mod p)

    Returns:
        QuantumCircuit: The circuit implementing Shor's algorithm for DLP
    """
    # Number of qubits needed for the modular arithmetic
    n = p.bit_length()

    # We need 2n qubits for the first register and n for the second
    first_register = QuantumRegister(n, "first")
    second_register = QuantumRegister(n, "second")
    first_classical_register = ClassicalRegister(n, "first_classical")
    second_classical_register = ClassicalRegister(n, "second_classical")

    circuit = QuantumCircuit(
        first_register,
        second_register,
        first_classical_register,
        second_classical_register,
    )

    # Step 1: Initialize superposition in first register
    for i in range(n):
        circuit.h(first_register[i])

    circuit.barrier()

    # Step 2: Create the periodic function
    # f(x) = g^x mod p
    U_g = generate_modular_exponentiation_circuit(g, p, n)

    circuit.append(U_g, first_register[:] + second_register[:])

    circuit.barrier()

    # Step 3: Apply QFT to the first register
    # Fix: Create QFT with size matching first_register
    inverse_qft = QFT(n)
    circuit.append(inverse_qft, first_register)

    print("Circuit before measurement:")
    circuit.barrier()

    circuit.measure(first_register, first_classical_register)
    circuit.measure(second_register, second_classical_register)

    print("Circuit after measurement:")
    print(circuit)

    return circuit


def is_primitive_root(g, p):
    """Check if g is a primitive root modulo p"""
    if p < 2:
        return False

    # Get prime factors of p-1
    factors = set()
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


def extract_period(measurements, p):
    """
    Process the measurement results to find the period
    """
    print(f"Extracting period from measurements: {measurements}")
    if measurements == 0:
        return None

    # Convert measurements to phase
    phase = measurements / (2 ** p.bit_length())

    # Improved continued fraction expansion
    def continued_fractions(x, max_denominator):
        a = []
        q = x
        while len(a) < 100 and q != 0:  # Increased iteration limit
            a.append(int(q))
            q = q - int(q)
            if q == 0:
                break
            q = 1 / q

        convergents = []
        h = [0, 1]
        k = [1, 0]

        for i in range(len(a)):
            if i >= 2:
                h.append(a[i] * h[i - 1] + h[i - 2])
                k.append(a[i] * k[i - 1] + k[i - 2])
                if k[i] > max_denominator:
                    break
                convergents.append(Fraction(h[i], k[i]))

        return convergents

    candidates = continued_fractions(phase, p)

    # Test candidates with improved verification
    best_r = None
    min_residue = float("inf")

    for candidate in candidates:
        r = candidate.denominator
        if 1 < r < p:
            residue = abs(pow(g, r, p) - 1)
            if residue < min_residue:
                min_residue = residue
                best_r = r
                if residue == 0:
                    break

    return best_r


def solve_dlp(p: int, g: int, h: int) -> int:
    """
    Solve the discrete logarithm problem using Shor's algorithm with improved error handling

    Args:
        p: Prime modulus
        g: Generator
        h: Target element (g^x mod p)

    Returns:
        x: Solution to g^x ≡ h (mod p)
    """
    if not is_prime(p):
        raise ValueError("p must be prime")
    if g <= 0 or g >= p:
        raise ValueError("g must be between 1 and p-1")
    if h <= 0 or h >= p:
        raise ValueError("h must be between 1 and p-1")

    max_attempts = 5  # Increased attempts
    periods = set()  # Use set to avoid duplicates

    circuit = create_dla_circuit(p, g, h)

    for attempt in range(max_attempts):
        measurement = simulate_measurement(circuit)
        print(f"Attempt {attempt + 1}: Measured {measurement}")
        period = extract_period(measurement, p)

        if period is not None:
            periods.add(period)
            print(f"Attempt {attempt + 1}: Found period {period}")

            # Try to solve with each period
            for r in periods:
                # Try both positive and negative exponents
                for x in range(r):
                    if pow(g, x, p) == h:
                        return x
                    if pow(g, -x, p) == h:
                        return p - x

    raise RuntimeError(f"Failed to find valid solution after {max_attempts} attempts")


def simulate_measurement(circuit):
    """
    Simulates the measurement outcome using Qiskit's simulator with improved error handling
    """
    backend = AerSimulator()
    shots = 100000  # Increased shots for better statistics

    try:
        compiled_circuit = transpile(circuit, backend, optimization_level=3)
        result = backend.run(compiled_circuit, shots=shots).result()
        counts = result.get_counts(circuit)

        # Process measurements more carefully
        n = len(circuit.clbits) // 2
        measurements = {}

        for bitstring, count in counts.items():
            bitstring = bitstring[::-1]  # Reverse bitstring
            first_reg = bitstring.split(" ")[0]
            value = int(first_reg, 2)
            measurements[value] = measurements.get(value, 0) + count

        print(f"Measurements: {measurements}")

        if not measurements:
            return 0

        # Return the most frequent measurement
        return max(measurements.items(), key=lambda x: x[1])[0]
    except Exception as e:
        print(f"Simulation error: {e}")
        return 0


def is_prime(n: int) -> bool:
    """
    Check if a number is prime
    """
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


# Small example parameters (not secure, for demonstration)
p = 7  # smaller prime modulus
g = 3  # generator
h = 2  # public value

# Find Alice's private key
private_key = solve_dlp(p, g, h)
print(f"Found private key: {private_key}")

# Verify the solution
assert pow(g, private_key, p) == h % p
print("Solution verified successfully")
