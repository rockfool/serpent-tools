"""Parser responsible for reading the ``*coe.m`` files"""

from six import iteritems
from numpy import array

from serpentTools.objects import splitItems
from serpentTools.objects.containers import BranchContainer
from serpentTools.objects.readers import XSReader
from serpentTools.messages import debug, info


class BranchingReader(XSReader):
    """
    Parser responsible for reading and working with automated branching files.

    Parameters
    ----------
    filePath: str
        path to the depletion file
    """

    def __init__(self, filePath):
        XSReader.__init__(self, filePath, 'branching')
        self.__fileObj = None
        self.branches = {}
        self._whereAmI = {key: None for key in
                          {'runIndx', 'coefIndx', 'buIndx', 'universe'}}

    def read(self):
        """Read the branching file and store the coefficients."""
        info('Preparing to read {}'.format(self.filePath))
        with open(self.filePath) as fObj:
            self.__fileObj = fObj
            while self.__fileObj is not None:
                self._processBranchBlock()
        info('Done reading branching file')

    def _advance(self, possibleEndOfFile=False):
        if self.__fileObj is None:
            raise IOError("Attempting to read on file that has been closed.\n"
                          "Parser: {}\nFile: {}".format(self, self.filePath))
        line = self.__fileObj.readline()
        if line == '':
            if possibleEndOfFile:
                self.__fileObj = None
                return None
            raise EOFError('Unexpected end of file {}'.format(self.filePath))
        return line.split()

    def _processBranchBlock(self):
        fromHeader = self._processHeader()
        if fromHeader is None:
            return
        thisBranch, totUniv = fromHeader
        burnup, burnupIndex = self._advance()[:-1]
        self._whereAmI['buIndx'] = int(burnupIndex)
        for univNum in range(totUniv):
            self._whereAmI['universe'] = univNum
            debug(
                'Reading run {runIndx} of {coefIndx} - universe {universe} at '
                'burnup step {buIndx}'.format(**self._whereAmI))
            self._processBranchUniverses(thisBranch, float(burnup),
                                         self._whereAmI['buIndx'])

    def _processHeader(self):
        """Read over all data up to universe loop."""
        header = self._advance(possibleEndOfFile=True)
        if header is None:
            return
        indx, runTot, coefIndx, totCoef, totUniv = header
        self._whereAmI['runIndx'] = int(indx)
        self._whereAmI['coefIndx'] = int(coefIndx)
        branchNames = tuple(self._advance()[1:])
        if branchNames not in self.branches:
            branchState = self._processBranchStateData()
            self.branches[branchNames] = (
                BranchContainer(self, coefIndx, branchNames, branchState))
        else:
            self._advance()
        return self.branches[branchNames], int(totUniv)

    def _processBranchStateData(self):
        keyValueList = self._advance()[1:]
        stateData = {}
        mappings = {'intVariables': int, 'floatVariables': float}

        for keyIndex in range(0, len(keyValueList), 2):
            key, value = keyValueList[keyIndex: keyIndex + 2]
            stateData[key] = value
            for mapKey, mapFunc in mappings.items():
                if key in self.settings[mapKey]:
                    stateData[key] = mapFunc(value)
                    break
        return stateData

    def _processBranchUniverses(self, branch, burnup, burnupIndex):
        """Add universe data to this branch at this burnup."""
        unvID, numVariables = [int(xx) for xx in self._advance()]
        univ = branch.addUniverse(unvID, burnup, burnupIndex)
        for step in range(numVariables):
            splitList = self._advance(possibleEndOfFile=step == numVariables-1)
            varName = splitList[0]
            varValues = [float(xx) for xx in splitList[2:]]
            if self._checkAddVariable(varName):
                if self.settings['areUncsPresent']:
                    vals, uncs = splitItems(varValues)
                    univ.addData(varName, array(vals), uncertaity=False)
                    univ.addData(varName, array(uncs), unertainty=True)
                else:
                    univ.addData(varName, array(varValues), uncertainty=False)

    def iterBranches(self):
        """Iterate over branches yielding paired branch IDs and containers"""
        for bID, b in iteritems(self.branches):
            yield bID, b
