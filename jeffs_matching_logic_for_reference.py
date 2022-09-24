#*************************************************************************************************************
# find_bolide_match_from_website
#
# Compares a bolide candidate with the list from the neo-bolides website and finds any matches.
#
# Inputs:
#   bolideDispositionProfileList -- [list] of BolideDispositionProfile objects
#   bolidesFromWebsite  -- [WebsiteBolideEvent list] created by:
#       bolide_dispositions.pull_dispositions_from_website
#   goesSatellite       -- [str] Which GLM to search for {'G16', 'G17'}
#   confidenceThreshold -- [float] Classifier confidence score to use as detection threshold
#   beliefSource        -- [str] Which source to use for belief confidence score {'human', 'machine'}
#                       if confidenceThreshold==0.0 then ignore beliefSource
#
# Outputs:
#   matchIndex -- [int np.array] Same size and len(bolideDispositionProfileList).
#       Gives the bolide index in bolidesFromWebsite which matches this detection.
#       [-1 means no match but same satellite,
#        -2 means below confidenceThreshold
#        -3 means no match and not even same satellite]
#   
#*************************************************************************************************************
    def find_bolide_match_from_website(bolideDispositionProfileList, bolidesFromWebsite, goesSatellite,
        confidenceThreshold=0.0, beliefSource=None):

    assert confidenceThreshold >= 0.0 and confidenceThreshold <= 1.0, 'confidenceThreshold must be between 0 and 1, inclusive'

    try:
        bd.validSatellites.index(goesSatellite)
    except:
        raise Exception('Unknown GOES Satellite')

    matchIndex = np.full([len(bolideDispositionProfileList)], int(-1))

    # How close does the beginning or end the clusters need to be to the truth bolides to be considered a hit
    distDeltaRange = 50.0 # kilometers (was: 50.0)

    #***
    # Get the data from the truth bolides
    # Extend ranges by expansion amount to account for bracketing errors
    timeRangeExt    = 0.0 / 60 / 60 / 24 # convert second => day (was: 0.0)
    latLonRangeExt  = 0.0 # degrees (was: 0.0)
    # There can be both G16 and G17 data per bolide in bolidesFromWebsite
    # In Unix Time
    bolideStartTimes    = []
    bolideEndTimes      = []
    bolideAvgLat        = []
    bolideAvgLon        = []
    nBolides = len(bolidesFromWebsite)
    for bolide in bolidesFromWebsite:
        idx = np.nonzero(np.in1d(bolide.satellite, goesSatellite))[0]
        if (len(idx) == 1):
            idx = idx[0]
            # Found a bolide for the GOES Satelite data in file_path
            bolideStartTimes.append(bolide.timeRange[idx][0].timestamp() - timeRangeExt)
            bolideEndTimes.append(bolide.timeRange[idx][1].timestamp()   + timeRangeExt)
            bolideAvgLat.append(np.mean(bolide.latRange[idx]))
            bolideAvgLon.append(np.mean(bolide.lonRange[idx]))
        else:
            bolideStartTimes.append(np.nan)
            bolideEndTimes.append(np.nan)
            bolideAvgLat.append(np.nan)
            bolideAvgLon.append(np.nan)

    bolideStartTimes    = np.array(bolideStartTimes)
    bolideEndTimes      = np.array(bolideEndTimes)
    bolideAvgLat        = np.array(bolideAvgLat)
    bolideAvgLon        = np.array(bolideAvgLon)

    # Pick which belief to return
    # But only if confidenceThreshold > 0.0
    if confidenceThreshold > 0.0:
        selection = bDisp.bolideBeliefSwitcher.get(beliefSource, bDisp.bolideBeliefSwitcher['unknown'])
        if (selection == bDisp.bolideBeliefSwitcher['unknown']):
            raise Exception("Unknown belief source")

    
    #***
    # For each bolide disposition, search for a match in bolidesFromWebsite
    for idx, disposition in enumerate(bolideDispositionProfileList):

        # Check if not even the correct satellite, set index to -2
        if (disposition.features.goesSatellite != goesSatellite):
            matchIndex[idx] = int(-3)
            continue
        
        # Check if confidence score is too low
        # But only if confidenceThreshold > 0.0
        if confidenceThreshold > 0.0:
            if selection == bDisp.bolideBeliefSwitcher['human']:
                # TODO: Get this working for multiple opinions
                if (disposition.humanOpinions is not None and disposition.humanOpinions[0].belief < confidenceThreshold):
                    matchIndex[idx] = int(-2)
                    continue
            elif selection == bDisp.bolideBeliefSwitcher['machine']:
                # TODO: Get this working for multiple opinions
                if (disposition.machineOpinions is not None and disposition.machineOpinions[0].bolideBelief < confidenceThreshold):
                    matchIndex[idx] = int(-2)
                    continue
        
        # Does this bolide candidate agree with any ground truth bolides?
        # First find any true bolides that line up in time with this one.
        # "Lining up" means 50% of the groups lie within the extended range of the true bolide
        # Ignore warning about Nans
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            potentialTimeMatchHere = np.logical_and(disposition.features.bolideMidRange[0].timestamp() > bolideStartTimes,
                    disposition.features.bolideMidRange[1].timestamp() < bolideEndTimes)
        
        if (len(np.nonzero(potentialTimeMatchHere)[0]) > 0):
            # Some line up in time. Now check lat/lon
            avgLat = disposition.features.avgLat
            avgLon = disposition.features.avgLon
            latLonDist = geoUtil.DistanceFromLatLonPoints(avgLat, avgLon,
                    np.transpose(bolideAvgLat), np.transpose(bolideAvgLon))

            # Check for any lat/lon matches in kilometers
            # Ignore warning about Nans
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                potentialDistMatchHere = np.abs(latLonDist) <= distDeltaRange

            thisMatchIndex = np.nonzero(np.logical_and(potentialTimeMatchHere, potentialDistMatchHere))[0]

            if (len(thisMatchIndex) == 1):
                # We found a match!
                matchIndex[idx] = int(thisMatchIndex)
            if (len(thisMatchIndex) > 1):
                # Found more than one match!
               #matchIndex[idx] = int(thisMatchIndex[0])
                raise Exception('Found more than one bolide match.')

    return matchIndex