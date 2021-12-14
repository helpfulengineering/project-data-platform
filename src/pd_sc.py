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
from sympy import *

import pprint

# Note: I'm using the name eqn, here but possibly
# an expression is better (but in any case we will use the SymPy pacakges.
# Note an invariant (currently unchecked) is that the eqn should have the same number
# of sybols as the inputs (or that + 1) and the names should match.
# It would be better if we asserted that cleanly
class Supply:
    def __init__(self,name,outputs,inputs,eqn):
        self.name = name
        self.inputs = frozenset(inputs)
        self.outputs = frozenset(outputs)
        self.eqn = eqn




# A vary basic set of supplies...

# We will first create "symbols" (similar to Intern with LISP)
chair,leg,seat,back = symbols("chair leg seat back")
fabric,plane = symbols("fabric plane")
frame,stuffing = symbols("frame stuffing")
upholstery = symbols("upholstery")

# These are more or "supplier" constants
chair_1,chair_2,leg_1,seat_1,seat_2,seat_3 = symbols("chair_1 chair_2 leg_1 seat_1 seat_2 seat_3")
back_1,fabric_1,plane_1 = symbols("back_1 fabric_1 plane_1")
stuffing_1 = symbols("stuffing_1")

# This makes more sense as a dictionary;
# However, the SymPy package uses a list of pairs (symbol, expression).
price_map = [(chair_1,4),
             (chair_2,3),
             (leg_1,1),
             (seat_1,2),
             (seat_2,2),
             (seat_3,3),
             (back_1,3),
             (fabric_1,1),
             (plane_1,1),
             (stuffing_1,2)]


# Possibly we should create anonymous supply signatures...
# These are effectively hard-coded OKH elements; we may
# eventually have a way to import OKHs.
# TODO: Shift seat to "Frame, stuffing, upholstery"
# TODO: Shift to a mask
c1 = Supply("chair_1",["chair"],["leg","seat","back"],chair_1 + 4*leg + seat + back)
c2 = Supply("chair_2",["chair"],["leg","seat","back"],chair_2 + 4*leg + seat + back)
l1 = Supply("leg_1",["leg"],[],leg_1)
s1 = Supply("seat_1",["seat"],[],seat_1)
s2 = Supply("seat_2",["seat"],["fabric","plane"],seat_2 + fabric + plane)
s3 = Supply("seat_3",["seat"],["frame","stuffing","upholstery"],seat_3 + frame + stuffing + upholstery)
ss1 = Supply("stuffing_1",["stuffing"],[],stuffing_1)
b1 = Supply("back_1",["back"],[],back_1)
f1 = Supply("fabric_1",["fabric"],[],fabric_1)
p1 = Supply("plane_1",["plane"],[],plane_1)

class SupplyNetwork:
    def __init__(self,name,supplies):
        self.name = name
        self.supplies = supplies

def unionSupplyNetworks(a,b):
    return SupplyNetwork(a.name + "|" + b.name,a.supplies + b.supplies)

a = SupplyNetwork("A",[c1,c2,l1,s1,b1,s2,f1,p1,s3,ss1])

A,B,C,X,Y = symbols("A B C X Y")
A_1,B_1,C_1,X_1,Y_1 = symbols("A_1 B_1 C_1 X_1 Y_1")

A1 = Supply("A_1",["A"],["B","C"],A_1 + B + C )
B1 = Supply("B_1",["B"],[],B_1)
C1 = Supply("C_1",["C"],[],C_1)

X1 = Supply("X_1",["X"],["Y"],X_1+Y)
Y1 = Supply("Y_1",["Y"],[],Y_1)

xy = SupplyNetwork("XY",[X1,Y1])

ab = SupplyNetwork("AB",[A1,B1])
abc = SupplyNetwork("ABC",[A1,B1,C1])
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

# SupplyTree is consistent only if the Supplies in the inputDict match the type

sx = SupplyTree(c1,{"leg": SupplyTree(l1,{}),
                    "seat": SupplyTree(s1,{}),
                    "back": SupplyTree(b1,{})})

# TODO: We could add Equational consistency to this
def checkConsistency(supplyTree):
    for key in supplyTree.inputDict:
        if key not in supplyTree.inputDict[key].supply.outputs:
            return False
        else:
            return checkConsistency(supplyTree.inputDict[key])
    return True

checkConsistency(sx)

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


for st in list(SupplyProblem("chair",a)):
    print(st)

len(list(iter(SupplyProblem("chair",a))))

for st in list(SupplyProblem("A",ab)):
    print(st)

abc_sp = iter(SupplyProblem("A",abc))
for st in list(SupplyProblem("A",abc)):
    print(st)

for st in list(SupplyProblem("X",xy)):
    print(st)
for st in list(SupplyProblem("Y",xy)):
    print(st)

xyi = iter(SupplyProblem("X",xy))

sp = SupplyProblem("chair",a)
i = iter(sp)
print(next((x for i,x in enumerate(SupplyProblem("chair",a)) if i==0), None))
print(next((x for i,x in enumerate(SupplyProblem("chair",a)) if i==1), None))


# Print only those SupplyTrees which are complete in the "chair" problem
for st in list(SupplyProblem("chair",a).completeSupplyTrees()):
    print(st)
    print(characteristicExpression(st))
    print(characteristicExpression(st).subs(price_map))

