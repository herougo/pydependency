from long_import import (stuff1,
  stuff2, stuff3)
import sort
from sort.bad import *
from sorting import There
import yes.good.hello


# Comment


YU = None
MODIFIED_TWICE = 1
MODIFIED_TWICE = 2
USED_BY_CLASS_1 = 1
USED_BY_CLASS_2 = 2

class Empty:
  pass

class Hi:
  def __init__(self):
    pass

class Large:
  _constant = None
  def __init__(self, asdf, **kwargs):
    do_stuff()
    self._asdf = asdf

  def adder(self, other):
    global USED_BY_CLASS_1
    USED_BY_CLASS_1 = 0

  def say_hi(self):
    return USED_BY_CLASS_2

class UnusedClass:
  def __init__(self):
    pass

def my_func():
  """
  Multi-line comment
  """
  not_comment = """
  not a multi-line comment
  """
  global YU
  YU = 2
  MODIFIED_TWICE = 3 # no effect
  return None

def func(a, b, c, *vargs, **kwargs):
  pass
  
def          unused_func(**kwargs):
  pass

if True:
  # global variables, classes, and functions
  hi = yu
  z = Empty()
  a = Hi()
  b = my_func()
  c = func(1, 4, 2, 2, 54, 5, yes="yes")
  
  # Large
  l = Large(a, no="no")
  l.adder("yes")
  l.say_hi()
  
  # import using
  a = sort.bell()
  b = yes.good.hello.hi()
  c = There()
  
  # Not defined yet
  d = ClassNotDefinedYet()
  d.function_not_defined_yet(a, b, c=c)
  e = other_function_not_defined_yet(a, b, c=c)
  i.dont.exist()