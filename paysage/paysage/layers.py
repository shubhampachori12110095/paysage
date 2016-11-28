import numpy
from scipy.stats import bernoulli
from scipy.special import expit


#----- LAYER CLASSES -----#

class Layer(object):

    def __init__(self, length):
        self.len = length
        
    def prox(self, vis):
        pass
        
    def update_params(self, *args):
        pass
    
    def mean(self):
        pass
    
    def partition_function(self):
        pass
    
    def sample_state(self):
        pass


class GaussianLayer(Layer):
    
    def __init__(self, length):
        super().__init__(length)
        self.loc = numpy.zeros(self.len, dtype=numpy.float32)
        self.scale = numpy.ones(self.len, dtype=numpy.float32)
        
    def prox(self, vis):
        return vis
        
    def update_params(self, *args):
        self.loc[:] = args[0]
        self.scale[:] = args[1]
        
    def mean(self):
        return self.loc
        
    def partition_function(self):
        return 1 / self.scale
    
    def sample_state(self):
        return self.loc + self.scale * numpy.random.normal(loc=0.0, scale=1.0, size=self.loc.shape)


class IsingLayer(Layer):

    def __init__(self, length):
        super().__init__(length)
        self.loc = numpy.zeros(self.len, dtype=numpy.int8)
        
    def prox(self, vis):
        return 2 * (vis > 0).astype(numpy.int8) - 1

    def update_params(self, *args):
        self.loc[:] = args[0]
        
    def mean(self):
        return numpy.tanh(self.loc)
        
    def partition_function(self):
        return numpy.cosh(self.loc)

    def sample_state(self):
        return 2 * bernoulli.rvs(expit(self.loc)) - 1
        
        
class BernoulliLayer(Layer):
    
    def __init__(self, length):
        super().__init__(length)
        self.loc = numpy.zeros(self.len, dtype=numpy.int8)
        
    def prox(self, vis):
        return (vis > 0).astype(numpy.int8)
        
    def update_params(self, *args):
        self.loc[:] = args[0]
        
    def mean(self):
        return expit(self.loc)
        
    def partition_function(self):
        return 1.0 + numpy.exp(self.loc)
        
    def sample_state(self):
        return bernoulli.rvs(expit(self.loc))


class ExponentialLayer(Layer):

    def __init__(self, length):
        super().__init__(length)
        self.loc = numpy.ones(self.len, dtype=numpy.float32)
        
    def prox(self, vis):
        return vis.clip(min=0.0)
        
    def update_params(self, *args):
        self.loc[:] = args[0]
        
    def mean(self):
        return 1.0 / self.loc
        
    def partition_function(self):
        return 1.0 / self.loc

    def sample_state(self):
        return numpy.random.exponential(self.loc)
        
        
# ---- FUNCTIONS ----- #
        
def get(key):
    if 'gauss' in key.lower():
        return GaussianLayer
    elif 'ising' in key.lower():
        return IsingLayer
    elif 'bern' in key.lower():
        return BernoulliLayer
    elif 'expo' in key.lower():
        return ExponentialLayer
    else:
        raise ValueError('Unknown layer type')
