# Module:   unrepr
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au
#
# NOTE:     Borrowed from CherryPy3
#
# Borrowed from sahriswiki (https://sahriswiki.org/)
# with permission from James Mills, prologic at shortcircuit dot net dot au


"""unrepr

unrepr(...) function and support borrowed from the CherryPy3 library
with fixes and improvements.
"""


# public domain "unrepr" implementation, found on the web and then improved.


import sys
import operator as _operator


class _Builder:

    def build(self, o):
        m = getattr(self, 'build_' + o.__class__.__name__, None)
        if m is None:
            raise TypeError("unrepr does not recognize %s" %
                            repr(o.__class__.__name__))
        return m(o)

    def build_Subscript(self, o):
        return self.build(o.value)[self.build(o.slice)]

    def build_Index(self, o):
        return self.build(o.value)

    def build_Call(self, o):
        callee = self.build(o.func)

        if o.args is None:
            args = ()
        else:
            args = tuple([self.build(a) for a in o.args])

        if o.starargs is None:
            starargs = ()
        else:
            starargs = self.build(o.starargs)

        if o.kwargs is None:
            kwargs = {}
        else:
            kwargs = self.build(o.kwargs)

        return callee(*(args + starargs), **kwargs)

    def build_List(self, o):
        return list(map(self.build, o.elts))

    def build_Str(self, o):
        return o.s

    def build_Num(self, o):
        return o.n

    def build_Dict(self, o):
        return dict([(self.build(k), self.build(v))
                     for k, v in zip(o.keys, o.values)])

    def build_Tuple(self, o):
        return tuple(self.build_List(o))

    def build_Name(self, o):
        name = o.id
        if name == 'None':
            return None
        if name == 'True':
            return True
        if name == 'False':
            return False

        # See if the Name is a package or module. If it is, import it.
        try:
            return modules(name)
        except ImportError:
            pass

        # See if the Name is in __builtins__.
        try:
            return getattr(__builtins__, name)
        except AttributeError:
            pass

        raise TypeError("unrepr could not resolve the name %s" % repr(name))

    def build_BinOp(self, o):
        left, op, right = map(self.build, [o.left, o.op, o.right])
        return op(left, right)

    def build_Add(self, o):
        return _operator.add

    def build_Attribute(self, o):
        parent = self.build(o.value)
        return getattr(parent, o.attr)

    def build_NoneType(self, o):
        return None


def _astnode(s):
    """Return a Python ast Node compiled from a string."""
    try:
        import ast
    except ImportError:
        # Fallback to eval when ast package is not available,
        # e.g. IronPython 1.0.
        return eval(s)

    p = ast.parse("__tempvalue__ = " + s)
    return p.body[0].value


def unrepr(s):
    """Return a Python object compiled from a string."""
    if not s:
        return s
    obj = _astnode(s)
    return _Builder().build(obj)


def modules(modulePath):
    """Load a module and retrieve a reference to that module."""
    try:
        mod = sys.modules[modulePath]
        if mod is None:
            raise KeyError()
    except KeyError:
        # The last [''] is important.
        mod = __import__(modulePath, globals(), locals(), [''])
    return mod
