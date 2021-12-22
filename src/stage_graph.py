# stage_graph - Helpful Engineering's Project Data stage_graph (stages of an order)
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

from supply import *
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
        # The history will be list of previous supplyTrees attempted for this
        # node. If this node is changed, the old StageGraph goes into this list
        self.repaired = []
        self.inputDict = {}
        for key in supplyTree.inputDict:
            self.inputDict[key] = StageGraph(key,supplyTree.inputDict[key])
        self.currentStatus = StageStatus.OPEN
    def isComplete(self):
        return self.currentStatus == StageStatus.SUCCEEDED
    def nameOfSupplyThatNeedsRepair(self):
        # This only returns one; we may need a version that returns
        # several, but we need not consider a FAILED node below
        # another node that is FAILED (at least because of a supply!)
        if (self.currentStatus == StageStatus.FAILED):
            return self.curSupply.name
        else:
            for key in self.inputDict:
                thisOneNeedsRepair = self.inputDict[key].nameOfSupplyThatNeedsRepair()
                if thisOneNeedsRepair is not None:
                    return thisOneNeedsRepair
            return None
    def namesOfAllSuppliesThatNeedRepair(self):
        names = []
        if (self.currentStatus == StageStatus.FAILED):
            names.append(self.curSupply.name)
        else:
            for key in self.inputDict:
                allNames = self.inputDict[key].namesOfAllSuppliesThatNeedRepair()
                names += allNames
        return names
    def needsRepair(self):
        return self.nameOfSupplyThatNeedsRepair() is not None
    def assertSupplyStatus(self,supplyName,status):
        if (supplyName == self.curSupply.name):
            self.currentStatus = status
            return True
        else:
            found = False
            for key in self.inputDict:
                foundThisOne = self.inputDict[key].assertSupplyStatus(supplyName,status)
                found = found or foundThisOne
            return found
    def scratch(self,supplyName):
        # A convenience function for "scratching a supplier"
        self.assertSupplyStatus(supplyName,StageStatus.FAILED)
    # Return a (sub) StageGraph based on name
    def findStageGraphByName(self,supplyName):
        # WARNING: It is not entirely clear this is unique.
        if supplyName == self.curSupply.name:
            return self
        else:
            for key in self.inputDict:
                foundThisOne = self.inputDict[key].findStageGraphByName(supplyName)
                if foundThisOne:
                    return foundThisOne
        return None
    def findGoodSuppliedByName(self,supplyName):
        sg = self.findStageGraphByName(supplyName)
        return sg.good
    # Replace the named with a new supply, and set the status to open
    # This returns
    def repair(self,supplyName,newSupplyTree):
        # First find if if the supplyName exists
        if (supplyName == self.curSupply.name):
            self.repaired.append(self)
            self.curSupply = newSupplyTree.supply
            for key in newSupplyTree.inputDict:
                self.inputDict[key] = StageGraph(key,newSupplyTree.inputDict[key])
            self.currentStatus = StageStatus.OPEN
            return True
        else:
            found = False
            for key in self.inputDict:
                foundThisOne = self.inputDict[key].repair(supplyName,newSupplyTree)
                found = found or foundThisOne
            return found
    def applySub(self,sub,sn):
        good = self.findGoodSuppliedByName(sub.a)
        sts = list(SupplyProblem(good,sn).CompleteSupplyTrees())
        if (len(sts) > 1):
            print("warning! an arbitrary decisions is being made by applySub")
        if (len(sts) >= 0): # nothing to do
            st = sts[0]
            self.repair(sub.a,st)
    def applySubs(self,subs,sn):
        for s in subs:
            applySub(s,sn)
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

# This is just a formalization of a structure that replaces
# one symbol with another for clarity. The symbol package
# deals this this as a list of tuples; that might be better.
# This means that name_b is substituted in for name_a
class SubstSupply:
    def __init__(self,name_a,name_b):
        self.a = name_a
        self.b = name_b
    def __str__(self):
        return self.a + "->" + self.b




# Return a list of substitutions
def findAllSubstitutions(sn,sg):
    # Return all complete substitutions possible from the sn network in the sg
    # This may be an expensive operation.
    # A basic approach is to find all highest-level failures,
    # and then just compute all supplyTrees for that good that we can,
    # and construct substitutions for that.
    subs = []
    highestLevelNeeedsRepair = sg.namesOfAllSuppliesThatNeedRepair()
    for nm in highestLevelNeeedsRepair:
        # Now we need to find the good associated with this name
        # in the stage_graph
        good = sg.findGoodSuppliedByName(nm)
        sp = SupplyProblem(good,sn)
        for st in list(sp.completeSupplyTrees()):
            subs.append(SubstSupply(nm,st.supply.name))
    return subs



# Now I suppose we should write a function that tells if the order
# is StageGraph is complete, and test by randomly completing orders
# from the bottom up until it is true.

class Order:
    def __init__(self,good,supplyTree):
        self.supplyTree = supplyTree
        self.stageGraph = StageGraph(good,self.supplyTree)
    def findOneOPEN(self,sg):
        # Advance the first element that is not OPEN
        # (assume none of the nodes are FAILED, i.e., it is repaird)
        # If there is no such element, return null. This should be a
        # DEEPEST such element
        oneThatIsOpen = None
        for key in sg.inputDict:
            oneThatIsOpen = self.findOneOPEN(sg.inputDict[key])
            if oneThatIsOpen is not None:
                return oneThatIsOpen
        if sg.currentStatus == StageStatus.OPEN:
            return sg
        else:
            return None
    def advanceOne(self):
        # return a StageGraph if we succeed, None if we do not
        sg = self.findOneOPEN(self.stageGraph)
        if (sg is not None):
            sg.currentStatus = StageStatus.SUCCEEDED
            return sg
        else:
            return None

# Functions operating on lists of sgs
def scratch(sgs,sn):
    for sg in sgs:
        for s in sn.supplies:
            sg.scratch(s.name)



# This is a deep one: We look for anything we can repair and apply it,
# producing new stage graphs.
def repair(sgs,sn):
    repaired = []
    for s in sgs:
        subs = findAllSubstitutions(sn,s)
        if subs is None:
            repaired.append(s)
        else:
            new_s = s.applySubs(subs)
            repaired.append(new_s)
    return repaired
