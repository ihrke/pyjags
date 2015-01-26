"""
Ugly as hell wrapper to access JAGS from python.
It uses `rpy` to access `JAGS` via `R` (did I mention how ugly this is?).

WARNING: No protection whatsoever! It happily passes variables back 
and forth between R and python without checking for overwriting them etc.

- Don't attempt to use multiple models in the same program 
  (simultaneously, one after the other is ok)
- the code will mess with rpy2's R instance, i.e., if you run R-magics, 
  the environment is changed by this code
  
Requirements:

- JAGS
- R
- rjags (R package)
- rpy2 (python package)
"""
import numpy as np
import tempfile
from IPython.utils.io import capture_output
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
import rpy2.robjects as robj
import pandas.rpy.common as com



_R_init="""
library(rjags)
source('rjags_coda_samples_dic.R')
"""

_R_build_model="""
pyjags_mod=jags.model("{fname}", data=pyjags_data, 
            n.chains={nchains}, n.adapt={adapt}, 
            quiet=TRUE, inits=pyjags_inits)
"""

_R_burnin="""
update(pyjags_mod, n.iter={niter}, progress.bar="none")
"""

_R_sample_dic="""
pyjags_samp=coda.samples.dic(pyjags_mod, variable.names=pyjags_variables, n.iter={niter}, 
            thin={thin}, progress.bar='none')
"""

class Model(object):  
    def __init__(self, modstr, data, inits=None, nchains=1, nadapt=0):
        """
        modstr: a string containing the jags model
        data: a dictionary of numpy arrays (or convertible by calling np.array(data[key]))
        inits: similar to data but for initial values of unobserved variables
        nchains: int (number of chains)
        nadapt: int (number of adaption steps)
        """
        self._burnin_ok=False
        self._model_fname=tempfile.mktemp()
        with open(self._model_fname, 'w') as f:
            f.write(modstr)
        with capture_output() as io:
            robj.r(_R_init)
        
        ## default conversion for list results in R-list (unnamed)
        data_keys=sorted(data.keys())
        dlist=[]
        for k in data_keys:
            dlist.append(np.array(data[k]) if not np.isscalar(data[k]) else np.array([data[k]]))
        #dlist=[np.array(data[k]) for k in data_keys]
        robj.r.assign('pyjags_data', dlist)
        robj.r.assign('pyjags_data_names', np.array(data_keys))
        robj.r('names(pyjags_data) <- pyjags_data_names')
        
        ## init
        if inits==None:
            robj.r('pyjags_inits <- NULL')
        else:
            inits_keys=sorted(inits.keys())
            dlist=[]
            for k in inits_keys:
                dlist.append(np.array(inits[k]) if not np.isscalar(inits[k]) else np.array([inits[k]]))
            robj.r.assign('pyjags_inits', dlist)
            robj.r.assign('pyjags_inits_names', np.array(inits_keys))
            robj.r('names(pyjags_inits) <- pyjags_inits_names')       

        robj.r(_R_build_model.format(fname=self._model_fname,
                                     nchains=nchains,
                                     adapt=nadapt))
    def burnin(self, niter):
        robj.r(_R_burnin.format(niter=niter))
        self._burnin_ok=True
        
    def get_variables(self, which='unobserved'):
        """which: "all" or "unobserved" """
        if which=='unobserved':
            return list(robj.r("names(coef(pyjags_mod))"))
        else:
            return list(robj.r("variable.names(pyjags_mod)"))
        
    def sample(self, niter, thin=1, variables=None, run_diagnostic=True):
        """
        variables: if None, use all as extracted with self.get_variables(which='unobserved')
        """
        if not self._burnin_ok:
            print "WARNING: you might want to run burnin() first"
        if variables==None:
            variables=self.get_variables(which='unobserved')
        robj.r.assign('pyjags_variables', np.array(variables))
        
        with capture_output() as io: # get rid of some remaining output
            robj.r(_R_sample_dic.format(niter=niter,
                                        thin=thin))
    
        ## temporarily disable numpy conversion
        rpy2.robjects.numpy2ri.deactivate()
            
        if run_diagnostic:
            robj.r('pyjags_gelman=gelman.diag(pyjags_samp$samples)$psrf')
            self._gelmandiag_last_run=com.convert_robj(robj.r('pyjags_gelman'))
            if np.any(self._gelmandiag_last_run.iloc[:,0]>1.05):
                print "WARNING: there may be problems with your convergence (some R>1.05)"
        else:
            self._gelmandiag_last_run=None
        ms=com.convert_robj(robj.r('as.matrix(pyjags_samp$samples)'))        
        self._dic_last_run=com.convert_robj(robj.r('pyjags_samp$dic'))

        ## enable numpy conversion again
        rpy2.robjects.numpy2ri.activate()
        
        return ms
    
    def gelman_diagnostic(self):
        """return gelman diagnostics for last run of sample()"""
        return self._gelmandiag_last_run
    
    def dic(self):
        return self._dic_last_run