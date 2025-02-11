import matplotlib.pyplot as plt
from experiment.qiskit_experiment import QiskitExperiment
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram

# Build quantum circuit
circuit = QuantumCircuit(1,1)
circuit.h(0)
circuit.measure(0,0)

# Simulate circuit
experiment = QiskitExperiment()
result = experiment.run(circuit, 1024)

plot_histogram(result.get_counts())
plt.draw()

# Draw circuit
circuit.draw(output="mpl")
plt.show()