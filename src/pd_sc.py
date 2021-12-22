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
from supply import *

# A vary basic set of supplies...

# We will first create "symbols" (similar to Intern with LISP)
chair,leg,seat,back = symbols("chair leg seat back")
fabric,plane = symbols("fabric plane")
frame,stuffing = symbols("frame stuffing")
upholstery = symbols("upholstery")

# These are more or "supplier" constants
chair_1,chair_2,leg_1,seat_1,seat_2,seat_3 = symbols("chair_1 chair_2 leg_1 seat_1 seat_2 seat_3")
back_1,fabric_1,plane_1 = symbols("back_1 fabric_1 plane_1")
fabric_2 = symbols("fabric_2")
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
f2 = Supply("fabric_2",["fabric"],[],fabric_2)
p1 = Supply("plane_1",["plane"],[],plane_1)

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

goodTypes(a)

oneSupply("chair",a)

# This is a somewhat effective paradigm for getting all supplies of a type
next((x for i,x in enumerate(allSupplies("chair",a)) if i==0), None)
next((x for i,x in enumerate(allSupplies("chair",a)) if i==1), None)

# SupplyTree is consistent only if the Supplies in the inputDict match the type

sx = SupplyTree(c1,{"leg": SupplyTree(l1,{}),
                    "seat": SupplyTree(s1,{}),
                    "back": SupplyTree(b1,{})})


checkConsistency(sx)

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

print(SupplyProblem("chair",a).optimalCompleteSupplyTreeByPrice(price_map)[0])


from okf import *

okh1 = OKH("SurgeMask",["mask"],["NWPP","coffee_tin_ties","fabric_ties"],["sewing_machine"],"no eqn yet")

okw1 = OKW("NearJames",["sewing_machine"])

okf1 = OKF("okf1",[okh1],[okw1])

# Now create a SupplyNetwork from the okf, and union it with
# our non-OKF supplies..

okf_sn = SupplyNetwork("fromOKF",okf1.supplies())
combined = unionSupplyNetworks(a,okf_sn)

for st in list(SupplyProblem("mask",okf_sn)):
    print(st)

from stage_graph import *

sgc = StageGraph("chair",sx)
sgc.assertSupplyStatus("seat_1",StageStatus.FAILED)
print(sgc.isComplete())
print(sgc.needsRepair())
print(sgc.nameOfSupplyThatNeedsRepair())

st_seat_1 = SupplyTree(s1,{"fabric": SupplyTree(f1,{}),
                           "plane": SupplyTree(p1,{})})
st_seat_2 = SupplyTree(s2,{"fabric": SupplyTree(f1,{}),
                           "plane": SupplyTree(p1,{})})

st_fabric_2 = SupplyTree(f2,{})

sg = StageGraph("seat",st_seat_2)
sg.repair("fabric_1",st_fabric_2)
print(st_seat_2)

sgc = StageGraph("chair",sx)
sgc.repair("seat_1",st_seat_2)
print(sgc)

o1 = Order("chair",sx)

import unittest

# This code assumes the existence of our "standard" symbols from supply
class TestOrder(unittest.TestCase):
    def test_canAdvanceOrderToCompletion(self):
        sx = SupplyTree(c1,{"leg": SupplyTree(l1,{}),
                            "seat": SupplyTree(s1,{}),
                            "back": SupplyTree(b1,{})})
        o1 = Order("chair",sx)
        sg = o1.advanceOne()
        while(sg is not None):
            sg = o1.advanceOne()
        self.assertTrue(o1.stageGraph.isComplete())

unittest.main(exit=False)
