from serpentTools.settings import rc


class BaseReader(object):
    """Parent class from which all parsers will inherit.

    Parameters
    ----------
    filePath: str
        path pointing towards the file to be read
    readerSettingsLevel: str or list
        type of reader. Determines which settings to obtain
    """

    def __init__(self, filePath, readerSettingsLevel):
        self.filePath = filePath
        self.metadata = {}
        if isinstance(readerSettingsLevel, str):
            self.settings = rc.getReaderSettings(readerSettingsLevel)
        else:
            self.settings = {}
            for level in readerSettingsLevel:
                self.settings.update(rc.getReaderSettings(level))

    def __str__(self):
        return '<{} reading {}>'.format(self.__class__.__name__, self.filePath)

    def read(self):
        """Read the file and store the data.

        :warning:

            This read function has not been implemented yet

        """
        raise NotImplementedError


class MaterialReader(BaseReader):
    """Parent class for files that store materials."""

    def __init__(self, filePath, readerSettingsLevel):
        BaseReader.__init__(self, filePath, readerSettingsLevel)
        self.materials = {}

    def read(self):
        raise NotImplementedError


class XSReader(BaseReader):
    """Parent class for the branching and results reader"""

    def __init__(self, filePath, readerSettingsLevel):
        BaseReader.__init__(self, filePath, ['xs', readerSettingsLevel])
        self.settings['variables'] = rc.expandVariables()
        self.settings.pop('variableGroups')
        self.settings.pop('variableExtras')

    def read(self):
        raise NotImplementedError

    def _checkAddVariable(self, variableName):
        """Check if the data for the variable should be stored"""
        # no variables given -> get all
        if not any(self.settings['variables']):
            return True
        # explicitly named
        if variableName in self.settings['variables']:
            return True
        if (self.settings['getB1XS'] and variableName.replace('B1_', '') in
                self.settings['variables']):
            return True
        if (self.settings['getInfXS'] and variableName.replace('INF_', '') in
                self.settings['variables']):
            return True
        return False
