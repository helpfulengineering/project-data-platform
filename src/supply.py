    # supply - Helpful Engineering's Project Data supply module
    # Copyright (C) 2021  Robert L. Read <read.robert@gmail.com>

    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU Affero General Public License as
    # published by the Free Software Foundation, either version 3 of the
    # License, or (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU Affero General Public License for more details.

    # You should have received a copy of the GNU Affero General Public License


# Note: I'm using the name eqn, here but possibly
# an expression is better (but in any case we will use the SymPy pacakges.
# Note an invariant (currently unchecked) is that the eqn should have the same number
# of sybols as the inputs (or that + 1) and the names should match.
# It would be better if we asserted that cleanly
from functools import reduce
from sympy import *

class Supply:
    def __init__(self,name,outputs,inputs,eqn):
        self.name = name
        self.inputs = frozenset(inputs)
        self.outputs = frozenset(outputs)
        self.eqn = eqn

class SupplyNetwork:
    def __init__(self,name,supplies):
        self.name = name
        self.supplies = supplies

def unionSupplyNetworks(a,b):
    return SupplyNetwork(a.name + "|" + b.name,a.supplies + b.supplies)

# return all the types appearing the supply network
def goodTypes(sn):
    return reduce(lambda a, b: frozenset.union(a,b),
                  map(lambda a: frozenset.union(a.inputs,a.outputs),sn.supplies))

# find one supplier of type t
def oneSupply(tp,sn):
    for s in sn.supplies:
        if tp in s.outputs:
            return tp
    return None

def allSupplies(tp,sn):
    for s in sn.supplies:
        if tp in s.outputs:
            yield s

# The inputDict maps keys to additional SupplyTrees.
class SupplyTree:
    def __init__(self,supply,inputDict):
        self.supply = supply
        self.inputDict = inputDict
    def incompleteGoods(self):
        missingGoods = []
        for v in self.supply.inputs:
            if v in self.inputDict:
                missingGoods = missingGoods + self.inputDict[v].incompleteGoods()
            else:
                missingGoods.append(v)
        return missingGoods
    def isComplete(self):
        missingGoods = self.incompleteGoods()
        return not missingGoods
    # my initial printing will just take the subtrees and
    # place this node above them.
    def __str__(self):
        # if the inputDict is empty, we can render without a line!
        numerator = ",".join(self.supply.outputs) + ":" + self.supply.name
        if (self.inputDict):
            subtrees = "".join(map(str,self.inputDict.values()))
            labels = []
            for (k, v) in iter(self.inputDict.items()):
                labels.append(k + ':' + str(v.supply.name))
            denominator = ",".join(labels)
            charlen = max(len(denominator),len(numerator))
            numdiff = max(charlen - len(numerator),0)//2
            demdiff = max(charlen - len(denominator),0)//2
            return ' ' * numdiff + numerator + '\n' + '-' * charlen + '\n' + ' ' * demdiff + denominator + '\n' + subtrees
        else:
            charlen = len(numerator)
            return numerator + '\n' + '=' * charlen + '\n'

# TODO: We could add Equational consistency to this
def checkConsistency(supplyTree):
    for key in supplyTree.inputDict:
        if key not in supplyTree.inputDict[key].supply.outputs:
            return False
        else:
            return checkConsistency(supplyTree.inputDict[key])
    return True

# Return the characteristic equation of this supplyTree by using
# substitutions on the equations of supply
# For now this code will make the assumption there is only one good
# and it is the first of the outputs.
def characteristicExpression(supplyTree):
    pairs = []
    good = next(iter(supplyTree.supply.outputs))
    for key in supplyTree.inputDict:
        old = symbols(key)
        new = characteristicExpression(supplyTree.inputDict[key])
        pairs.append((old,new))
    return supplyTree.supply.eqn.subs(pairs)

# Now we define a SupplyProblem to be a desired type and
# SupplyNetwork. There are lots of things you can ask of
# a SupplyProblem, but the most basic is to enumerate all
# solutions, which are consistent SupplyTrees. So our
# basic goal is to define SupplyProblem in a way to do that.

