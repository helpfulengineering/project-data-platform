# okf - Helpful Engineering's Project Data okf (Open Know Framework)
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

# Now attempting to model a OKH and OKW class, though we may make these
# more generic. An important aspect is that these should be able to
# read the YAML definitions of those objects as imports. However,
# we will postpone implementing that.

# The basic concept is that an OKW can produce a Supply for a good
# if it there is an OKH for it and it has the tooling (which we
# will not attempt to represent perfectly at first.) A collection
# of OKWs and OKHs then becomes a SupplyNetwork, or can produce
# Supply objects to be added to some other SupplyNetwork.
from supply import *

import yamale

class OKH:
    # At first this looks ridiculously like a supply, but
    # over time we will provide other methods
    def __init__(self,name = None,outputs = [],inputs = [],requiredTooling = [],eqn = "no eqn yet"):
        self.name = name
        self.outputs = frozenset(outputs)
        self.inputs = frozenset(inputs)
        self.requiredTooling = frozenset(requiredTooling)
        self.eqn = eqn
    def fromFile(self,filename):
        okh_yml = yamale.make_data(filename)
        main = okh_yml[0][0]
        self.name = main["title"]
        if "bom" in main:
            self.inputs = main["bom"].split(',')
        else:
            self.inputs = None
        self.outputs = main["title"]
        if "tool-list" in main:
            self.requiredTooling = main["tool-list"].split(',')
        else:
            self.requiredTooling = None
        return self

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


# Here are a nubmer of .yml files.
# We are now undertaking issue #4: https://github.com/helpfulengineering/project-data-platform/issues/4
# And will attempt to read in files like this:
# https://github.com/helpfulengineering/library/tree/main/alpha/okh
# Useful files are:
# okh-manifest-surge-english.yml

def slurpOKH(filename):
#    schema = yamale.make_schema('./schema.yaml')
    okh = yamale.make_data(filename)
    return okh
