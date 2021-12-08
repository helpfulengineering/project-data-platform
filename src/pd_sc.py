    # pd_sc - Helpful Engineering's Project Data Supply Chain modeling and CLI
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
    # along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Our most basic type is the "Product Type", but we will just use strings for these for now.

# The second type is the Supply, which is really short for "SupplyCapability". A Supply has
# inputs and output types, a name, and a characteristic equation.


from functools import reduce
import pprint

class Supply:
    def __init__(self,name,outputs,inputs,eqn):
        self.name = name
        self.inputs = frozenset(inputs)
        self.outputs = frozenset(outputs)
        self.eqn = eqn

# A vary basic set of supplies...
# Possibly we should create anonymous supply signatures...
c1 = Supply("chair_1",["chair"],["leg","seat","back"],"no equation yet")
c2 = Supply("chair_2",["chair"],["leg","seat","back"],"no equation yet")
l1 = Supply("leg_1",["leg"],[],"no equation yet")
s1 = Supply("seat_1",["seat"],[],"no equation yet")
b1 = Supply("back_1",["back"],[],"no equation yet")

class SupplyNetwork:
    def __init__(self,name,supplies):
        self.name = name
        self.supplies = supplies

a = SupplyNetwork("A",[c1,c2,l1,s1,b1])

A1 = Supply("A_1",["A"],["B","C"],"no equation")
B1 = Supply("B_1",["B"],[],"no equation")

ab = SupplyNetwork("AB",[A1,B1])
# return all the types appearing the supply network
def goodTypes(sn):
    return reduce(lambda a, b: frozenset.union(a,b),
                  map(lambda a: frozenset.union(a.inputs,a.outputs),sn.supplies))

goodTypes(a)

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

oneSupply("chair",a)

# This is a somewhat effective paradigm for getting all supplies of a type
next((x for i,x in enumerate(allSupplies("chair",a)) if i==0), None)
next((x for i,x in enumerate(allSupplies("chair",a)) if i==1), None)

# The inputDict maps keys to additional SupplyTrees.
class SupplyTree:
    def __init__(self,supply,inputDict):
        self.supply = supply
        self.inputDict = inputDict
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
            return numerator + '\n' + '-' * charlen + '\n'

# SupplyTree is consistent only if the Supplies in the inputDict match the type

sx = SupplyTree(c1,{"leg": SupplyTree(l1,{}),
                    "seat": SupplyTree(s1,{}),
                    "back": SupplyTree(b1,{})})

def checkConsistency(s):
    for key in s.inputDict:
        if key not in s.inputDict[key].supply.outputs:
            return False
        else:
            return checkConsistency(s.inputDict[key])
    return True

