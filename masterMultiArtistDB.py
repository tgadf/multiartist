from fileIO import fileIO
from fsUtils import setDir, isFile, isDir, mkDir, setFile
from timeUtils import timestat
from sys import prefix
from pandas import Series
  
class masterMultiArtistDB:
    def __init__(self, install=False, debug=False):
        self.debug = debug
        print("{0} masterMultiArtistDB() {1}".format("="*25,"="*25))
        self.debug  = debug
        
        self.io = fileIO()
        self.multiArtistDir = setDir(prefix, 'multiartist')
        self.initializeData() if install is False else self.installData()
    
    def initializeData(self):
        self.manualMultiArtists = self.getData(fast=True, local=False)
        self.summary()
        
    def installData(self):
        if not isDir(self.multiArtistDir):
            print("Install: Making Prefix Dir [{0}]".format(self.multiArtistDir))
            mkDir(self.multiArtistDir)
        if not isFile(self.getFilename(fast=True, local=False)):
            print("Install: Creating Prefix Data From Local Data")
            self.writeToMainPickleFromLocalYAML()
                        
    def summary(self, manualMultiArtists=None):
        manualMultiArtists = self.manualMultiArtists if manualMultiArtists is None else manualMultiArtists
        print("masterArtistNameDB Summary:")
        print("  Entries: {0}".format(len(manualMultiArtists)))
        #print("  Artists: {0}".format(manualRenames.nunique()))

            
    #########################################################################################################
    #
    # I/O
    #
    #########################################################################################################
    def getFilename(self, fast, local):
        basename="ManualMultiArtists"
            
        self.localpfname = "{0}.p".format(basename)
        self.localyfname = "{0}.yaml".format(basename)
        self.pfname = setFile(self.multiArtistDir, self.localpfname)
        self.yfname = setFile(self.multiArtistDir, self.localyfname)
        
        if fast is True:
            if local is True:
                return self.localpfname
            else:
                return self.pfname
        else:
            if local is True:
                return self.localyfname
            else:
                return self.yfname
            
        raise ValueError("Somehow didn't get a filename!")

    def getData(self, fast=True, local=False):
        ftype = {True: "Pickle", False: "YAML"}
        ltype = {True: "Local", False: "Main"}
        ts = timestat("Getting Manual Renames Data From {0} {1} File".format(ltype[local], ftype[fast]))
        fname = self.getFilename(fast, local)
        manualRenames = self.io.get(fname)

        ts.stop()
    
        return manualRenames

    def writeToLocalYamlFromMainPickle(self):
        ts = timestat("Writing To Local YAML From Main Pickle")
        manualMultiArtists = self.getData(fast=True, local=False)
        self.saveData(manualMultiArtists, fast=False, local=True)
        ts.stop()

    def writeToMainPickleFromLocalYAML(self):
        ts = timestat("Writing To Main Pickle From Local YAML")
        manualMultiArtists = self.getData(fast=False, local=True)
        self.saveData(manualMultiArtists, fast=True, local=False)
        ts.stop()
        
    def saveData(self, manualMultiArtists, fast=True, local=False):
        ftype = {True: "Pickle", False: "YAML"}
        ltype = {True: "Local", False: "Main"}
        ts = timestat("Saving Manual Renames Data To {0} {1} File".format(ltype[local], ftype[fast]))
        #manualMultiArtists = self.manualMultiArtists if manualMultiArtists is None else manualMultiArtists
        #self.summary(manualRenames)
        
        fname = self.getFilename(fast, local)
        if fast:
            toSave = Series(manualMultiArtists) if isinstance(manualMultiArtists, list) else manualMultiArtists
            toSave = toSave.sort_values()
        else:
            toSave = manualMultiArtists.to_list() if isinstance(manualMultiArtists, Series) else manualMultiArtists
        self.io.save(idata=toSave, ifile=fname)
        
        ts.stop()
        
        
    ##########################################################################################
    #
    # Global Getting Function
    #
    ##########################################################################################
    def isMulti(self, artistName):
        return self.manualMultiArtists.__contains__(artistName)

        
    ##########################################################################################
    #
    # Merge
    #
    ##########################################################################################
    def merge(self, newMultiArtists, saveit=True):
        print("Merging New Renames With Master Renames Data")
        newMultiArtists = Series(newMultiArtists) if not isinstance(newMultiArtists, Series) else newMultiArtists
        manualMultiArtists = self.getData(fast=True, local=False)
        print("  Old MultiArtists: {0}".format(len(manualMultiArtists)))
        print("  New MultiArtists: {0}".format(len(newMultiArtists)))
        testMultiArtists = self.manualMultiArtists.append(newMultiArtists)
        print("Merge MultiArtists: {0}".format(len(testMultiArtists)))
        
        testMultiArtists = testMultiArtists.drop_duplicates()
        print("Final MultiArtists: {0}".format(len(testMultiArtists)))
        
        if saveit is True:
            self.saveData(testMultiArtists, fast=True, local=False)
            self.saveData(testMultiArtists, fast=False, local=True)
        else:
            print("Not saving merged multi artists...")