import numpy, torch
from multipledispatch import dispatch

EPSILON = numpy.finfo(numpy.float32).eps

# ----- TENSORS ----- #

def to_numpy_array(tensor):
    return tensor.numpy()

def float_scalar(scalar):
    return numpy.float32(scalar)

def float_tensor(tensor):
    return torch.FloatTensor(tensor)

def shape(tensor):
    return tuple(tensor.size())

def ndim(tensor):
    return tensor.ndimension()

def transpose(tensor):
    return tensor.t()

def zeros(shape):
    return torch.zeros(shape)

def zeros_like(tensor):
    return zeros(shape(tensor))

def ones(shape):
    return torch.ones(shape)

def ones_like(tensor):
    return ones(shape(tensor))

def diag(mat):
    return mat.diag()

def diagonal_matrix(vec):
    return torch.diag(vec)

def identity(n):
    return torch.eye(n)

def fill_diagonal(mat, val):
    for i in range(len(mat)):
        mat[i,i] = val

def sign(tensor):
    return tensor.sign()

def clip(tensor, a_min=-numpy.inf, a_max=numpy.inf):
    return tensor.clamp(a_min, a_max)

def clip_inplace(tensor, a_min=-numpy.inf, a_max=numpy.inf):
    return tensor.clamp_(a_min, a_max)

def tround(tensor):
    return tensor.round()

def flatten(tensor):
    return tensor.view(int(numpy.prod(shape(tensor))))

def reshape(tensor, newshape):
    return tensor.view(*newshape)

def dtype(tensor):
    raise tensor.type()


######################

"""
Routines for matrix operations

"""

def mix_inplace(w,x,y):
    """
        Compute a weighted average of two matrices (x and y) and store the results in x.
        Useful for keeping track of running averages during training.

        x <- w * x + (1-w) * y

    """
    x.mul_(w)
    x.add_(y.mul(1-w))

def square_mix_inplace(w,x,y):
    """
        Compute a weighted average of two matrices (x and y^2) and store the results in x.
        Useful for keeping track of running averages of squared matrices during training.

        x < w x + (1-w) * y**2

    """
    x.mul_(w)
    x.add_(y.mul(y).mul(1-w))

def sqrt_div(x,y):
    """
        Elementwise division of x by sqrt(y).

    """
    return x.div_(torch.sqrt(EPSILON + y))

def normalize(x):
    """
        Divide x by it's sum.

    """
    return x.div(torch.sum(EPSILON + x))


# ----- THE FOLLOWING FUNCTIONS ARE THE MAIN BOTTLENECKS ----- #

def norm(x):
    return x.norm()

def tmax(x, axis=None, keepdims=False):
    if axis is not None:
        tmp = torch.max(x, dim=axis)[0]
        if keepdims:
            return tmp
        else:
            return flatten(tmp)
    else:
        return torch.max(x)

def tmin(x, axis=None, keepdims=False):
    if axis is not None:
        tmp = torch.min(x, dim=axis)[0]
        if keepdims:
            return tmp
        else:
            return flatten(tmp)
    else:
        return torch.min(x)

def mean(x, axis=None, keepdims=False):
    if axis is not None:
        tmp = torch.mean(x, dim=axis)
        if keepdims:
            return tmp
        else:
            return flatten(tmp)
    else:
        return torch.mean(x)

def var(x, axis=None, keepdims=False):
    if axis is not None:
        tmp = torch.var(x, dim=axis)
        if keepdims:
            return tmp
        else:
            return flatten(tmp)
    else:
        return torch.var(x)

def std(x, axis=None, keepdims=False):
    if axis is not None:
        tmp = torch.std(x, dim=axis)
        if keepdims:
            return tmp
        else:
            return flatten(tmp)
    else:
        return torch.std(x)

def tsum(x, axis=None, keepdims=False):
    if axis is not None:
        tmp = torch.sum(x, dim=axis)
        if keepdims:
            return tmp
        else:
            return flatten(tmp)
    else:
        return torch.sum(x)

def tprod(x, axis=None, keepdims=False):
    if axis is not None:
        tmp = torch.prod(x, dim=axis)
        if keepdims:
            return tmp
        else:
            return flatten(tmp)
    else:
        return torch.prod(x)

def tany(x, axis=None, keepdims=False):
    tmp = tmax(x == True, axis=axis)
    if keepdims:
        return tmp
    else:
        return flatten(tmp)

def tall(x, axis=None, keepdims=False):
    tmp = tmin(x == True, axis=axis)
    if keepdims:
        return tmp
    else:
        return flatten(tmp)

def equal(x, y):
    return torch.eq(x, y)

def allclose(x, y):
    return torch.le(torch.abs(x - y), EPSILON)

def not_equal(x, y):
    return torch.neq(x, y)

def greater(x, y):
    return torch.gt(x, y)

def greater_equal(x, y):
    return torch.ge(x, y)

def lesser(x, y):
    return torch.lt(x, y)

def lesser_equal(x, y):
    return torch.le(x, y)

def maximum(x, y):
    return torch.max(x, y)

def minimum(x, y):
    return torch.min(x, y)

def argmax(x, axis=None):
    if axis is not None:
        return torch.max(x, dim=axis)[1]
    else:
        a,b = torch.max(x, dim=0)
        index = torch.max(a, dim=1)[1]
        return b[0, index[0,0]]

def argmin(x, axis=None):
    if axis is not None:
        return torch.min(x, dim=axis)[1]
    else:
        a,b = torch.min(x, dim=0)
        index = torch.min(a, dim=1)[1]
        return b[0, index[0,0]]

def dot(a, b):
    return a @ b

def outer(x,y):
    return torch.ger(x, y)

def broadcast(vec, mat):
    return vec.unsqueeze(0).expand(mat.size(0), vec.size(0))

def affine(a,b,W):
    tmp = dot(W, b)
    tmp += broadcast(a, tmp)
    return tmp

def quadratic(a,b,W):
    return a @ W @ b

def inv(mat):
    return mat.inverse()

def batch_dot(vis, W, hid, axis=1):
    """
        Let v by a L x N matrix where each row v_i is a visible vector.
        Let h be a L x M matrix where each row h_i is a hidden vector.
        And, let W be a N x M matrix of weights.
        Then, batch_dot(v,W,h) = \sum_i v_i^T W h_i
        Returns a vector.

        The actual computation is performed with a vectorized expression.

    """
    raise NotImplementedError

def batch_outer(vis, hid):
    """
        Let v by a L x N matrix where each row v_i is a visible vector.
        Let h be a L x M matrix where each row h_i is a hidden vector.
        Then, batch_outer(v, h) = \sum_i v_i h_i^T
        Returns an N x M matrix.

        The actual computation is performed with a vectorized expression.

    """
    raise NotImplementedError

def repeat(tensor, n, axis):
    raise NotImplementedError

def stack(tensors, axis):
    raise NotImplementedError

def hstack(tensors):
    raise NotImplementedError

def vstack(tensors):
    raise NotImplementedError

def trange(start, end, step=1):
    return torch.range(start, end-1, step)


# ------------------------------------------------------------ #

# ----- SPECIALIZED MATRIX FUNCTIONS ----- #


def euclidean_distance(a, b):
    """
        Compute the euclidean distance between two vectors.

    """
    raise (a - b).norm()

def squared_euclidean_distance(a, b):
    """
        Compute the squared euclidean distance between two vectors.

    """
    return euclidean_distance(a, b)**2

def fast_energy_distance(minibatch, samples, downsample=100):
    raise NotImplementedError
