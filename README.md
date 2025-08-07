# SPE2025

## Basic Network (v. 1)
- Simpy is used to simulate concurrent processes (nodes).
- Each node is identifiable by id and holds a list of all its peers.
- Crashed nodes don't process messages.
- Basic ring and bully election simulation set to tolerate one initiator (the first node that detects coordinator crash) and network delays.

### TODO
- [ ] Modify ring algorithm to support multiple initiators (**done, miss testing**).
- [ ] Modify bully algorithm to support multiple initiators.
- [ ] Modify ring algorithm to tolerate multiple crashes happening during election.
- [ ] Modify bully algorithm to tolerate multiple crashes happening during election (**done, miss testing**).
- [ ] Modify algorithms to tolerate packet loss (**violate reliable links requirement**).
- [ ] Modify bully algorithm to deal with unpredictable message delays message (**violate synchronous system requirement**).
- [ ] (Optional) Test what happens when there are nodes with the same id (**violate node identifiability requirement**).
