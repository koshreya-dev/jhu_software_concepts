# Module 1 Assignment README
Name: Shreya Kodati (skodati1)

Module Info: Module 14 Final Exam: Quantum Computation Due on 08/14/2025 at 11:59 EST

Approach: 

main.py - I implemented a quantum computing simulator that reads qubit states and quantum gate operations from the file provided in Canvas and processes them using object-oriented methods. The script parses an input file containing initial qubit amplitudes values and sequences of quantum operators, validates the probability amplitudes, applies the specified quantum gates in sequence, and runs 100 measurement experiments to show their probabilistic nature. The program prints invalid operators and normalizes throughout.
qubit.py – I implemented a Qubit class that extends the provided ComputingBit abstract class, representing quantum bits as complex NumPy column vectors. The class validates that probability amplitudes by making sure that |α|² + |β|² = 1, calculates measurement probabilities from the amplitudes, and simulates quantum measurements using binomial distribution sampling. The experiment() method uses quantum randomness by performing 100 measurements, and the str method provides clean formatting.

qoperators.py - I implemented a quantum gate system using inheritance, with SingleQubitOperator as an abstract base class that stores operator matrices and defines the operate() interface. 

paulix.py - The PauliX class implements the quantum NOT gate with the [[0,1],[1,0]] matrix. It applies the 2x2 matrix to qubit state vectors through matrix multiplication and returns new Qubit objects with the transformed quantum states.

hadamard.py - The Hadamard class implements the superposition gate with the (1/√2)[[1,1],[1,-1]] matrix. It applies the 2x2 matrix to qubit state vectors through matrix multiplication and returns new Qubit objects with the transformed quantum states.

references: I used the readings and lecture notes, as well as the documentation for numpy and random.

Known Bugs:
There are no known bugs
