import pyjags
import numpy as np

modstr="""
model {
    for (i in 1:N) {
        x[i] ~ dnorm(mu, tau)
    }
    mu ~ dnorm(0, .0001)
    tau <- pow(sigma, -2)
    sigma ~ dunif(0, 100)
}
"""
N=1000
mu,sigma=5, .3
x=np.random.randn(N)*sigma+mu

adapt=100
burn=100
nchains=3
nsteps=500
thin=1
niter=int(np.ceil( (nsteps*thin)/float(nchains)))

data={'x':x,
      'N':N}
mod=pyjags.Model(modstr, data, nchains=nchains, inits={'mu':np.mean(x), 'sigma':np.std(x)})
mod.burnin(100)
ms=mod.sample(niter=niter, thin=thin)
print "Real mu (sigma)=%.2f (%.2f)"%(mu, sigma)
print "Estimated (means):"
print np.mean(ms,0)
print "Estimated (5-95 percentile):"
print np.percentile(ms, q=[5,95], axis=0).T

print mod.gelman_diagnostic()
print mod.dic()