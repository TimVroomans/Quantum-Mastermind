"""
This class can be used as a basic framework for a Qiskit Experiment.
"""
from qiskit import execute
from quantuminspire.qiskit import QI

__author__ = "Maarten Lips"

import os
from getpass import getpass

from quantuminspire.credentials import load_account, get_token_authentication, get_basic_authentication

QI_EMAIL = os.getenv('QI_EMAIL')
QI_PASSWORD = os.getenv('QI_PASSWORD')
QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')


def get_authentication():
    """ Gets the authentication for connecting to the Quantum Inspire API."""
    token = load_account()
    if token is not None:
        return get_token_authentication(token)
    else:
        if QI_EMAIL is None or QI_PASSWORD is None:
            print('Enter email:')
            email = input()
            print('Enter password')
            password = getpass()
        else:
            email, password = QI_EMAIL, QI_PASSWORD
        return get_basic_authentication(email, password)


def _setup():
    authentication = get_authentication()
    QI.set_authentication(authentication, QI_URL)
    qi_backend = QI.get_backend('QX single-node simulator')

    return qi_backend


class QiskitExperiment:
    def __init__(self):
        self.qi_backend = _setup()

    def run(self, circuit, shots, optimization=1):
        qi_job = execute(circuit, backend=self.qi_backend, shots=shots, optimization_level=optimization)
        return qi_job.result()
