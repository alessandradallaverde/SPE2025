# SPE2025

## Basic Network (v. 0)
- Each node is identifiable by id and holds a list of all its peers.
- Crashed nodes don't process messages.
- Nodes have no async capability.
- There is a message queue and basic **receive()**, **send()** and **multicast()** commands. 
- Basic logging capability added.
- Simulation starts when a node detects crash of coordinator by calling method  **start_bully_election()** or **start_ring_election()**.

### TODO
- Add an event system to simulate asynchronicity of nodes.
- Account for network delays.
- Upgrade message handling system to deal with async events.