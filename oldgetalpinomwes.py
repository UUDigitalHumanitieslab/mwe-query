def getalpinomwes(syntree: SynTree, sentenceid=None) -> List[MWEMeta]:  # noqa: C901
    mwemetas = []
    mwelexicon = "Alpino"
    sentence = getsentence(syntree)
    mwequerytype = "MEQ"
    iavnode = None
    zichnode = None
    partnode = None
    verbs = syntree.xpath('.//node[@pt="ww" ]')
    for verb in verbs:
        iavnode = None
        zichnode = None
        partnode = None
        classes = []
        mwenodes = []
        svpnodes = []
        wwsvpnode = None
        siblings = verb.xpath("../node")
        for sibling in siblings:
            if sibling == verb:
                continue
            siblingrel = gav(sibling, "rel")
            if siblingrel == "pc":
                classes += ["IAV"]
                if terminal(sibling):
                    mwenodes.append(sibling)
                    iavnode = sibling
                else:
                    siblinghead = getheadof(sibling)
                    mwenodes.append(siblinghead)
                    iavnode = siblinghead
            if siblingrel == "se":
                if terminal(sibling):
                    zichnode = sibling
                else:
                    zichnode = getheadof(sibling)
                mwenodes.append(zichnode)
                classes.append("IRV")
            if siblingrel == "svp":
                if isparticleverb(verb):
                    if terminal(sibling):
                        siblingpt = gav(sibling, "pt")
                        if siblingpt == "ww":
                            classes += ["MVC"]
                            wwsvpnode = sibling
                            mwenodes.append(sibling)
                        else:
                            wwprt = getprtfromlemma(verb)
                            siblinglemma = gav(sibling, "lemma")
                            if wwprt == siblinglemma:
                                classes += ["VPC.full"]
                                # partnode = sibling
                                mwenodes.append(sibling)
                            else:
                                pass  # we ignore other svp nodes and rely for this on DUCAME
                    else:
                        if len(sibling) == 1:
                            siblinghead = sibling[0]
                            siblingpt = gav(siblinghead, "pt")
                            siblinglemma = gav(siblinghead, "lemma")
                            wwprt = getprtfromlemma(verb)
                            if siblingpt == "ww":
                                classes += ["MVC"]
                            elif wwprt == siblinglemma:
                                classes += ["VPC.full"]
                                # partnode = sibling
                                mwenodes.append(sibling)
                            else:
                                classes += ["VID"]
                        else:
                            siblingcat = gav(sibling, "cat")
                            siblingleaves = getnodeyield(sibling)
                            svpnodes = getsvpnodes(siblingleaves)
                            if siblingcat in ["ti", "inf"]:
                                classes.append("MVC")
                                mwenodes += siblingleaves
                            else:
                                pass  # we ignore these and rely on DUCAME
                else:
                    if terminal(sibling):
                        siblingpt = gav(sibling, "pt")
                        mwenodes.append(sibling)
                        if siblingpt == "ww":
                            if isparticleverb(sibling):
                                classes = ["VID", "VPC.full"]
                            else:
                                classes += ["MVC"]
                            wwsvpnode = sibling
                    else:
                        (mwuppok, mwupphd, mwuppleaves) = ismwupp(sibling)
                        if mwuppok:
                            mwenodes += mwuppleaves
                            svpnodes = mwuppleaves
                            classes += ["VID"]
                        else:
                            siblingcat = gav(sibling, "cat")
                            siblingleaves = getnodeyield(sibling)
                            svpnodes = getsvpnodes(siblingleaves)
                            wwsvpnodecands = [
                                svpnode
                                for svpnode in svpnodes
                                if gav(svpnode, "pt") == "ww"
                            ]
                            if wwsvpnodecands != []:
                                wwsvpnode = wwsvpnodecands[0]
                                svpnodes = [
                                    svpnode
                                    for svpnode in svpnodes
                                    if svpnode != wwsvpnode
                                ]
                            else:
                                wwsvpnode = None
                            mwenodes += siblingleaves
                            if siblingcat in ["ti", "inf"]:
                                classes.append("MVC")
                            else:
                                classes += ["VID"]
        if "VPC.full" not in classes and isparticleverb(verb):
            classes.append("VPC.full")
        if classes != []:
            mwenodes.append(verb)
            intpositions = getintpositions(mwenodes)
            headposition = int(gav(verb, "end"))
            headpos = "ww"
            headlemma = gav(verb, 'lemma')
            parsemetype = getmwetype(verb, headpos, classes)
            if sentenceid is None:
                sentenceid = ""
            mweid = getmweid(zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode)
            mwemeta = MWEMeta(
                sentence,
                sentenceid,
                mweid,
                mwelexicon,
                mwequerytype,
                mweid,
                intpositions,
                headposition,
                headpos,
                headlemma,
                classes,
                parsemetype,
            )
            mwemetas.append(mwemeta)
    vzs = syntree.xpath(
        './/node[@pt="vz" and @rel="hd" ]'
    )  # no condition on vztype because of 'ergens op af'
    for vz in vzs:
        vzposition = int(gav(vz, "end"))
        vzazsiblings = vz.xpath('../node[@pt="vz" and @vztype="fin" and @rel="hdf"]')
        for az in vzazsiblings:
            vzlemma = gav(vz, "lemma")
            azlemma = gav(az, "lemma")
            mweid = f"{vzlemma}...{azlemma}"
            azposition = int(gav(az, "end"))
            intpositions = sorted([vzposition, azposition])
            headposition = vzposition
            headpos = gav(vz, "pt")
            headlemma = gav(vz, 'lemma')
            classes = ["PID"]
            parsemetype = getmwetype(vz, headpos, classes)
            mwemeta = MWEMeta(
                sentence,
                sentenceid,
                mweid,
                mwelexicon,
                mwequerytype,
                mweid,
                intpositions,
                headposition,
                headpos,
                headlemma,
                classes,
                parsemetype,
            )
            mwemetas.append(mwemeta)
    return mwemetas
