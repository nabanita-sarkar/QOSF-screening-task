
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, transpile
from qiskit.circuit.library.standard_gates import CPhaseGate
from numpy import pi
import operator


def qft(qc, reg):
    for k in range(reg.size - 1, -1, -1):
        qc.h(reg[k])
        for i in range(k):
            qc.cp(pi / 2 ** (k - i), reg[i], reg[k])
    return qc


def i_qft(qc, reg):
    for k in range(reg.size):
        for i in range(k - 1, - 1, -1):
            qc.cp(- (pi / 2 ** (k - i)), reg[i], reg[k])
        qc.h(reg[k])
    return qc


def get_binary(num1, num2):
    num1_bin = bin(num1)[2:]
    num2_bin = bin(num2)[2:]

    if(len(num1_bin) > len(num2_bin)):
        length = len(num1_bin) + 1
    elif(len(num1_bin) == len(num2_bin)):
        length = len(num1_bin) + 1
    else:
        length = len(num2_bin) + 1
    return num1_bin.zfill(length), num2_bin.zfill(length)


def rotate(target_reg, control_reg, n, super_control_reg, z, qc):
    for j_val in range(n):
        for i_val in range(2 * n):
            theta = pi / 2**(i_val - j_val - z)
            ccp = CPhaseGate(theta).control(1)
            qc.append(ccp, [super_control_reg[z], control_reg[j_val], target_reg[i_val]])
    return qc


def prepare_qubit(qc, reg, binary):
    rev = binary[::-1]
    for pos, i in enumerate(rev):
        if(i == '1'):
            qc.x(reg[pos])
    return qc


def binary_to_decimal(binary):
    return int('0b' + binary, 2)


def multiply(num1, num2):
    num1_bin, num2_bin = get_binary(num1, num2)

    n = len(num1_bin) - 1

    a = QuantumRegister(n, 'a')
    b = QuantumRegister(n, 'b')

    ab = QuantumRegister(2 * n, 'ab')
    cr = ClassicalRegister(2 * n, 'output')

    qc = QuantumCircuit(b, a, ab, cr)

    qc = prepare_qubit(qc, a, num1_bin)
    qc = prepare_qubit(qc, b, num2_bin)

    qc = qft(qc, ab)

    for z in range(n):
        qc = rotate(ab, a, n, b, z, qc)

    qc = i_qft(qc, ab)

    for i in range(2 * n):
        qc.measure(ab[i], cr[i])
    qc.draw()

    simulator = Aer.get_backend('aer_simulator')

    circ = transpile(qc, simulator)

    result = simulator.run(circ).result()
    counts = result.get_counts(circ)

    output_binary = max(counts.items(), key=operator.itemgetter(1))[0]

    return binary_to_decimal(output_binary)


num1 = 22
num2 = 7
print(multiply(num1, num2))
