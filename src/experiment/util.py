from qiskit.visualization import plot_histogram


def show_histogram(result):
    plot_histogram(result.get_counts()).show()


def show_circuit(circuit):
    circuit.draw(output='mpl').show()


def filter_at(index, string="1"):
    def func(tup):
        (key, value) = tup
        for (i, num) in enumerate(string):
            if key[index + i] != num:
                return False
        return True

    return func


def filter_on(index, size):
    return filter_at(size - index)