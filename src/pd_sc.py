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

# SupplyTree is consistent only if the Supplies in the inputDict match the type

sx = SupplyTree(c1,{"leg": SupplyTree(l1,{}),
                    "seat": SupplyTree(s1,{}),
                    "back": SupplyTree(b1,{})})

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
import copy
# our basic goal here is to create a bifurcated supply network:
# C = A union B, where A intersect B = 0.
# For every good, we want to show:
# repair(scratch(A,CT(C)),A) = CT(C),
# where CT(C) = the CompleteTrees of C.
# WARNING: this assumes these symbols have been defined!
# This code assumes the existence of our "standard" symbols from supply
class TestStageGraph(unittest.TestCase):
    def test_canScratchAWholeNetwork(self):
        print("BBB")
        # our basic goal here is to create a bifurcated supply network:
        # C = A union B, where A intersect B = 0.
        # For every good, we want to show:
        # repair(scratch(A,CT(C)),A) = CT(C),
        # where CT(C) = the CompleteTrees of C.
        # WARNING: this assumes these symbols have been defined!
        a = SupplyNetwork("A",[c1,l1,s1,b1,f1])
        b = SupplyNetwork("B",[c2,s2,s3,ss1,p1])
        c = unionSupplyNetworks(a,b)
        gs = goodTypes(c)
        gsa = goodTypes(a)
        gsb = goodTypes(b)
        for g in gs:
            sp_c = SupplyProblem(g,c)
            cts_c = sp_c.completeSupplyTrees()
            sgs_c = list(map(lambda t: StageGraph(g,t),cts_c))
            sgs_c = copy.deepcopy(sgs_c)
            scratch(sgs_c,a)
            cnt = 0;
            for s in sgs_c:
                needs = s.nameOfSupplyThatNeedsRepair()
                if needs:
                    cnt += 1
            if g in gsb and g not in gsa:
                # in this case we were NOT scratched,
                # so there should be zero repairs
                self.assertEqual(cnt,0)
            else:
                self.assertEqual(cnt,len(list(sp_c.completeSupplyTrees())))
    def test_canGetMultipleRepairableNodes_AndFindSubstituions(self):
        print("AAAX")
        sx = SupplyTree(c1,{"leg": SupplyTree(l1,{}),
                            "seat": SupplyTree(s1,{}),
                            "back": SupplyTree(b1,{})})
        sgc = StageGraph("chair",sx)
        sgc.scratch("leg_1")
        sgc.scratch("seat_1")
        nms = sgc.namesOfAllSuppliesThatNeedRepair()
        self.assertEqual(len(nms),2)
        scratched = copy.deepcopy(a)
        scratched.scratch("leg_1")
        scratched.scratch("seat_1")
        subs = findAllSubstitutions(scratched,sgc)
        self.assertEqual(len(subs),1)
        self.assertEqual(subs[0].a,"seat_1")
    def test_bifurcatedSupplyNetworksAreFullyRepairable(self):
        print("CCC")
        a = SupplyNetwork("A",[c1,l1,s1,b1,f1,p1,ss1])
        b = SupplyNetwork("B",[c2,s2,s3,ss1])
        c = unionSupplyNetworks(a,b)
        gs = goodTypes(c)
        for g in gs:
            ca = copy.deepcopy(a)
            sp_c = SupplyProblem(g,c)
            cts_c = sp_c.completeSupplyTrees()
            sp_a = SupplyProblem(g,a)
            cts_a = sp_a.completeSupplyTrees()
            sgs_a = list(map(lambda t: StageGraph(g,t),cts_a))
            sgs_c = list(map(lambda t: StageGraph(g,t),cts_c))
            scratch(cts_a,a)
            print("QQQ")
            print(cts_a)
            # We reapair by the same thing we scratched by, to get
            # a full repair!
            a_repaired_sgs = repair(sgs_a,a)
            print("spud")
            print(a_repaired_sgs)
            print(sgs_a)
            self.assertEqual(len(a_repaired_sgs),len(sgs_a))

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

import copy
scratched = copy.deepcopy(a)
scratched.scratch("leg_1")
for s in scratched.supplies:
    print(s)

if __name__ == '__main__':
    unittest.main(exit=False)
