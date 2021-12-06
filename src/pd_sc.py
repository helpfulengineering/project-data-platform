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

oneSupply("chair",a)
