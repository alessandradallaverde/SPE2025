# SPE2025

## Basic Network (v. 1)
- Simpy is used to simulate concurrent processes (nodes).
- Each node is identifiable by id and holds a list of all its peers.
- Crashed nodes don't process messages.
- Basic ring and bully election simulation set to tolerate one initiator (the first node that detects coordinator crash) and network delays.

### TODO
- [x] Modify algorithms to support multiple initiators.
- [x] Modify algorithms to tolerate multiple crashes happening during election.
- [x] Modify algorithms to tolerate packet loss (**violate reliable links requirement**).
- [x] Modify bully algorithm to deal with unpredictable message delays message (**violate synchronous system requirement**).
- [x] (Optional) Test what happens when there are nodes with the same id (**violate node identifiability requirement**).