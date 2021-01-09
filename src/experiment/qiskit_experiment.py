"""
This class can be used as a basic framework for a Qiskit Experiment.
"""
from qiskit import execute, Aer, IBMQ
from quantuminspire.qiskit import QI

__author__ = "Maarten Lips"

import os
from getpass import getpass

from quantuminspire.credentials import load_account, get_token_authentication, get_basic_authentication

QI_EMAIL = os.getenv('QI_EMAIL')
QI_PASSWORD = os.getenv('QI_PASSWORD')
QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')

def get_authentication(B):
    if B == 'QI':
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
    elif B == 'IBMQ':
        print('Enter IBMQ token:')
        ibmq_token = input()
        return IBMQ.enable_account(ibmq_token)

def _setup(B):
    if B == 'QI':
        authentication = get_authentication(B)
        QI.set_authentication(authentication, QI_URL)
        sim_backend = QI.get_backend('QX single-node simulator')
        
    elif B == 'LOCAL':
        sim_backend = Aer.get_backend('qasm_simulator')
        
    elif B == 'IBMQ':
        provider = get_authentication(B)
        sim_backend = provider.get_backend('ibmq_qasm_simulator')
    return sim_backend


class QiskitExperiment():        
    def __init__(self):
        print('\n\nChoose backend:')
        print('LOCAL: local qasm simulator,')
        print('IBMQ: qasm simulator at IBMQ,')
        print('QI: QX single-node qasm simulator at Quantum Inspire')
        while True:
            try:
                backend = str(input())
                if backend == 'LOCAL' or backend == 'QI' or backend == 'IBMQ':
                    self.sim_backend = _setup(backend)
                else:
                    raise ValueError
                break
            except ValueError:
                print('Please choose LOCAL, IBMQ or QI')
        

    def run(self, circuit, shots, optimization=1):
        qi_job = execute(circuit, backend=self.sim_backend, shots=shots, optimization_level=optimization)
        return qi_job.result()
