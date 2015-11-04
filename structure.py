"""

Inspect the structure of Python objects

(c) Jason Utt

"""


import re


__all__ = ['structure', 'typedfunc']


atomic_types    = {str, unicode, int, float, type(int), bool}
container_types = {list, tuple, set, dict}



def type_name(t):
    """
    Extract type/class name from its __str__ representation
    """
    type_str_pat = re.compile(r"""<(?:type|class) '(?:.*\.)?(.+)'>""")
    return type_str_pat.sub(r'\1', str(t))

def robust_func_eq(f, args, out):
    """
    Test if f applied to *args yields out
    """
    try:
        return f(*args)==out
    except:
        return False

def inspect_container(seq):
    """
    Get the structure of a container-type object
    """
    value_types = set()
    if hasattr(seq, "iteritems"):
        res = "dict(%s)"
        for k, v in seq.iteritems():
            value_types.add((structure(k), structure(v)))
        res = res % ", ".join(map(":".join, value_types))
    elif type(seq) is tuple:
        res = "tuple(%s)"
        value_types = []
        for val in seq:
            value_types.append(structure(val))
        res = res % ", ".join(value_types)
    else:
        res = type_name(type(seq)) + "(%s)"
        for val in seq:
            value_types.add(structure(val))
        res = res % ", ".join(value_types)
    return res

def structure(x):
    """
    Get the structure of object x
    """
    typex = type(x)
    if typex in atomic_types:
        return type_name(typex)
    if typex in container_types:
        return inspect_container(x)
    if hasattr(x, "__call__"):
        try:
            intype = x.__instructure__
            outtype = x.__outstructure__
            ftype = "func(%s -> %s)" % (intype, outtype)
        except:
            ftype = "function"
        return ftype
    return type_name(typex)


def dict_structure(d):
    assert hasattr(d, "iteritems")
    return dict((k, structure(v)) for k, v in d.iteritems())

def typedfunc(inkind, outkind):
    """
    A decorator for functions
    
    inkind, outkind can be:
        type / value / str
    """
    def decorator(f):
        if type(inkind) is type:
            assert type(outkind) is type
            # 1) types were specified
            # we interpret this as meaning these are the "i/o-types"
            # i.e. *not* the values
            f.__instructure__  = type_name(inkind)
            f.__outstructure__ = type_name(outkind)
        elif type(inkind) is str:
            assert type(outkind) is str
            # 2) strings were specified
            # we interpret this as meaning these are the designations
            # to be given as the function's structure
            f.__instructure__  = inkind
            f.__outstructure__ = outkind
        else:
            # 3) "values" were specified
            # we interpret this as meaning these are i/o-values
            # this means a) their structure defines the function's
            # structure, and b) we can test if the function actually
            # returns the out-value for the specified in-value
            indata = inkind
            outdata = outkind
            
            tested = False
            try:
                assert robust_func_eq(f, indata, outdata)
                f.__instructure__  = structure(indata)
                tested = True
                passed = True
            except AssertionError:
                passed = False
                tested = True
            if not passed or not tested:
                try:
                    indata_tuple = (indata,)
                    assert robust_func_eq(f, indata_tuple, outkind)
                    f.__instructure__  = structure(indata)
                    tested = True
                    passed = True
                except AssertionError:
                    tested = True
                    passed = False
            assert tested and passed, "calculated output does not match specified %s" % f
            f.__outstructure__ = structure(outkind)
        return f
    return decorator


def test():
    print structure(({1:"asd", ("word",1,2,1):structure, "asdf".decode("utf8"):1.3, 1.2:{1:[]}, 1.3:set(["asd", "asdf".decode("utf8")])}, "hi!"))
    print structure(structure)
    print
    print structure(unicode())
    print structure("asdf".decode("utf8"))
    print structure({123:"asdf".decode("utf8")})
    print structure(set(["asd", "asd".decode("utf8")]))
    print set(["asd", "asd".decode("utf8")])

if __name__ == '__main__':
    test()
