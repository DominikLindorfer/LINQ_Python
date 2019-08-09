import itertools
from .core import Key, OrderingDirection
from .decorators import deprecated
from .exceptions import NoElementsError, NoMatchingElement, NullArgumentError, \
    MoreThanOneMatchingElement


class Enumerable3(object):
    """
    Could probably optimize code by inheriting from Enumerable and overwriting
    only the methods that need refactoring to support python 3. Admittedly
    code duplication here. Thought this would be OK design for separation of
    concerns since Python 3 is a distinct codebase from Python 2.
    """
    def __init__(self, data=[]):
        """
        Constructor
        ** Note: no type checking of the data elements are performed during
        instantiation. **
        :param data: iterable object
        :return: None
        """
        if not hasattr(data, "__iter__"):
            raise TypeError(
                u"Enumerable must be instantiated with an iterable object")
        self._data = data

    @property
    def data(self):
        """
        The iterable of the Enumerable instance
        :return: iterable
        """
        return self._data

    def __iter__(self):
        cache = []
        for element in self._data:
            cache.append(element)
            yield element
        self._data = cache

    def __repr__(self):
        return self._data.__repr__()

    def to_list(self):
        """
        Converts the iterable into a list
        :return: list object
        """
        return list(element for element in self)

    def count(self, predicate=None):
        """
        Returns the number of elements in iterable
        :return: integer object
        """
        if predicate is not None:
            return sum(1 for element in self.where(predicate))
        return sum(1 for element in self)

    def select(self, func=lambda x: x):
        """
        Transforms data into different form
        :param func: lambda expression on how to perform transformation
        :return: new Enumerable object containing transformed data
        """
        return Enumerable3(map(func, self))

    def sum(self, func=lambda x: x):
        """
        Returns the sum of af data elements
        :param func: lambda expression to transform data
        :return: sum of selected elements
        """
        return sum(self.select(func))

    def min(self, func=lambda x: x):
        """
        Returns the min value of data elements
        :param func: lambda expression to transform data
        :return: minimum value
        """
        if self.count() == 0:
            raise NoElementsError(u"Iterable contains no elements")
        return min(self.select(func))

    def max(self, func=lambda x: x):
        """
        Returns the max value of data elements
        :param func: lambda expression to transform data
        :return: maximum value
        """
        if self.count() == 0:
            raise NoElementsError(u"Iterable contains no elements")
        return max(self.select(func))

    def avg(self, func=lambda x: x):
        """
        Returns the average value of data elements
        :param func: lambda expression to transform data
        :return: average value as float object
        """
        count = self.count()
        if count == 0:
            raise NoElementsError(u"Iterable contains no elements")
        return float(self.sum(func)) / float(count)

    def median(self, func=lambda x: x):
        """
        Return the median value of data elements
        :param func: lambda expression to project and sort data
        :return: median value
        """
        if self.count() == 0:
            raise NoElementsError(u"Iterable contains no elements")
        result = self.order_by(func).select(func).to_list()
        length = len(result)
        i = int(length / 2)
        return result[i] if length % 2 == 1 else (float(result[i - 1]) + float(result[i])) / float(2)

    def element_at(self, n):
        """
        Returns element at given index.
            * Raises NoElementsError if no element found at specified position
        :param n: index as int object
        :return: Element at given index
        """
        result = list(itertools.islice(self.to_list(), max(0, n), n + 1, 1))
        if len(result) == 0:
            raise NoElementsError(u"No element found at index {0}".format(n))
        return result[0]

    def element_at_or_default(self, n):
        """
        Returns element at given index or None if no element found
            * Raises IndexError if n is greater than the number of elements in
            enumerable
        :param n: index as int object
        :return: Element at given index
        """
        try:
            return self.element_at(n)
        except NoElementsError:
            return None

    def first(self, func=None):
        """
        Returns the first element in a collection
        :func: predicate as lambda expression used to filter collection
        :return: data element as object or NoElementsError if transformed data
        contains no elements
        """
        if func is not None:
            return self.where(func).element_at(0)
        return self.element_at(0)

    def first_or_default(self, func=None):
        """
        Return the first element in a collection. If collection is empty, then returns None
        :func: predicate as lambda expression used to filter collection
        :return: data element as object or None if transformed data contains no
         elements
        """
        if func is not None:
            return self.where(func).element_at_or_default(0)
        return self.element_at_or_default(0)

    def last(self, func=None):
        """
        Return the last element in a collection
        :func: predicate as a lambda expression used to filter collection
        :return: data element as object or NoElementsError if transformed data
        contains no elements
        """
        if func is not None:
            return self.where(func).reverse().first()
        return self.reverse().first()

    def last_or_default(self, func=None):
        """
        Return the last element in a collection or None if the collection is empty
        :func: predicate as a lambda expression used to filter collection
        :return: data element as object or None if transformed data contains no
         elements
        """
        if func is not None:
            return self.where(func).reverse().first_or_default()
        return self.reverse().first_or_default()

    def order_by(self, key):
        """
        Returns new Enumerable sorted in ascending order by given key
        :param key: key to sort by as lambda expression
        :return: new Enumerable object
        """
        if key is None:
            raise NullArgumentError(u"No key for sorting given")
        kf = [OrderingDirection(key, reverse=False)]
        return SortedEnumerable3(kf, self._data)

    def order_by_descending(self, key):
        """
        Returns new Enumerable sorted in descending order by given key
        :param key: key to sort by as lambda expression
        :return: new Enumerable object
        """
        if key is None:
            raise NullArgumentError(u"No key for sorting given")
        kf = [OrderingDirection(key, reverse=True)]
        return SortedEnumerable3(kf, self._data)

    def skip(self, n):
        """
        Returns new Enumerable where n elements have been skipped
        :param n: Number of elements to skip as int
        :return: new Enumerable object
        """
        return Enumerable3(itertools.islice(self, n, None, 1))

    def take(self, n):
        """
        Return new Enumerable where first n elements are taken
        :param n: Number of elements to take
        :return: new Enumerable object
        """
        return Enumerable3(itertools.islice(self, 0, n, 1))

    def where(self, predicate):
        """
        Returns new Enumerable where elements matching predicate are selected
        :param predicate: predicate as a lambda expression
        :return: new Enumerable object
        """
        if predicate is None:
            raise NullArgumentError(u"No predicate given for where clause")
        return Enumerable3(filter(predicate, self))

    def single(self, predicate):
        """
        Returns single element that matches given predicate.
        Raises:
            * NoMatchingElement error if no matching elements are found
            * MoreThanOneMatchingElement error if more than one matching
            element is found
        :param predicate: predicate as a lambda expression
        :return: Matching element as object
        """
        result = self.where(predicate).to_list()
        count = len(result)
        if count == 0:
            raise NoMatchingElement(u"No matching element found")
        if count > 1:
            raise MoreThanOneMatchingElement(
                u"More than one matching element found. Use where instead")
        return result[0]

    def single_or_default(self, predicate):
        """
        Return single element that matches given predicate. If no matching
        element is found, returns None
        Raises:
            * MoreThanOneMatchingElement error if more than one matching
            element is found
        :param predicate: predicate as a lambda expression
        :return: Matching element as object or None if no matches are found
        """
        try:
            return self.single(predicate)
        except NoMatchingElement:
            return None

    def select_many(self, func=lambda x: x):
        """
        Flattens an iterable of iterables returning a new Enumerable
        :param func: selector as lambda expression
        :return: new Enumerable object
        """
        return Enumerable3(itertools.chain.from_iterable(self.select(func)))

    def add(self, element):
        """
        Adds an element to the enumerable.
        :param element: An element
        :return: new Enumerable object
        """
        if element is None:
            return self
        return self.concat(Enumerable3([element]))

    def concat(self, enumerable):
        """
        Adds enumerable to an enumerable
        :param enumerable: An iterable object
        :return: new Enumerable object
        """
        if not isinstance(enumerable, Enumerable3):
            raise TypeError(
                u"enumerable argument must be an instance of Enumerable")
        return Enumerable3(itertools.chain(self._data, enumerable.data))

    def group_by(self, key_names=[], key=lambda x: x, result_func=lambda x: x):
        """
        Groups an enumerable on given key selector. Index of key name
        corresponds to index of key lambda function.

        Usage:
            Enumerable([1,2,3]).group_by(key_names=['id'], key=lambda x: x) _
                .to_list() --> Enumerable object [
                    Grouping object {
                        key.id: 1,
                        _data: [1]
                    },
                    Grouping object {
                        key.id: 2,
                        _data: [2]
                    },
                    Grouping object {
                        key.id: 3,
                        _data: [3]
                    }
                ]
            Thus the key names for each grouping object can be referenced
            through the key property. Using the above example:

            Enumerable([1,2,3]).group_by(key_names=['id'], key=lambda x: x) _
            .select(lambda g: { 'key': g.key.id, 'count': g.count() }

        :param key_names: list of key names
        :param key: key selector as lambda expression
        :param result_func: lambda function to transform group_join into
        desired structure
        :return: Enumerable of grouping objects
        """
        result = []
        ordered = sorted(self, key=key)
        grouped = itertools.groupby(ordered, key)
        for k, g in grouped:
            can_enumerate = isinstance(k, list) or isinstance(k, tuple) \
                and len(k) > 0
            key_prop = {}
            for i, prop in enumerate(key_names):
                key_prop.setdefault(prop, k[i] if can_enumerate else k)
            key_object = Key(key_prop)
            result.append(Grouping3(key_object, list(g)))
        return Enumerable3(result).select(result_func)

    def distinct(self, key=lambda x: x):
        """
        Returns enumerable containing elements that are distinct based on given
        key selector
        :param key: key selector as lambda expression
        :return: new Enumerable object
        """
        return Enumerable3(self.group_by(key=key).select(lambda g: g.first()).to_list())

    def join(
            self,
            inner_enumerable,
            outer_key=lambda x: x,
            inner_key=lambda x: x,
            result_func=lambda x: x
    ):
        """
        Return enumerable of inner equi-join between two enumerables
        :param inner_enumerable: inner enumerable to join to self
        :param outer_key: key selector of outer enumerable as lambda expression
        :param inner_key: key selector of inner enumerable as lambda expression
        :param result_func: lambda expression to transform result of join
        :return: new Enumerable object
        """
        if not isinstance(inner_enumerable, Enumerable3):
            raise TypeError(
                u"inner_enumerable parameter must be an instance of Enumerable"
            )
        return Enumerable3(
            itertools.product(
                filter(
                    lambda x: outer_key(x) in map(inner_key, inner_enumerable),
                    self
                ),
                filter(
                    lambda y: inner_key(y) in map(outer_key, self),
                    inner_enumerable
                )
            )
        )\
            .where(lambda x: outer_key(x[0]) == inner_key(x[1]))\
            .select(result_func)

    def default_if_empty(self, value=None):
        """
        Returns an enumerable containing a single None element if enumerable is
        empty, otherwise the enumerable itself
        :return: an Enumerable object
        """
        if self.count() == 0:
            return Enumerable3([value])
        return self

    def group_join(
            self,
            inner_enumerable,
            outer_key=lambda x: x,
            inner_key=lambda x: x,
            result_func=lambda x: x
    ):
        """
        Return enumerable of group join between two enumerables
        :param inner_enumerable: inner enumerable to join to self
        :param outer_key: key selector of outer enumerable as lambda expression
        :param inner_key: key selector of inner enumerable as lambda expression
        :param result_func: lambda expression to transform the result of group
        join
        :return: new Enumerable object
        """
        if not isinstance(inner_enumerable, Enumerable3):
            raise TypeError(
                u"inner enumerable parameter must be an instance of Enumerable"
            )
        return Enumerable3(
            itertools.product(
                self,
                inner_enumerable.default_if_empty()
            )
        ).group_by(
            key_names=['id'],
            key=lambda x: outer_key(x[0]),
            result_func=lambda g: (
                g.first()[0],
                g.where(lambda x: inner_key(x[1]) == g.key.id).select(
                    lambda x: x[1]
                )
            )
        ).select(result_func)

    def any(self, predicate=None):
        """
        Returns true if any elements that satisfy predicate are found
        :param predicate: condition to satisfy as lambda expression
        :return: boolean True or False
        """
        if predicate is None:
            return self.count() > 0
        return self.where(predicate).count() > 0

    def intersect(self, enumerable, key=lambda x: x):
        """
        Returns enumerable that is the intersection between given enumerable
        and self
        :param enumerable: enumerable object
        :param key: key selector as lambda expression
        :return: new Enumerable object
        """
        if not isinstance(enumerable, Enumerable3):
            raise TypeError(
                u"enumerable parameter must be an instance of Enumerable")
        return self.join(enumerable, key, key).select(lambda x: x[0])

    def union(self, enumerable, key=lambda x: x):
        """
        Returns enumerable that is a union of elements between self and given
        enumerable
        :param enumerable: enumerable to union self to
        :param key: key selector used to determine uniqueness
        :return: new Enumerable object
        """
        if not isinstance(enumerable, Enumerable3):
            raise TypeError(
                u"enumerable parameter must be an instance of Enumerable")
        if self.count() == 0:
            return enumerable
        if enumerable.count() == 0:
            return self
        return self.concat(enumerable).distinct(key)

    def except_(self, enumerable, key=lambda x: x):
        """
        Returns enumerable that subtracts given enumerable elements from self
        :param enumerable: enumerable object
        :param key: key selector as lambda expression
        :return: new Enumerable object
        """
        if not isinstance(enumerable, Enumerable3):
            raise TypeError(
                u"enumerable parameter must be an instance of Enumerable")
        membership = (
            0 if key(element) in enumerable.intersect(self, key).select(key) else 1
            for element in self
        )
        return Enumerable3(
            itertools.compress(
                self,
                membership
            )
        )

    def contains(self, element, key=lambda x: x):
        """
        Returns True if element is found in enumerable, otherwise False
        :param element: the element being tested for membership in enumerable
        :param key: key selector to use for membership comparison
        :return: boolean True or False
        """
        return self.select(key).any(lambda x: x == key(element))

    def aggregate(self, func, seed=None):
        """
        Perform a calculation over a given enumerable using the initial seed
        value
        :param func: calculation to perform over every the enumerable.
        This function will ingest (aggregate_result, next element) as parameters
        :param seed: initial seed value for the calculation. If None, then the
        first element is used as the seed
        :return: result of the calculation
        """
        result = seed if seed is not None else self.first()
        for i, e in enumerate(self):
            if i == 0 and seed is None:
                continue
            result = func(result, e)
        return result

    def all(self, predicate):
        """
        Determines whether all elements in an enumerable satisfy the given
        predicate
        :param predicate: the condition to test each element as lambda function
        :return: boolean True or False
        """
        return self.where(predicate).count() == self.count()

    def append(self, element):
        """
        Appends an element to the end of an enumerable
        :param element: the element to append to the enumerable
        :return: Enumerable object with appended element
        """
        return self.concat(Enumerable3([element]))

    def prepend(self, element):
        """
        Prepends an element to the beginning of an enumerable
        :param element: the element to prepend to the enumerable
        :return: Enumerable object with the prepended element
        """
        return Enumerable3([element]).concat(self)

    @staticmethod
    def empty():
        """
        Returns an empty enumerable
        :return: Enumerable object that contains no elements
        """
        return Enumerable3()

    @staticmethod
    def range(start, length):
        """
        Generates a sequence of integers starting from start with length of length
        :param start: the starting value of the sequence
        :param length: the number of integers in the sequence
        :return: Enumerable of the generated sequence
        """
        return Enumerable3(range(start, start + length, 1))

    @staticmethod
    def repeat(element, length):
        """
        Generates an enumerable containing an element repeated length times
        :param element: the element to repeat
        :param length: the number of times to repeat the element
        :return: Enumerable of the repeated elements
        """
        return Enumerable3(itertools.repeat(element, length))

    def reverse(self):
        """
        Inverts the order of the elements in a sequence
        :return: Enumerable with elements in reversed order
        """
        return self.aggregate(lambda *args: args[0].prepend(args[1]), Enumerable3())

    def skip_last(self, n):
        """
        Skips the last n elements in a sequence
        :param n: the number of elements to skip
        :return: Enumerable with n last elements removed
        """
        return self.take(self.count() - n)

    def skip_while(self, predicate):
        """
        Bypasses elements in a sequence while the predicate is True. After predicate fails
        remaining elements in sequence are returned
        :param predicate: a predicate as a lambda expression
        :return: Enumerable
        """
        return Enumerable3(itertools.dropwhile(predicate, self))

    def take_last(self, n):
        """
        Takes the last n elements in a sequence
        :param n: the number of elements to take
        :return: Enumerable containing last n elements
        """
        return self.skip(self.count() - n)

    def take_while(self, predicate):
        """
        Includes elements in a sequence while the predicate is True. After predicate fails
        remaining elements in a sequence are removed
        :param predicate: a predicate as a lambda expression
        :return: Enumerable
        """
        return Enumerable3(itertools.takewhile(predicate, self))

    def zip(self, enumerable, func):
        """
        Merges 2 Enumerables using the given function. If the 2 collections are of unequal length, then
        merging continues until the end of one of the collections is reached
        :param enumerable: Enumerable collection to merge with
        :param func: a function to perform the merging
        :return: Enumerable
        """
        if not isinstance(enumerable, Enumerable3):
            raise TypeError()
        return Enumerable3(itertools.zip_longest(self, enumerable)) \
            .where(lambda x: x[0] is not None and x[1] is not None) \
            .select(lambda x: func(x))