checkConsistency(sx)

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
        print("new supply")
        print(self.supIdx)
        print(len(self.supplies))
        if (self.supIdx >= len(self.supplies)):
            return False
        self.inputToProblemIterator = {}
        for input in self.supplies[self.supIdx].inputs:
            self.inputToProblemIterator[input] = iter(SupplyProblem(input,self.supplyNetwork))
            ## I don't belive this can be correct --- we have to ask ask the SupplyProblem where it stands!!
            ## Or, when we call next on it and we fails, we have to not count that as advancing at all!
            self.inputToBlank[input] = False
        # Really, Pythonistas? This is how you make a ternary expression? (sigh).
        self.inputIdx = 0 if self.supplies[self.supIdx].inputs else None
        # Because we have set a new supIdx, we start with a blank inputToTrees map
        self.inputToTrees = {}
        print("DDD")
        return True
    def __iter__(self):
        self.currentTreesValid = False
        self.supIdx = -1 # This are invalid until we have have a matching supply!
        self.inputIdx = -1 # This is invalid until we have inputs
        self.inputToTrees = {}
        self.inputToProblemIterator = {}
        # This is a boolean that marks if we have produces a tree
        # treating this Problm as missing yet (true); we treating a missing
        # supply tree as the FIRST state of the iteration over the
        # recursively accessed supplyProblems.
        self.inputToBlank = {}
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
            if i in self.inputToTrees and self.inputToTrees[i] is not None:
                d[i] = self.inputToTrees[i]
        return SupplyTree(self.supplies[self.supIdx],d)
    # This the trickiest part. We attempt to iterate the inputIdx
    # problem. If that fails, we move up to the next InputIdx,
    # and start all lower problems over again! If we fail on
    # the final index, we are done, and return false
    # This routine must advance either supIdx or inputIdx or
    # have successfully called next on a subproblem, or established
    # a subproblem which was not in place.
    def advanceExactlyOnce(self):
        print("ADVANCE")
        print(self.inputIdx)
        if (self.inputIdx is not None):
            while (self.inputIdx < len(self.supplies[self.supIdx].inputs)):
                # Incredibly, this is the best way to do it Python (sigh.)
                input = next(x for i,x in enumerate(self.supplies[self.supIdx].inputs) if i==self.inputIdx)
                # if the problem has not yet been created, try to create it
                print("Input:",input)
                if not self.inputToBlank[input]:
                    self.inputToBlank[input] = True
                    print("Set input Blank to True",input)
                    return True
                else:
                    try:
                        print("Calling next on iterator:",input)
                        tree = next(self.inputToProblemIterator[input])
                        self.inputToTrees[input] = tree;
                        print("SUCCESS!")
                        return True
                    except StopIteration:
                        print("EXCEPTION",input)
                        self.inputIdx = self.inputIdx + 1
                        # reset all lower trees and problems
                        print(enumerate(self.supplies[self.supIdx].inputs))
                        for count,input in enumerate(self.supplies[self.supIdx].inputs):
                            if count < self.inputIdx:
                                self.inputToTrees[input] = None
                                self.inputToProblemIterator[input] = iter(SupplyProblem(input,self.supplyNetwork))
                                self.inputToBlank[input] = False
        self.supIdx = self.supIdx + 1
        print("Calling new Supply of advance",self.supIdx)
        return self.newSupply()
    # Note this is made more complicated by the fact that we want
    # to return all solutions, including those which are incomplete...
    # That makes this a little harder to think about.
    def __next__(self):
        print("NEXT: ",self.good,self.currentTreesValid)
        if self.currentTreesValid:
            # If the currentTrees are valid, we want to generate a SupplyTree
            # to return, and then advance our iteration
            currentTree = self.generateCurrentTree()
            # Now we want have to make exactly one iteration.
            # If calling next on a subordinate SupplyProblem works,
            # this is easy. When it fails, we have to move "up".
            # If all fail, we are no longer valid.
            self.currentTreesValid = self.advanceExactlyOnce()
            print("RETURNING",self.good,self.currentTreesValid)
            return currentTree
        else:
            raise StopIteration

# This case is returning no values!

fs = frozenset(["a","b","c"])

next(x for i,x in enumerate(fs) if i==0)

for e in enumerate(frozenset(["a","b"])):
    print(e)

list(SupplyProblem("legx",a))
list(SupplyProblem("leg",a))
print(list(SupplyProblem("leg",a))[0])
print(list(SupplyProblem("chair",a)))
list(SupplyProblem("chair",a))[1]

spci = iter(SupplyProblem("chair",a))
print(next(spci))
print(next(spci))

b_sp = iter(SupplyProblem("B",ab))
ab_sp = iter(SupplyProblem("A",ab))
con_st = next(ab_sp)

for st in list(SupplyProblem("chair",a)):
    print(st)

for st in list(SupplyProblem("A",ab)):
    print(st)

sp = SupplyProblem("chair",a)
i = iter(sp)
print(next((x for i,x in enumerate(SupplyProblem("chair",a)) if i==0), None))
print(next((x for i,x in enumerate(SupplyProblem("chair",a)) if i==1), None))