# Invarinants: the supIdx and the inputIdx alwyays
# point to the next one to produce. The act of calling
# next always producing something or throws the StopIteration.
# After stashing a return value, we call next on the first supplyProblem/input.
# If this throws an exception, we move "up".
class SupplyProblem:
    def __init__(self,good,supplyNetwork):
        self.good = good
        self.supplyNetwork = supplyNetwork
    # true if we could establish a new supply
    def newSupply(self):
        if (self.supIdx >= len(self.supplies)):
            return False
        self.inputToProblemIterator = {}
        for input in self.supplies[self.supIdx].inputs:
            self.inputToProblemIterator[input] = iter(SupplyProblem(input,self.supplyNetwork))
        # Really, Pythonistas? This is how you make a ternary expression? (sigh).
        self.inputIdx = 0 if self.supplies[self.supIdx].inputs else None
        # Because we have set a new supIdx, we start with a blank inputToTrees map
        self.inputToTrees = {}
        return True
    def __iter__(self):
        self.currentTreesValid = False
        self.supIdx = -1 # This are invalid until we have have a matching supply!
        self.inputIdx = -1 # This is invalid until we have inputs
        self.inputToTrees = {}
        self.inputToProblemIterator = {}
        # Note: This may materialize all entries, which is not what we want.
        self.supplies = list(allSupplies(self.good,self.supplyNetwork))
        # We will retain an index to which supply we are on...
        if self.supplies:
            self.supIdx = 0
            # We also need to create recursive SupplyProblems (relative to this supply)
            # for all inputs...
            self.currentTreesValid = self.newSupply()
        else:
            self.currentTreesValid = False
        return self
    # We have a problem here. I need to work out the invariants
    # I think we need to produce something BEFORE we update
    # the indices. The problem is I currently can't tell
    # the difference between empty inputs and being done with them!
    # For a given supply, we begin by need to cylce through each input,
    # including the case of new supply provided for that input!
    # Can we compute this from only the inputIdx and supIdx?
    def generateCurrentTree(self):
        d = {}
        # return SupplyTree(self.supplies[self.supIdx],self.inputToTrees)
        for i in self.supplies[self.supIdx].inputs:
            # This must support inputToTrees being empty
            if i in self.inputToTrees and (self.inputToTrees[i] is not None):
                d[i] = self.inputToTrees[i]
        return SupplyTree(self.supplies[self.supIdx],d)
    # This the trickiest part. We attempt to iterate the inputIdx
    # problem. If that fails, we move up to the next InputIdx,
    # and start all lower problems over again! If we fail on
    # the final index, we are done, and return false
    # This routine must advance either supIdx or inputIdx or
    # have successfully called next on a subproblem, or established
    # a subproblem which was not in place.
    #
    # This return a boolean on success
    def advanceCurrentInputByOne(self):
        input = next(x for i,x in enumerate(self.supplies[self.supIdx].inputs) if i==self.inputIdx)
        # if the problem has not yet been created, try to create it
        try:
            tree = next(self.inputToProblemIterator[input])
            self.inputToTrees[input] = tree;
            return True
        except StopIteration:
            return False
    def advanceExactlyOnce(self):
        if (self.inputIdx is not None):
            while (self.inputIdx < len(self.supplies[self.supIdx].inputs)):
                success = self.advanceCurrentInputByOne()
                if success:
                    # reset all lower trees and problems
                    for count,input in enumerate(self.supplies[self.supIdx].inputs):
                            if count < self.inputIdx:
                                self.inputToTrees[input] = None
                                self.inputToProblemIterator[input] = iter(SupplyProblem(input,self.supplyNetwork))
                    self.inputIdx = 0 # here we start iterating from the the bottom again!
                    return True
                else:
                    self.inputIdx = self.inputIdx + 1
        self.supIdx = self.supIdx + 1
        return self.newSupply()
    # Note this is made more complicated by the fact that we want
    # to return all solutions, including those which are incomplete...
    # That makes this a little harder to think about.
    def __next__(self):
        if self.currentTreesValid:
            # If the currentTrees are valid, we want to generate a SupplyTree
            # to return, and then advance our iteration
            currentTree = self.generateCurrentTree()
            # Now we want have to make exactly one iteration.
            # If calling next on a subordinate SupplyProblem works,
            # this is easy. When it fails, we have to move "up".
            # If all fail, we are no longer valid.
            self.currentTreesValid = self.advanceExactlyOnce()
            return currentTree
        else:
            raise StopIteration
    def completeSupplyTrees(self):
        allTrees = list(iter(self))
        return filter(lambda a: a.isComplete(),allTrees)
    # f is the function to be optimized
    def optimalCompleteSupplyTrees(self,f):
        cTrees = self.completeSupplyTrees()
        m = None
        minE = None
        for tree in cTrees:
            v = f(tree)
            if m is None or v < m:
                m = v
                minE = tree
        return (tree,m)
    def optimalCompleteSupplyTreeByPrice(self,priceMap):
        return self.optimalCompleteSupplyTrees((lambda s: characteristicExpression(s).subs(priceMap)))