class Grouping3(Enumerable3):
    def __init__(self, key, data):
        """
        Constructor of Grouping class used for group by operations of
        Enumerable class
        :param key: Key instance
        :param data: iterable object
        :return: void
        """
        if not isinstance(key, Key):
            raise Exception("key argument should be a Key instance")
        self.key = key
        super(Grouping3, self).__init__(data)

    def __repr__(self):
        return {
            'key': self.key.__repr__(),
            'enumerable': self._data.__repr__()
        }.__repr__()


class SortedEnumerable3(Enumerable3):
    def __init__(self, key_funcs, data):
        """
        Constructor
        :param key_funcs: list of OrderingDirection instances in order of
        primary key
        --> less important keys
        :param data: data as iterable
        """
        if key_funcs is None:
            raise NullArgumentError(u"key_funcs argument cannot be None")
        if not isinstance(key_funcs, list):
            raise TypeError(u"key_funcs should be a list instance")
        self._key_funcs = [
            f for f in key_funcs if isinstance(f, OrderingDirection)
        ]
        super(SortedEnumerable3, self).__init__(data)

    def __iter__(self):
        for o in reversed(self._key_funcs):
            self._data = sorted(self._data, key=o.key,
                                reverse=o.descending)
        cache = []
        for d in self._data:
            cache.append(d)
            yield d
        self._data = cache

    def then_by(self, func):
        """
        Subsequent sorting function in ascending order
        :param func: lambda expression for secondary sort key
        :return: SortedEnumerable instance
        """
        if func is None:
            raise NullArgumentError(
                u"then by requires a lambda function arg")
        self._key_funcs.append(OrderingDirection(key=func, reverse=False))
        return SortedEnumerable3(self._key_funcs, self._data)

    def then_by_descending(self, func):
        """
        Subsequent sorting function in descending order
        :param func: lambda function for secondary sort key
        :return: SortedEnumerable instance
        """
        if func is None:
            raise NullArgumentError(
                u"then_by_descending requires a lambda function arg")
        self._key_funcs.append(OrderingDirection(key=func, reverse=True))
        return SortedEnumerable3(self._key_funcs, self._data)
