import time

from qiskit import transpile
from qiskit_aer import AerSimulator


def run_circuit(qc):
    backend = AerSimulator()
    # print(
    #    f"gate count before transpile: {qc.decompose().decompose().decompose().decompose().decompose().count_ops()}"
    # )
    # print(
    #    f"depth before transpile: {qc.decompose().decompose().decompose().decompose().decompose().depth()}"
    # )
    qc_compiled = transpile(qc, backend, optimization_level=3)
    # print(f"gate count after transpile: {qc_compiled.count_ops()}")
    # print(f"depth after transpile: {qc_compiled.depth()}")

    start_time = time.time()
    job_sim = backend.run(qc_compiled, shots=1)
    result_sim = job_sim.result()
    counts = result_sim.get_counts(qc_compiled)
    # print("--- %s seconds ---" % (time.time() - start_time))
    # print(counts)
    if len(counts) > 1:
        print("WARNING: More than one result")
    res = next(iter(counts))
    # remove the spaces
    res = res.replace(" ", "")
    return res
