from searchUtils import findNearest
from ioUtils import getFile
import hashlib
from masterMultiArtistDB import masterMultiArtistDB
  
class multiartist:
    def __init__(self, cutoff=0.9, discdata=None, exact=False):
        self.cutoff   = cutoff    
        self.discdata = discdata
        self.exact    = exact
        self.debug    = False
        
        self.uberdelims  = [" ::: "]
        self.basicdelims = ["Duet With", "Presents", "Featuring"]
        self.delims      = ["Duet With", "Presents", "Featuring", ",", "&", " And ", "+", "/", "With The", " with ", " With ", " y ", " Y ", " feat.",  " ft.", " Feat. ", " x ", " X ", " Ft. ", " VS. ", " VS ", " Vs ", " vs. ", " Vs. ", " × ", " featuring ", " Feturing ", " Meets "]
        self.discArtists = []

        self.masks = {}
        self.setKnownMultiDelimArtists()
        
        old="""
        if self.discdata is not None:
            self.discArtists = [x for x in discdata.keys() if x is not None]
        self.knownDelimArtists = {artist: True for artist in self.discArtists if self.nDelims(artist) > 0}
        
        self.knownMultiDelimArtists = []
        """
        
        
    def setKnownMultiDelimArtists(self):        
        self.mmadb    = masterMultiArtistDB()
        self.knownMultiDelimArtists = self.mmadb.getData()
        
        for i,artist in enumerate(self.knownMultiDelimArtists):
            if len(artist) == 0:
                raise ValueError("Artist has no length in masking")
            #print(i,'/',len(self.knownMultiDelimArtists),'\t',artist)
            result = hashlib.md5(artist.encode()) 
            if self.masks.get(artist) is not None:
                raise ValueError("There is an error with masking artist {0}".format(artist))            
            self.masks[artist] = result.hexdigest()
            if self.masks.get(result.hexdigest()) is not None:
                raise ValueError("There is an error with masking artist {0}".format(artist))
            self.masks[result.hexdigest()] = artist
            
        if self.debug:
            print("Adding {0} known multi delim artists.".format(len(self.knownMultiDelimArtists)))
        
        
    
    def getDiscArtists(self):
        return self.discArtists
    
    def getKnownDelimArtists(self):
        return self.knownDelimArtists  
    
    def isKnownArtist(self, artist):
        if isinstance(self.discdata, dict):
            return self.discdata.get(artist) != None
        return False
    
    def nDelims(self, artist):
        return sum([x in artist for x in self.delims])
    
    
    def getDelimData(self, val):
        valdata = {d: [x.strip() for x in val.split(d)] for d in self.delims if d in val}
        return valdata
    
    
    def getBasicDelimData(self, val):
        valdata = {d: [x.strip() for x in val.split(d)] for d in self.basicdelims if d in val}
        return valdata

    def getNdelims(self, val):
        return len(val)

    def addArtist(self, allArtists, val, debug=False, reason=None):
        #print("L={0}".format(len(allArtists)))
        if allArtists.get(val) is None:
            if debug:
                print("Adding {0}. Sum is {1}".format(val, len(allArtists)))
                if reason is not None:
                    print("  Reason: {0}".format(reason))
            allArtists[val] = True
    
    
    def cleanArtist(self, artist):
        artist = artist.replace("(", "")
        artist = artist.replace(")", "")
        return artist


    def newMethod(self, artist, debug=False):
        allArtists = {}
        if debug:
            print("Finding Artists Within: {0}".format(artist))
        
        ##############################################################################
        ## Quick check to see if artist is a known problem for the algorithm
        ##############################################################################
        if artist in self.knownMultiDelimArtists and False:
            self.addArtist(allArtists, artist, debug, "Known Artist")
            knownArtists = set(allArtists.keys())
            return self.combineResults(allArtists, knownArtists, debug)
        
        
        ##############################################################################
        ## Mask Multi Artists
        ##############################################################################
        for check in self.knownMultiDelimArtists:
            if artist.find(check) != -1:
                if debug:
                    print("  Found Known Artist {0} Within {1}".format(check, artist))
                artist = artist.replace(check, self.masks[check])
                if debug:
                    print("     Artist --> {0}".format(artist))
        
        
        ##############################################################################
        ## Uber Delim Artists
        ##############################################################################
        for check in self.uberdelims:
            if artist.find(check) != -1:
                if debug:
                    print("  Found Known Artist {0} Within {1}".format(check, artist))
                for uname in artist.split(check):
                    self.addArtist(allArtists, uname, debug, "Known Uber Artist")
                knownArtists = set(allArtists.keys())
                return self.combineResults(allArtists, knownArtists, debug)

        
        
        ##############################################################################
        ## Clean Artist And Set 1st Order Delims
        ##############################################################################
        artist = self.cleanArtist(artist)
        d1delims = self.getBasicDelimData(artist)
        if len(d1delims) == 0:
            d1delims = self.getDelimData(artist)
        if debug:
            print('1','\t',artist,'===>',d1delims)

        knownArtists = set()
        if len(d1delims) == 0:
            self.addArtist(allArtists, artist, debug, "No D1 Delims")
            knownArtists = set(allArtists.keys())
        elif self.isKnownArtist(artist):
            self.addArtist(allArtists, artist, debug, "Known Delims")
            knownArtists = set(allArtists.keys())
            d1delims = {}


        ##############################################################################
        ## 1st Delimiter Split
        ##############################################################################
        for delim1, delimdata1 in d1delims.items():
            delimdata1 = list(set(delimdata1).difference(knownArtists))
            for artist1 in delimdata1:
                d2delims = self.getDelimData(artist1)
                if debug:
                    print('2','\t',artist1,'===>',d2delims)
                if self.getNdelims(d2delims) == 0:
                    self.addArtist(allArtists, artist1, debug)
                    knownArtists = set(allArtists.keys())
                    continue
                elif self.isKnownArtist(artist1):
                    self.addArtist(allArtists, artist1, debug)
                    knownArtists = set(allArtists.keys())
                    d2delims = {}

                    
                ##############################################################################
                ## 2nd Delimiter Split
                ##############################################################################
                for delim2, delimdata2 in d2delims.items():
                    delimdata2 = list(set(delimdata2).difference(knownArtists))
                    for artist2 in delimdata2:
                        d3delims = self.getDelimData(artist2)
                        if debug:
                            print('3','\t',artist2,'===>',d3delims)
                        if self.getNdelims(d3delims) == 0:
                            self.addArtist(allArtists, artist2)
                            knownArtists = set(allArtists.keys())
                            continue
                        elif self.isKnownArtist(artist2):
                            self.addArtist(allArtists, artist2)
                            knownArtists = set(allArtists.keys())
                            d3delims = {}

                            
                        ##############################################################################
                        ## 3rd Delimiter Split
                        ##############################################################################
                        for delim3, delimdata3 in d3delims.items():
                            delimdata3 = list(set(delimdata3).difference(knownArtists))
                            for artist3 in delimdata3:
                                d4delims = self.getDelimData(artist3)
                                if self.getNdelims(d4delims) == 0:
                                    self.addArtist(allArtists, artist3)
                                    knownArtists = set(allArtists.keys())
                                    continue
                                elif self.isKnownArtist(artist3):
                                    self.addArtist(allArtists, artist3)
                                    knownArtists = set(allArtists.keys())
                                    d4delims = {}
                                    

                                ##############################################################################
                                ## 4th Delimiter Split
                                ##############################################################################
                                for delim4, delimdata4 in d4delims.items():
                                    delimdata4 = list(set(delimdata4).difference(knownArtists))
                                    for artist4 in delimdata4:
                                        d5delims = self.getDelimData(artist4)
                                        if self.getNdelims(d5delims) == 0:
                                            self.addArtist(allArtists, artist4)
                                            knownArtists = set(allArtists.keys())
                                            continue
                                        elif self.isKnownArtist(artist4):
                                            self.addArtist(allArtists, artist4)
                                            knownArtists = set(allArtists.keys())
                                            d5delims = {}


                                        ##############################################################################
                                        ## 5th Delimiter Split
                                        ##############################################################################
                                        for delim5, delimdata5 in d5delims.items():
                                            delimdata5 = list(set(delimdata5).difference(knownArtists))
                                            for artist5 in delimdata5:
                                                d6delims = self.getDelimData(artist5)
                                                if self.getNdelims(d6delims) == 0:
                                                    self.addArtist(allArtists, artist5)
                                                    knownArtists = set(allArtists.keys())
                                                    continue
                                                elif self.isKnownArtist(artist5):
                                                    self.addArtist(allArtists, artist5)
                                                    knownArtists = set(allArtists.keys())
                                                    d6delims = {}

                                                    

        ##############################################################################
        ## Combine Results
        ##############################################################################
        return self.combineResults(allArtists, knownArtists, debug)
        
        
    def combineResults(self, allArtists, knownArtists, debug=False):
        results = {}
        if debug:
            print("Combining Results")
            print("All Artists:   {0}".format(allArtists))
            print("Known Artists: {0}".format(knownArtists))
        if self.discdata is not None and len(self.discArtists) > 0:
            for name in knownArtists:
                retval = self.discdata.get(name)
                if self.exact is False:
                    if retval is None:
                        retval = findNearest(name, self.discArtists, 1, self.cutoff)
                        if len(retval) == 1:
                            retval = self.discdata.get(retval[0])
                        else:
                            retval = None
                        
                results[name] = retval
        else:
            for artist in allArtists.keys():
                if self.masks.get(artist) is not None:
                    artist = self.masks[artist]
                results[artist] = ['?']
            #results = {k: ['?'] for k,v in allArtists.items()}            
        return results
    

    def getArtistNames(self, artist, debug=False):
        if debug:
            print("Getting Artist Names For {0}".format(artist))
        return self.newMethod(artist, debug)
    
        if self.nDelims(artist) == 0:
            names = {artist: []}
            return names
        
        if self.discdata is not None and len(self.discArtists) > 0:
            retval = self.discdata.get(artist)
            if retval is not None:
                return {artist: retval}
            else:
                retval = findNearest(artist, self.discArtists, 1, self.cutoff)
                if len(retval) == 1:
                    return {artist: self.discdata.get(retval[0])}        
        
        names = {artist: None}
        names = self.splitArtist(names)
        names = self.unravelDict(names)
        names = self.unravelDict(names)
        return names


    def unravelDict(self, dvals):
        fvals = {}
        for k,v in dvals.items():
            if isinstance(v, dict):
                for k2,v2 in v.items():
                    if isinstance(v2, dict):
                        for k3,v3 in v.items():
                            if isinstance(v3, dict):
                                for k4,v4 in v.items():
                                    fvals[k4] = v4
                            else:
                                fvals[k3] = v3
                    else:
                        fvals[k2] = v2
            else:
                fvals[k] = v

        return fvals


    def splitArtistDelim(self, artist, delval):
        names = {}    
        if delval not in artist:
            return None

        for val in artist.split(delval):
            val = val.strip()
            
            if self.discdata is not None and len(self.discArtists) > 0:
                retval = self.discdata.get(val)
                if retval is not None:
                    names[val] = retval
                else:
                    retval = findNearest(val, self.discArtists, 1, self.cutoff)
                    if len(retval) == 0:
                        names[val] = None
                    else:
                        names[val] = retval
            else:
                names[val] = [-1]

        if len(names) == 0:
            return None

        if any(names.values()) is False:
            return None

        return names


    def splitArtist(self, result):
        delims = self.delims
            
        #print("Input: {0}".format(result))
        for name in result.keys():
            #print("  Name -->",name,"\tCurrent Value -->",result[name])
            if result[name] is None:
                for delim in delims:
                    #print("\tDelim: {0}  for {1}".format(delim, name))
                    result2 = self.splitArtistDelim(name,delval=delim)
                    #print("\tDelim Result: {0}".format(result2))


                    if result2 is not None:
                        result[name] = result2
                        #print("\tName:",name,'\tResult:',result2)
                        for name2 in result2.keys():
                            if result2[name2] is None:
                                for delim2 in delims:
                                    #print("\t\tDelim2: {0}  for {1}".format(delim2, name2))
                                    result3 = self.splitArtistDelim(name2,delval=delim2)
                                    #print("\t\tDelim Result: {0}".format(result3))


                                    if result3 is not None:
                                        #print("\t\tName:",name2,'\tResult:',result3)
                                        result2[name2] = result3

                                        ## Breaking from delim2 
                                        break

                        ## Breaking from delim
                        break

        return result