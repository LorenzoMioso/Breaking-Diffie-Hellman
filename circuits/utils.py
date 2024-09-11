from qiskit import transpile
from qiskit_aer import AerSimulator


def run_circuit(qc):
    backend = AerSimulator()
    qc_compiled = transpile(qc, backend, optimization_level=3)
    job_sim = backend.run(qc_compiled, shots=1024)
    result_sim = job_sim.result()
    counts = result_sim.get_counts(qc_compiled)
    # print(counts)
    if len(counts) > 1:
        print("WARNING: More than one result")
    res = next(iter(counts))
    # remove the spaces
    res = res.replace(" ", "")
    return res
