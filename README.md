# SPE2025

## Basic Network (v. 1)
- Simpy is used to simulate concurrent processes (nodes).
- Each node is identifiable by id and holds a list of all its peers.
- Crashed nodes don't process messages.
- Basic ring and bully election simulation set to tolerate one initiator (the first node that detects coordinator crash) and network delays.

### TODO
- [x] Modify ring algorithm to support multiple initiators (**done, miss testing**).
- [x] Modify bully algorithm to support multiple initiators (**done, miss testing**).
- [ ] Modify algorithms to tolerate packet loss (**bully done, further testing needed**).
- [ ] (Optional) Test what happens when there are nodes with the same id (**violate node identifiability requirement**).
