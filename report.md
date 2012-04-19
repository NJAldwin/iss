Final Project Report
====================

Eric Chin & Nick Aldwin

1. Design
    1. Data Structures
    2. Pipelining
    3. Hazards
2. Development
    1. Initial Data Path
    2. Pipelining
    3. Forwarding
3. Results


1. Design
=========

Data Structures
---------------

Planning for this project, we decided to follow the data flow shown in the
various diagrams in the textbook.  To this end, we opted to use several
structures to maintain pipeline registers, which provide natural divisions
in the logic of our simulator.

We chose also to represent the six instructions--_add_, _addi_, _beq_, _j_,
_lw_, and _sw_--with corresponding structures, which we use to store
individual instructions throughout the pipeline.


Pipelining
----------

Because of the design of our pipelining data structures, we found it
relatively simple and feasible to design the pipeline according to the
five separate pipeline stages (fetch, decode, execute, memory, writeback).


Hazards
-------

Likewise, in handling data and control hazards, we found that our pipeline
design was conducive to implementing hazard handling.  Because of our
iterative approach, however, we found a caveat: we needed to reverse the
order of the evaluation of the stages in order to ensure that data required
to resolve the hazard is available.



2. Development
==============

Initial Data Path
-----------------

When developing the intial data path, we adhered to our initial data design
and added the logic necessary for the evaluation of each pipeline stage.


Pipelining and Forwarding
-------------------------

While we encountered a few semantic difficulties in implementing pipelining
and forwarding, we added a number of rigorous debugging measures to find
the root of our problems (e.g. incorrect value forwarded).  We diagnosed
most of these bugs using a textual version of the waterfall diagram
introduced to us in class, which allowed us to step through the simulation
to inspect the pipeline. 


3. Results
==========

Our results match those provided in the solution without deviation, which 
confirms for us the accuracy of our simulator.
