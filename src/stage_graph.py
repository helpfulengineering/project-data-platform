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
        if (self.currentStatus == StageStatus.FAILED):
            return self.curSupply.name
        else:
            for key in self.inputDict:
                thisOneNeedsRepair = self.inputDict[key].nameOfSupplyThatNeedsRepair()
                if thisOneNeedsRepair is not None:
                    return thisOneNeedsRepair
            return None
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

# Now I suppose we should write a function that tells of the order
# is StageGraph is complete, and test by randomly completing orders
# from the bottom up until it is true.

class Order:
    def __init__(self,supplyTree):
        self.supplyTree = supplyTree
        self.stageGraph = StageGraph(self.supplyTree)
