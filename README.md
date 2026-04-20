<h1 align="center">Bully and Ring Election Algorithms Performance Analysis Considering Real Case Aspects</h1>
<p align="center"><em>Project of the Simulation and Performance Evaluation Course (2025)</em></p>

## Table of Contents

- [About the Project](#about-the-project)
- [Project Description](#project-description)
- [Repository Organization](#repository-organization)
  - [Python Source Code](#python-source-code)
    - [Project's Dependencies](#projects-dependencies)
  - [Report and Latex Source Code](#report-and-latex-source-code)
- [References](#references)

# About the Project
The repository contains the source code of the **Simulation and Performance
Evaluation course** project. The project's title is *Bully and Ring Election
Algorithms Performance Analysis Considering Real Case Aspects*. The next
sections will describe the aim of this work and how to navigate the repository.

# Project Description
Many papers in the distributed systems field analyze the **performance of
classical election algorithms**. However, they do not consider real case
scenarios, e.g., propagation delays, and different metrics other than
computational complexity.  
Therefore, the project simulates two relevant election algorithms: the **Bully**
algorithm [1] and the **Ring** algorithm [2], described in the book
*Distributed Systems* by M. van Steen and A. S. Tanenbaum [3]. Then, we
**compare the two algorithms** with two metrics: the **turnaround time**, i.e.,
the time
the network takes to reach consensus on the new coordinator, and the **number
of messages** exchanged during the election. In addition, we stress the two
algorithms under real case aspects, as **communication delays** and **links
failures**, e.g., lost packets. To support this last feature, we developed a new
version of the two algorithms with timeouts. 

# Repository Organization
This section describes the repository's organization.

## Python Source Code
The `code` folder contains the **Python source code** of the project.
Its **structure** is the following:
- `election`: folder containing the simulation core of the Bully and Ring
algorithms
- `msg`: folder containing the classes of the messages exchanged during the
election
- `node`: folder containing the network nodes implementation
- `statistic`: folder containing the file `statistic.py` that contains the
class used to plot and collect the metrics measurements
- `main.py`: contains the code of all the experiments described in the report
- `utils.py`: contains statistic utility functions

> [!IMPORTANT]
> To run the code, run the file `main.py`.

### Project's Dependencies
As we said, the code is written in **Python**. The framework used for the
simulations is **SimPy**. A part from this library, the project has the
following **dependencies**:
- numpy
- matplotlib
- scipy

> [!NOTE]
> We used SciPy 4.1.1 that requires at least Python 3.8.

## Report and Latex Source Code
The `report` folder contains the **Latex source code** of the final report (IEEE
standard) and the file `SPE_report.pdf`, containing the compiled **documentation**.<br>
It may be useful to first give a **contents overview** of this paper:
1.  **Introduction**: gives a brief introduction about the project and its goal
2.  **Assumptions**: analyzes the theoretical assumptions of the Ring and Bully
algorithms
3.  **Implementation choices**: describes the framework employed to implement
the election algorithms
4.  **Performance Analysis**: describes the Monte Carlo simulations and the
metrics chosen for the comparison
5.  **Results**: shows the results of the simulations
6.  **Conclusion**: highlights the fundamental results and the advantages of
the election algorithm choice

# References
[1] H. Garcia-Molina, Elections in a Distributed Computing System, IEEE Tr.
on Comp., Vol. C-31, NO. 1, Jan. 1982.  
[2] E.J.H.Chang and R.Roberts, An improved algorithm for decentralized
extremal finding in circular configurations of processes, Communications of the
ACM, vol. 22, no. 5, pp. 281–283, 1979.  
[3] M. van Steen and A. S. Tanenbaum, Distributed Systems, 4th ed., Version
4.03, Jan. 2025, ch. 5, sec. 5.4.2.