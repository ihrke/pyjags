pyjags
======

Ugly ass hell wrapper to access JAGS from python.
It uses `rpy` to access `JAGS` via `R` (did I mention how ugly this is?).

WARNING: No protection whatsoever! It happily passes variables back 
and forth between R and python without checking for overwriting them etc.

- Don't attempt to use multiple models in the same program 
  (simultaneously, one after the other is ok)
- the code will mess with rpy2's R instance, i.e., if you run R-magics, 
  the environment is changed by this code
  
Requirements:
-------------

- JAGS
- R
- rjags (R package)
- rpy2 (python package)
- ipython (python package)
