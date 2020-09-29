#!/usr/bin/env python3

from itertools import * #permutations, combinations, product
from random import random
from operator import itemgetter
from unidecode import unidecode

import pdb

def make_heading2(text, a="-", b="-"):
    return a * len(text) + "\n" + text + "\n" + b * len(text)

class Entry:
    '''
    A wrapper class for entries in a Dataset.

    Each Entry has a `value` for use in computations and an `ovalue` (original value) for display.
    '''

    def __init__(self, value):
        self.value = value # value to use in computations
        self.ovalue = value # original value to display

    def __repr__(self):
        return self.ovalue

    def __getitem__(self, x):
        return self.value[x]

    def __len__(self):
        return len(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def tidy(self, alpha_only=True, ignore_case=True, replace_special_characters=True):
        '''
        Entries can be `tidied` by removing non-alphabetical characters, ignoring case, or replacing special characters with equivalents using unidecode (e.g. replacing accented characters with unaccented ones).
        '''
        word = self.value
        if alpha_only:
            word = ''.join(c for c in word if c.isalpha())
        if replace_special_characters:
            word = unidecode(word)
        if ignore_case:
            word = word.lower()
        # self.ovalue = self.value
        self.value = word.rstrip()

class Dataset:
    '''
    A wrapper class for a set of data. A Dataset consists of a set of Entries.

    Each Dataset has a name and a list of Entries.
    '''
    def __init__(self, name, data=[]):
        self.name = name
        self.data = data

    def __str__(self):
        # return "Dataset {} with {} entries".format(self.name, len(self.data))
        return self.name

    def __repr__(self):
        return self.name

    # def __eq__(self, other):
    #     return self.name == other.name
    #
    # def __le__(self, other):
    #     return self.name <= other.name

    def load(self, filename=None):
        '''
        The data for a Dataset is usually read from a text file. By default this file has the same name as the Dataset.
        '''
        if not filename:
            filename = self.name
        try:
            with open("datasets/" + filename + ".txt") as f:
                self.data = [Entry(line.rstrip()) for line in f]
        except FileNotFoundError:
            print("Dataset {}.txt not found".format(filename))

    def sort(self, key=None):
        if not key:
            key = lambda x: x
        self.data = sorted(self.data, key=key) # use in place sort?

    def tidy(self, alpha_only=True, ignore_case=True, replace_special_characters=True):
        for entry in self.data:
            entry.tidy(alpha_only=alpha_only, ignore_case=ignore_case, replace_special_characters=replace_special_characters)

    def __getitem__(self, x):
        return self.data[x]

    def show(self, n=None):
        if not n:
            n = len(self.data)
        print("{} ({} entries)".format(self.name, n))
        print(self.data[:n])

    def nonoverlaps(self, args="mackerel"):
        '''
        Find Entries in a Dataset which have no letters in common with a given word (by default "mackerel")
        '''
        return [entry for entry in self.data if set(entry) & set(args) == set()]

    def alternators(self, args="", mode="v"):
        '''
        Find Entries in a Dataset in which the letters alternate between two sets, e.g. between vowels and consonants or between letters that can be typed with the left hand on a typewriter and those that can be typed with the right hand. Custom sets can also be specified.
        '''
        if not args and mode == "v":
            left, right = set("aeiou"), set("bcdfghjklmnpqrstvwxyz")
        elif mode == "k":
            left, right = set("qwertasdfgzxcvb"), set("yuiophjklnm")
        else:
            left, right = set(args), set("abcdefghijklmnopqrstuvwxyz") - set(args)
        def alternator(word):
            odds = {word[i] for i in range(len(word)) if i % 2 == 0}
            evens = {word[i] for i in range(len(word)) if i % 2 == 1}
            return (odds & left == set() and evens & right == set()) \
                   or (odds & right == set() and evens & left == set())
        return [entry for entry in self.data if alternator(entry)]

    def contains_all(self, args="aeiou"):
        '''
        Find Entries in a Dataset than contain all the letters in a given set (by default all the vowels).
        '''
        tidyargs = ''.join(c for c in args if c.isalpha()).lower()
        return [entry for entry in self.data if all(x in entry for x in tidyargs)]
        # Need to tidy args before use

    def contains_only(self, args="qwertyuiop"):
        '''
        Find Entries in a Dataset that only use letters from a given set (by default the top row of a Qwerty keyboard).
        '''
        tidyargs = ''.join(c for c in args if c.isalpha()).lower()
        return [entry for entry in self.data if all(x in tidyargs for x in entry)]

    def contains(self, args):
        '''
        Find Entries in a Dataset that contain a given string as a consecutive substring.
        '''
        return [entry for entry in self.data if args.lower() in entry.value]

    def contains_uniquely(self, args):
        '''
        Find Entries in a Dataset that contain a given string as a consecutive substring
        and are unique in their dataset for doing so.
        '''
        result = self.contains(args)
        return result if len(result) == 1 else None

    def unique_combinations(self, n=2):
        '''
        Generate all possible combinations of n letters and return all Entries uniquely containing each combination.
        '''
        for combo in permutations("abcdefghijklmnopqrstuvwxyz", n):
            c = "".join(combo)
            result = self.contains_uniquely(c)
            if result:
                print("{}: {}".format(c.upper(), result[0]))

class Collection:
    '''
    A wrapper class for a collection of Datasets.
    '''
    def __init__(self, name="Datasets", autoload=True, autotidy=True):
        self.name = name
        self.datasets = {}
        self.dataset_keys = {}
        # self.check_only = set()
        self.included_datasets = set()
        self.excluded_datasets = set()
        if autoload:
            self.load(autotidy=autotidy)

    def __str__(self):
        return "Collection {} with {} datasets".format(self.name.upper(), len(self.datasets))

    def __repr__(self):
        return self.name.upper()

    def __iter__(self):
        # return iter({**self.datasets, **self.dataset_keys})
        return iter(self.datasets.values())

    def __getitem__(self, d):
        '''
        Return a Dataset in a Collection either by name or by number.
        '''
        if type(d) is int:
            try:
                d = self.dataset_keys[d]
                return self.datasets[d]
            except KeyError:
                print("No loaded dataset with number {}".format(d))
        else:
            try:
                return self.datasets[d]
            except KeyError:
                print("No loaded dataset with name \"{}\"".format(d))

    def load(self, filename="datasets", verbose=False, autotidy=True):
        self.datasets = {}
        with open("datasets/" + filename + ".txt") as f:
            available_datasets = [(Dataset(d.rstrip().split(':')[0]), d.rstrip().split(':')[1][1:]) for d in f]
        # print(available_datasets)
        for i, (d, df) in enumerate(available_datasets):
            d.load(filename=df)
            self.datasets[d.name] = d
            self.dataset_keys[i+1] = d.name
            if verbose:
                print("Loaded dataset {}.txt".format(d.name))
        self.included_datasets = {self[d] for d in self.datasets}
        print("Loaded {} datasets from {}.txt".format(len(self.datasets),filename))
        if autotidy:
            self.tidy()
        # print("{} datasets were excluded".format(len(self.excluded_datasets)))

    def tidy(self, alpha_only=True, ignore_case=True, replace_special_characters=True):
        for d in self.datasets.keys():
            self[d].tidy(alpha_only=alpha_only, ignore_case=ignore_case, replace_special_characters=replace_special_characters)

    def show(self, d=None, n=None, keys=False):
        if not d:
            print(self)
            if keys:
                out = sorted([(i,self[self.dataset_keys[i]].name) for i in self.dataset_keys])
            else:
                out = sorted([self[d].name for d in self.datasets])
            for o in out:
                print(o)
        else:
            if d in self.datasets or d in self.dataset_keys:
                self[d].show(n)
            else:
                print("No loaded dataset with name \"{}\"".format(d))

    def check_only(self, ds):
        '''
        Specify that only certain Datasets be included in searches.
        '''
        if type(ds) is str or type(ds) is int:
            # if only one dataset is specified (either by name or number) it doesn't need to be written as a one-item list
            ds = {ds}
        self.included_datasets = {self[d] for d in ds}

    def check_all(self):
        # self.check(self.datasets)
        self.included_datasets = {d for d in self.datasets.values()}
        self.excluded_datasets = set()

    def include(self, ds):
        if type(ds) is str or type(ds) is int:
            ds = {ds}
        self.included_datasets |= {self[d] for d in ds}

    def exclude(self, ds):
        if type(ds) is str or type(ds) is int:
            ds = {ds}
        self.excluded_datasets |= {self[d] for d in ds}

    def add(self, ds, filenames=None):
        if type(ds) is str:
            ds = [ds]
        if not filenames:
            filenames = ds
        for i,d in enumerate(ds):
            d = Dataset(d)
            d.load(filename=filenames[i])
            self.datasets[d.name] = d
        self.excluded_datasets -= set(ds)

    def find_word_anagrams(self, w, allow_trivial=False):
        '''
        Find all Entries in Collection which are anagrams of a given word.
        '''
        # Generate a random code to append to the given word, to ensure uniqueness
        t = w + str(random())[2:7]
        # Create a temporary Dataset with the given word as the only Entry
        self.datasets[t] = Dataset("\""+w+"\"",data=[Entry(w)])
        self.check_only(t)
        self.tidy()
        # Find anagrams
        self.find_all_anagrams(allow_trivial=allow_trivial)
        # Delete temporary Dataset
        del self.datasets[t]

    def find_anagrams(self, d1, d2, allow_trivial=False):
        '''
        Find anagram pairs between two given Datasets.
        '''
        if type(d1) is str or type(d1) is int:
            d1 = self[d1]
        if type(d2) is str or type(d2) is int:
            d2 = self[d2]
        result = []
        # Naive version
        # return [(x,y) for (x,y) in product(d1,d2) if sorted(x) == sorted(y) and (x != y or allow_trivial)]

        for x in sorted(d1, key=len):
            for y in sorted(d2, key=len):
        # for x, y in product(sorted(d1, key=len), sorted(d2, key=len)):
                if len(x) < len(y):
                    break
                if len(x) > len(y):
                    continue
                if sorted(x) == sorted(y):
                    if (x != y or allow_trivial) and (x,y) not in result:
                        result.append((x,y))
        return result

    def find_anagram_pairs(self, k1, k2, allow_trivial=False):
        # return self.find_anagrams(d1, d2, allow_trivial=allow_trivial)
        d1, d2 = self[self.dataset_keys[k1]], self[self.dataset_keys[k2]]
        try:
            return self.anagram_pairs()[(d1,d2)]
        except KeyError:
            try:
                return self.anagram_pairs()[(d2,d1)]
            except KeyError:
                return []


    def find_all_anagrams(self, allow_trivial=False):
        namesort = lambda d: d.name
        left = self.included_datasets - self.excluded_datasets
        left = sorted(left, key=namesort)
        # right = set(self.datasets.values()) - self.excluded_datasets
        right = left
        checked_pairs = []
        # for d1, d2 in product(sorted(left, key=namesort), sorted(right, key=namesort)):
        # for d1, d2 in product(left, right):
        pairs = permutations(left, 2) if allow_trivial else combinations(left, 2)
        for d1, d2 in pairs:
            # if (d2,d1) in checked_pairs:
            #     continue
            # if allow_trivial and d1 == d2:
            #     continue
            # if d1 in self.excluded_datasets or d2 in self.excluded_datasets:
            #     continue
            # checked_pairs.append((d1,d2))
            anagrams = self.find_anagrams(d1, d2, allow_trivial)
            if anagrams:
                print("{} and {}".format(d1.name, d2.name))
                print(anagrams)

    def find_all(self, method, args, unique=True, longest=False):
        namesort = lambda d: d.name
        for d in sorted(self.included_datasets - self.excluded_datasets, key=namesort):
            result = method(d, args)
            c ='*' if len(result) == 1 and not unique else ''
            if unique and len(result) != 1:
                continue
            if longest and result:
                result = sorted(result, key=len, reverse=True)[0]
            if result:
                print("{}: {}{}".format(d.name,result,c))

    def find_nonoverlaps(self, args="mackerel", unique=True, longest=False):
        f = lambda d, args: d.nonoverlaps(args)
        return self.find_all(f, args, unique=unique, longest=longest)

    def find_alternators(self, args="", mode="v", unique=True, longest=False):
        f = lambda d, args: d.alternators(args, mode=mode)
        return self.find_all(f, args, unique=unique, longest=longest)

    def find_contains_all(self, args="aeiou", unique=True, longest=False):
        f = lambda d, args: d.contains_all(args)
        return self.find_all(f, args, unique=unique, longest=longest)

    def find_contains_only(self, args="qwertyuiop", unique=True, longest=False):
        f = lambda d, args: d.contains_only(args)
        return self.find_all(f, args, unique=unique, longest=longest)

    def create_anagram_table(self):
        self.anagram_table = dict()
        for d in self:
            for entry in d:
                k = ''.join(sorted(entry.value))
                try:
                    self.anagram_table[k].add((d, entry))
                except KeyError:
                    self.anagram_table[k] = {(d, entry)}

    def anagram_pairs(self, allow_trivial=False):
        if not self.anagram_table:
            self.create_anagram_table()
            # Entries in anagram table are of the form *sorted anagram*: {(Dataset, Entry), ...}
        result_table = dict()
        for vs in self.anagram_table.values():
            # vs is a set of pairs of the form (Dataset, Entry)
            # We only care about sets where there is more than one element
            if len(vs) > 1:
                for x, y in combinations(vs, 2):
                    # x and y are pairs of the form (Dataset, Entry)
                    d1, d2 = x[0], y[0] # Datasets
                    v1, v2 = x[1], y[1] # Entrys
                    if v1 != v2 or allow_trivial:
                        try:
                            result_table[(d1,d2)].add((v1,v2))
                        except KeyError:
                            result_table[(d1,d2)] = {(v1,v2)}
        return result_table
        # Entries in result table are of the form (Dataset1, Dataset2): {(Entry1, Entry2), ...}

    def show_anagram_pairs(self, allow_trivial=False):
        for (d1,d2), matches in self.anagram_pairs(allow_trivial).items():
            print(make_heading2("{} and {}".format(d1,d2)))
            for (x,y) in matches:
                print("{} <-> {}".format(x,y))

    def show_word_anagrams(self, word, allow_trivial=False):
        if not self.anagram_table:
            self.create_anagram_table()
        for anagram in self.anagram_table[sorted(word)]:
            for (x,y) in matches:
                print("{} <-> {}".format(x,y))
