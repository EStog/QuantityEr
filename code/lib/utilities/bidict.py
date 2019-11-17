class Bidict(dict):
    """
    A bijective dictionary. This means that the following invariant always
    hold for any bijective dictionary d:
    d[x] = y if and only if d.sym[y] = x where d.sym is the same dictionary but with
    keys as values and values as keys.
    For example:
        >>> d = Bidict({'a': 1, 'b': 2, 'c': 3})
        >>> assert d.sym == {1: 'a',2: 'b', 3: 'c'}


    If a dictionary which is not injective is given to the constructor, some of the repeated elements will be
    erased until there is only one:
        >>> d = Bidict({'item1': 4, 'item2': 4, 'item3': 5})
        >>> assert len(d) == len(d.sym) == 2
        >>> d.sym.update({5: 'other'})
        >>> assert len(d) == len(d.sym) == 2
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self)
        self._sym = self.__new__(self.__class__)
        self._sym._sym = self
        for key, value in dict(*args, **kwargs).items():
            if value not in self.sym:
                self[key] = value

    @property
    def sym(self):
        """
        >>> d = Bidict()
        >>> assert d is d.sym.sym
        >>> assert d.sym is d.sym.sym.sym
        """
        return self._sym

    def __repr__(self):
        """
        >>> d = Bidict({1:2, 3:4})
        >>> assert repr(d) == str(d) == 'BiDict({1: 2, 3: 4})'
        >>> assert repr(d.sym) == str(d.sym) == 'BiDict({2: 1, 4: 3})'
        """
        return f'{self.__class__.__name__!s}({dict(self)!r})'

    def __setitem__(self, key, value):
        """
        >>> d = Bidict()
        >>> d['one'] = 'two'
        >>> assert d['one'] == 'two'
        >>> assert d.sym['two'] == 'one'
        >>> d.sym['three'] = 'four'
        >>> assert d.sym['three'] == 'four'
        >>> assert d['four'] == 'three'
        >>> d['four'] = 4
        >>> assert d.sym[4] == 'four'
        >>> assert 'three' not in d.sym
        >>> d.sym[4] = 1
        >>> assert d[1] == 4
        >>> assert 'four' not in d
        >>> assert d == {'one':'two', 1:4}
        >>> assert d.sym == {'two': 'one', 4:1}
        """
        if key in self:
            old_value = self[key]
            dict.__delitem__(self._sym, old_value)
        if value in self._sym:
            old_key = self._sym[value]
            dict.__delitem__(self, old_key)
        dict.__setitem__(self, key, value)
        dict.__setitem__(self._sym, value, key)

    def __delitem__(self, key):
        """
        >>> d = Bidict({'blue':'red', 'wrong':'right'})
        >>> del d['wrong']
        >>> assert d == {'blue':'red'}
        >>> assert d.sym == {'red':'blue'}
        >>> del d.sym['red']
        >>> assert d.sym == d == {}
        """
        value = self[key]
        dict.__delitem__(self, key)
        dict.__delitem__(self._sym, value)

    def update(self, *args, **kwargs):
        """
        >>> d = Bidict({'one':'two', 'four':'three'})
        >>> d.update({'other':'more', 'last':'first', })
        >>> assert d == {'other':'more', 'last':'first', 'one':'two', 'four':'three'}
        >>> assert d.sym == {'more':'other', 'first':'last', 'two':'one', 'three':'four'}
        >>> d.sym.update({'more':2, 3:4})
        >>> assert d.sym  == {'more':2, 'first':'last', 'two':'one', 'three':'four', 3:4}
        >>> assert d == {2:'more', 'last':'first', 'one':'two', 'four':'three', 4:3}
        """
        for key, values in dict(*args, **kwargs).items():
            self[key] = values

    def pop(self, *args, **kwargs):
        """
        >>> d = Bidict({'a':'b', 'x':'y'})
        >>> assert d.pop('a') == 'b'
        >>> assert d.sym == {'y':'x'}
        >>> assert d.sym.pop('y') == 'x'
        >>> assert d == d.sym == {}
        >>> assert d.pop('any', None) is None
        >>> assert d.sym.pop('other', 'blank') == 'blank'
        """
        value = dict.pop(self, *args, **kwargs)
        try:
            dict.__delitem__(self._sym, value)
        except KeyError:
            pass  # in case a default was given and the element was not found in the mains dictionary, then do nothing
        return value

    def setdefault(self, key, default=None):
        """
        >>> d = Bidict({'a':'b', 'b':'c', 'x':'y'})
        >>> assert d.setdefault('a', True) == 'b'
        >>> assert d.setdefault('z', 3) == 3
        >>> assert d == {'a':'b', 'b':'c', 'x':'y', 'z':3}
        >>> assert d.sym == {'b':'a', 'c':'b', 'y':'x', 3:'z'}
        >>> assert d.sym.setdefault('y', 3) == 'x'
        >>> assert d.sym.setdefault('s', 'z') == 'z'
        >>> assert d == {'a': 'b', 'b': 'c', 'x': 'y', 'z': 's'}
        >>> assert d.sym == {'b': 'a', 'c': 'b', 'y': 'x', 's': 'z'}
        """
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def popitem(self):
        """
        >>> d = Bidict({'a':'b', 'b':'c', 'x':'y'})
        >>> assert d.popitem() == ('x', 'y')
        >>> assert d.sym.popitem() == ('c', 'b')
        >>> assert d == {'a':'b'}
        >>> assert d.sym == {'b':'a'}
        """
        key, value = dict.popitem(self)
        dict.__delitem__(self._sym, value)
        return key, value

    def clear(self):
        """
        >>> d =  Bidict({'a':'b', 'b':'c', 'x':'y'})
        >>> d.clear()
        >>> assert d == d.sym == {}
        >>> d =  Bidict({'a':'b', 'b':'c', 'x':'y'})
        >>> d.sym.clear()
        >>> assert d == d.sym == {}
        """
        dict.clear(self)
        dict.clear(self._sym)

    def copy(self):
        """
        >>> d =  Bidict({'a':'b', 'b':'c', 'x':'y'})
        >>> copy = d.copy()
        >>> assert isinstance(copy, Bidict)
        >>> assert copy == d
        >>> assert copy.sym == d.sym
        >>> copy[1] = 2
        >>> assert copy != d
        >>> assert copy.sym != d
        """
        return self.__class__(self)
