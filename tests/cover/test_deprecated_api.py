# coding=utf-8

# Copyright (C) 2013-2015 David R. MacIver (david@drmaciver.com)

# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

from __future__ import division, print_function, absolute_import, \
    unicode_literals

import sys
from random import Random
from decimal import Decimal
from fractions import Fraction

import pytest
from hypothesis.errors import InvalidArgument
import hypothesis.specifiers as s
from hypothesis import Settings, strategy
from hypothesis.internal.compat import text_type, binary_type, \
    integer_types
from hypothesis.searchstrategy.narytree import NAryTree, Branch, Leaf
from tests.common.basic import Bitfields

original_strictness = Settings.default.strict


def setup_module():
    Settings.default.strict = False


def teardown_module():
    Settings.default.strict = original_strictness


@pytest.mark.parametrize('typ', [
    complex, float, bool, Random, type(None), text_type, binary_type,
    Decimal, Fraction,
])
def test_types_give_types(typ):
    assert isinstance(strategy(typ).example(), typ)


def test_int_gives_ints():
    assert isinstance(strategy(int).example(), integer_types)


def test_just_is_just():
    assert strategy(s.just(1)).example() == 1


def test_tuples_give_tuples():
    x = strategy((bool, bool)).example()
    assert len(x) == 2
    assert isinstance(x[0], bool)
    assert isinstance(x[1], bool)


def test_lists_mix():
    x = strategy([(bool,), (bool, bool)]).example()
    assert all(1 <= len(y) <= 2 for y in x)


def test_none_lists():
    assert not any(strategy([None]).example())


def test_sampled_from_samples():
    x = strategy(s.sampled_from((1, 2, 3)))
    assert x.example() in (1, 2, 3)


def test_none_is_none():
    assert strategy(None).example() is None


def test_sets_give_sets():
    assert isinstance(strategy(set()).example(), set)


def test_frozensets_give_frozensets():
    assert isinstance(strategy(frozenset()).example(), frozenset)


def test_streaming():
    assert isinstance(strategy(s.streaming(bool)).example()[100], bool)


def test_random():
    strategy(Random).example().random()


def test_variadic_dictionaries():
    x = strategy(s.dictionary(bool, bool)).example()
    assert all(
        isinstance(k, bool) and isinstance(v, bool) for k, v in x.items())


def test_one_of():
    assert isinstance(strategy(s.one_of((bool, ()))).example(), (bool, tuple))


def test_fixed_dict():
    assert strategy({'k': None}).example() == {'k': None}


def test_sampled_from_one():
    assert strategy(s.sampled_from((1,))).example() == 1


def test_basic():
    assert isinstance(strategy(Bitfields).example(), integer_types)
    assert isinstance(strategy(Bitfields()).example(), integer_types)


def test_tree():
    tree = strategy(NAryTree(bool, bool, bool)).example()
    assert isinstance(tree, (Branch, Leaf))


@pytest.mark.parametrize('r', [
    s.floats_in_range(0, 1),
    s.floats_in_range(1, 2),
    s.floats_in_range(1, 1),
    s.floats_in_range(-sys.float_info.max, sys.float_info.max),
])
def test_float_ranges(r):
    assert r.start <= strategy(r).example() <= r.end


def test_strings():
    x = strategy(s.strings("a")).example()
    assert set(x).issubset({"a"})


def test_empty_strings():
    assert strategy(s.strings("")).example() == ""


def test_single_float_in_range():
    assert strategy(s.floats_in_range(1, 1)).example() == 1


def test_float_range_validates():
    with pytest.raises(InvalidArgument):
        s.floats_in_range(2, 1)

    with pytest.raises(InvalidArgument):
        s.floats_in_range(1, float('inf'))


def test_sampled_from_validates():
    with pytest.raises(ValueError):
        strategy(s.sampled_from([]))