print(SupplyProblem("chair",a).optimalCompleteSupplyTreeByPrice(price_map))


# Now attempting to model a OKH and OKW class, though we may make these
# more generic. An important aspect is that these should be able to
# read the YAML definitions of those objects as imports. However,
# we will postpone implementing that.

# The basic concept is that an OKW can produce a Supply for a good
# if it there is an OKH for it and it has the tooling (which we
# will not attempt to represent perfectly at first.) A collection
# of OKWs and OKHs then becomes a SupplyNetwork, or can produce
# Supply objects to be added to some other SupplyNetwork.

class OKH:
    # At first this looks ridiculously like a supply, but
    # over time we will provide other methods
    def __init__(self,name,outputs,inputs,requiredTooling,eqn):
        self.name = name
        self.outputs = frozenset(outputs)
        self.inputs = frozenset(inputs)
        self.requiredTooling = frozenset(requiredTooling)
        self.eqn = eqn

class OKW:
    def __init__(self,name,toolingGoods):
        self.name = name
        self.tooling = frozenset(toolingGoods)
    def hasToolingFor(self,okh):
        # This is over simple, but we will just require that
        # all requiredTooling be in our tooling
        for tool in okh.requiredTooling:
            if tool not in self.tooling:
                return False
        return True



# And OKF is a collection of OKHs and OKWs which in particular
# allows you to compute Supplies
class OKF:
    def __init__(self,name,okhs,okws):
        self.name = name
        self.okhs = okhs
        self.okws = okws
    def supplies(self):
        # Roughly speaking we can produce a Supply named by
        # the okw,good pair whenever the okw has the "tooling"
        # for the okh.
        ss = []
        for w in self.okws:
            for h in self.okhs:
                if w.hasToolingFor(h):
                    name = w.name + "|" + h.name
                    ss.append(Supply(name,h.outputs,h.inputs,h.eqn))
        return ss

okh1 = OKH("SurgeMask",["mask"],["NWPP","coffee_tin_ties","fabric_ties"],["sewing_machine"],"no eqn yet")

okw1 = OKW("NearJames",["sewing_machine"])

okf1 = OKF("okf1",[okh1],[okw1])

# Now create a SupplyNetwork from the okf, and union it with
# our non-OKF supplies..

okf_sn = SupplyNetwork("fromOKF",okf1.supplies())
combined = unionSupplyNetworks(a,okf_sn)

for st in list(SupplyProblem("mask",okf_sn)):
    print(st)

# Now beginning working on the order concept
# A basic approach is that a an order can be generated from a SupplyTree,
# in that a StageGraph is very similar to a Supply Tree.
# A StageGraph can be considered a SupplyTree decorated by human assertions and
# boolean conditions. The fundamental operations on a StageGraph
# are to advance conditions with assertions, and to compute what needs
# to be advanced. Our eventual goal is to be able to repair and order
# by changing the SupplyTree in some way. So our new types are:
# StageAssertion
# StageGraph
# Order

from enum import Enum
class StageStatus(Enum):
    OPEN = 0
    SUCCEEDED  = 1
    FAILED = 2


class StageGraph:
    def __init__(self,good,supplyTree):
        # Now we want to do a deep copy of the supplyTree,
        # but add in a decoration. We could make this recursive, so we are doing
        # it all at each level. I suppose that is best.
        # However, a StageGraph has a history, in a way that a SupplyTree doesn't.
        self.curSupply = supplyTree.supply
        self.good = good
        # The history will be a dictionary that maps inputs to lists of
        # StageGraphs. They have to be list to handle the case of the same
        # input failing multiple times
        self.repaired = {}
        self.inputDict = {}
        for key in supplyTree.inputDict:
            self.inputDict[key] = StageGraph(key,supplyTree.inputDict[key])
        self.currentStatus = StageStatus.OPEN
    def assertSupplyStatus(self,supplyName,status):
        if (supplyName == self.curSupply.name):
            self.currentStatus = status
            return True
        else:
            for key in self.inputDict:
                self.inputDict[key].assertSupplyStatus(supplyName,status)
    def __str__(self):
        # if the inputDict is empty, we can render without a line!
        numerator = self.curSupply.name + "/" + str(self.currentStatus.name)
        if (self.repaired):
            numerator = numerator + " REPAIRED"
        if (self.inputDict):
            subtrees = "".join(map(str,self.inputDict.values()))
            labels = []
            for (k, v) in iter(self.inputDict.items()):
                labels.append(k + ':' + str(v.curSupply.name))
            denominator = ",".join(labels)
            charlen = max(len(denominator),len(numerator))
            numdiff = max(charlen - len(numerator),0)//2
            demdiff = max(charlen - len(denominator),0)//2
            return ' ' * numdiff + numerator + '\n' + '-' * charlen + '\n' + ' ' * demdiff + denominator + '\n' + subtrees
        else:
            charlen = len(numerator)
            return numerator + '\n' + '=' * charlen + '\n'


sg = StageGraph("chair",sx)
sg.assertSupplyStatus("back_1",StageStatus.FAILED)
print(sg)





class Order:
    def __init__(self,supplyTree):
        self.supplyTree = supplyTree
        self.stageGraph = StageGraph(self.supplyTree)
