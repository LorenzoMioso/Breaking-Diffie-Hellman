from qiskit import QuantumCircuit


def const_mod_exp4(X, C, X_MULT, A, B, CARRY, N, T, n, a):

    qc = QuantumCircuit(X, C, X_MULT, A, B, CARRY, N, T, name="const_mod_exp4")

    qc.barrier()

    # prepare to |1> X_MULT
    qc.x(X_MULT[0])

    for i, qx in enumerate(X):
        # qx must activate the multiplication by flipping C
        qc.cx(qx, C)
        # apply modular multiplication
        qc.append(
            const_mod_mult4(C, X_MULT, A, B, CARRY, N, T, n, a),
            C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
        )
        # swap B and X_MULT
        qc.swap(X_MULT, B)
        # apply modular multiplication inverse
        qc.append(
            const_mod_mult4_inv(C, X_MULT, A, B, CARRY, N, T, n, a),
            C[:] + X_MULT[:] + A[:] + B[:] + CARRY[:] + N[:] + T[:],
        )
        # reset C
        qc.cx(qx, C)

    return qc


def double_controlled_exp_prep(a, k):
    assert 0 <= a <= 7, "a must be a number between 0 and 7"
    assert 0 <= k <= 3, "k must be a number between 0 and 3"

    result = a * (2**k)

    qc = QuantumCircuit(6, name=f"cc_{a}*{2**k}")

    if result == 0:
        return qc  # No need to do anything for a result of 0

    # Apply CCX based on the binary representation of result
    for i in range(4 * 2):  # last 4 qubits are the target qubits
        if result & (1 << i):
            qc.ccx(0, 1, 2 + (i % 4))

    return qc


def double_controlled_exp_prep_inv(a, k):

    assert 0 <= a <= 7, "a must be a number between 0 and 7"
    assert 0 <= k <= 3, "k must be a number between 0 and 3"

    result = a * (2**k)

    qc = QuantumCircuit(6, name=f"cc_{a}*{2**k}_inv")

    if result == 0:
        return qc  # No need to do anything for a result of 0

    # Apply CCX based on the binary representation of result
    for i in reversed(range(4 * 2)):  # last 3 qubits are the target qubits
        if result & (1 << i):
            qc.ccx(0, 1, 2 + (i % 4))

    return qc


def controlled_copy4(C, A, B):

    qc = QuantumCircuit(C, A, B, name="controlled_copy4")

    qc.x(C)
    for i in range(4):
        qc.ccx(C, A[i], B[i])
    qc.x(C)

    return qc


def const_mod_mult4(C, X, A, B, CARRY, N, T, n, a):

    qc = QuantumCircuit(C, X, A, B, CARRY, N, T, name=f"mod_mult4_{a}x_mod_{n}")

    for i, qx in enumerate(X):
        qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
        qc.append(mod_addr4(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:])
        qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

    qc.append(controlled_copy4(C, X, B), C[:] + X[:] + B[:])

    return qc


def const_mod_mult4_inv(C, X, A, B, CARRY, N, T, n, a):

    qc = QuantumCircuit(C, X, A, B, CARRY, N, T, name=f"inv_mod_mult4_{a}x_mod_{n}")

    qc.append(controlled_copy4(C, X, B), C[:] + X[:] + B[:])

    for i, qx in enumerate(X):
        qc.append(double_controlled_exp_prep(a, i), [C] + [qx] + A[:])
        qc.append(
            mod_subtr4(A, B, CARRY, N, T, n), A[:] + B[:] + CARRY[:] + N[:] + T[:]
        )
        qc.append(double_controlled_exp_prep_inv(a, i), [C] + [qx] + A[:])

    return qc


def control_prepare_4(x):
    qc = QuantumCircuit(5, name=f"control_prepare_{x}")
    if x & 1:
        qc.cx(4, 0)
    if x & 2:
        qc.cx(4, 1)
    if x & 4:
        qc.cx(4, 2)
    if x & 8:
        qc.cx(4, 3)
    return qc


def mod_addr4(A, B, C, N, T, n):

    c_4 = C[4]
    t = T

    qc = QuantumCircuit(A, B, C, N, T, name="mod_addr4")

    # a + b
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
    # a + b - n
    qc.swap(A, N)
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])
    # set t to 1 if overflow
    qc.x(c_4)
    qc.cx(c_4, t)
    qc.x(c_4)
    # add n if overflow
    qc.append(control_prepare_4(n), A[:] + [t])
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
    qc.append(control_prepare_4(n), A[:] + [t])
    # go back to the original state
    qc.swap(A, N)
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])
    qc.cx(c_4, t)
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])

    return qc


def mod_subtr4(A, B, C, N, T, n):

    b_3 = B[3]
    c_4 = C[4]
    t = T

    qc = QuantumCircuit(A, B, C, N, T, name="mod_subtr4")

    # Apply the subtractor with modulus
    # b - a
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])
    qc.cx(c_4, t)
    # (b - a) + a
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
    qc.swap(A, N)
    qc.append(control_prepare_4(n), A[:] + [t])
    # (b - a) + a - n if overflow
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])
    qc.append(control_prepare_4(n), A[:] + [t])
    qc.x(c_4)
    qc.cx(c_4, t)
    qc.x(c_4)
    # (b - a) + a - n + n if overflow
    qc.append(addr4(A, B, C), A[:] + B[:] + C[:])
    qc.swap(A, N)
    #
    qc.append(subtr4(A, B, C), A[:] + B[:] + C[:])

    return qc


def addr4(A, B, C):

    a_0, a_1, a_2, a_3 = A
    b_0, b_1, b_2, b_3 = B
    c_0, c_1, c_2, c_3, c_4 = C

    qc = QuantumCircuit(A, B, C, name="addr4")

    # Apply the adder
    qc.append(carry3(), [c_0, a_0, b_0, c_1])
    qc.append(carry3(), [c_1, a_1, b_1, c_2])
    qc.append(carry3(), [c_2, a_2, b_2, c_3])
    qc.append(carry3(), [c_3, a_3, b_3, c_4])

    qc.cx(a_3, b_3)
    qc.append(sum3(), [c_3, a_3, b_3])
    qc.append(reverse_carry3(), [c_2, a_2, b_2, c_3])
    qc.append(sum3(), [c_2, a_2, b_2])
    qc.append(reverse_carry3(), [c_1, a_1, b_1, c_2])
    qc.append(sum3(), [c_1, a_1, b_1])
    qc.append(reverse_carry3(), [c_0, a_0, b_0, c_1])
    qc.append(sum3(), [c_0, a_0, b_0])

    return qc


def subtr4(A, B, C):

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


def carry3():

    qc = QuantumCircuit(4, name="carry3")
    qc.ccx(1, 2, 3)
    qc.cx(1, 2)
    qc.ccx(0, 2, 3)
    return qc


def reverse_carry3():

    qc = QuantumCircuit(4, name="reverse_carry3")
    qc.ccx(0, 2, 3)
    qc.cx(1, 2)
    qc.ccx(1, 2, 3)
    return qc


def sum3():

    qc = QuantumCircuit(3, name="sum3")
    qc.cx(0, 2)
    qc.cx(1, 2)
    return qc
