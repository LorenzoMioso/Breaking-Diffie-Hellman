from const_mod_mult4 import const_mod_mult4
from const_mod_mult4_inv import const_mod_mult4_inv
from qiskit import QuantumCircuit, QuantumRegister, transpile
from qiskit_aer import AerSimulator


def debug_const_mod_exp4(X, C, X_MULT, A, B, CARRY, N, T, n, a, x_val):
    """
    Versione debug del circuito con punti di controllo
    """
    qc = QuantumCircuit(X, C, X_MULT, A, B, CARRY, N, T, name="debug_const_mod_exp4")

    # Inizializzazione
    qc.barrier()
    qc.x(X_MULT[0])

    # Prepara input X
    for i in range(len(X)):
        if x_val & (1 << i):
            qc.x(X[i])

    # Debug point 1: Verifica stato iniziale
    qc_init = qc.copy()
    qc_init.measure_all()
    print("Stato iniziale:")
    execute_and_print(qc_init)

    for i, qx in enumerate(reversed(X)):
        print(f"\n--- Iterazione {i} ---")

        # Debug point 2: Prima di cx
        qc_pre_cx = qc.copy()
        qc_pre_cx.measure_all()
        print(f"Prima di cx {i}:")
        execute_and_print(qc_pre_cx)

        qc.cx(qx, C)

        # Debug point 3: Dopo cx
        qc_post_cx = qc.copy()
        qc_post_cx.measure_all()
        print(f"Dopo cx {i}:")
        execute_and_print(qc_post_cx)

        # Moltiplicazione modulare
        qc.append(
            const_mod_mult4(C, X_MULT, A, B, CARRY, N, T, n, a),
            C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
        )

        # Debug point 4: Dopo moltiplicazione
        qc_post_mult = qc.copy()
        qc_post_mult.measure_all()
        print(f"Dopo moltiplicazione {i}:")
        execute_and_print(qc_post_mult)

        qc.swap(X_MULT, B)

        # Debug point 5: Dopo swap
        qc_post_swap = qc.copy()
        qc_post_swap.measure_all()
        print(f"Dopo swap {i}:")
        execute_and_print(qc_post_swap)

        qc.append(
            const_mod_mult4_inv(C, X_MULT, A, B, CARRY, N, T, n, a),
            C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
        )

        # Debug point 6: Dopo inversione
        qc_post_inv = qc.copy()
        qc_post_inv.measure_all()
        print(f"Dopo inversione {i}:")
        execute_and_print(qc_post_inv)

        qc.cx(qx, C)

    return qc


def execute_and_print(qc):
    backend = AerSimulator()
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=1024)
    result = job.result()
    counts = result.get_counts(qc)
    print(counts)


# Test con valori specifici
n = 15
a = 7
x_val = 3

# Crea i registri quantistici
X = QuantumRegister(4, "x")
C = QuantumRegister(1, "control")
X_MULT = QuantumRegister(4, "x_mult")
A = QuantumRegister(4, "a")
B = QuantumRegister(4, "b")
CARRY = QuantumRegister(5, "carry")
N = QuantumRegister(4, "n")
T = QuantumRegister(1, "t")

# Esegui il debug
qc_debug = debug_const_mod_exp4(X, C, X_MULT, A, B, CARRY, N, T, n, a, x_val)
