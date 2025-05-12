
aaienstr = """
v(aai,aait,aaien,geaaid,aaide,aaiden,
    [h([intransitive,
    transitive,
    ld_pp,
    ld_adv,
    np_ld_pp,
    np_ld_adv])]).


"""

acclimatiseerstr = """
v(acclimatiseer,acclimatiseert,acclimatiseren,geacclimatiseerd,acclimatiseerde,acclimatiseerden,
  [unacc([intransitive
     ]),
   h([transitive  % de vogels moeten geacclimatiseerd worden
     ])]).
"""
zwerenstr = """
v(zweer,zweert,zweren,gezworen,[zweerde,zwoer,zwoor],[zweerden,zwoeren,zworen],
    [h([intransitive,
    np_sbar,
    np_vp_subj,
    sbar,
    so_pp_np,
    np_np,
    transitive,
    vp,
    part_transitive(af),
    pc_pp(bij),
    pc_pp(op)])]).

"""

acclimatiseerstr2 = """
v(acclimatiseer,acclimatiseert,acclimatiseren,geacclimatiseerd,acclimatiseerde,acclimatiseerden,
  [unacc([intransitive
     ]),
   h([transitive
     ])]).
"""

achtenstr = """
v(acht,acht,achten,geacht,achtte,achtten,
    [h([np_vp_obj1,             % verplicht passief?
    pred_np,
    pred_np_sbar,        % we achten het bewezen dat ..
    pred_np_vp,
    transitive])]).
"""

adresserenstr = """
v(adresseer,adresseert,adresseren,geadresseerd,adresseerde,adresseerden,
    [h([% refl,
    so_pp_np,
    transitive])]).

"""


applaudiserenstr = """
v([applaudisseer,applaudiseer],
  [applaudisseert,applaudiseert],
  [applaudisseren,applaudiseren],
  [geapplaudisseerd,geapplaudiseerd],
  [applaudisseerde,applaudiseerde],
  [applaudisseerden,applaudiseerden],
    [h([intransitive,
    mod_pp(voor)])]).

"""

bakkenstr = """
v(bak,bakt,bakken,gebakken,bakte,bakten,
    [h([transitive,
        part_intransitive(af),
        part_transitive(af),
    ap_pred_np,  % gaar, goudbruin
        fixed([mod_pp(in),acc],norm_passive),
        fixed([mod_pp(in),ap_pred,acc],norm_passive),
    np_np,       % iemand een poets bakken
    np_pc_pp(van)]),
     b([intransitive])]).

"""  # noqa: E101, W191

begaanstr = """
v(bega,begaat,inflected(begaan,begane),begaan,beging,begingen,
    [h([intransitive,
    transitive])]).
"""

beginnenstr = """
v(begin,begint,beginnen,begonnen,begon,begonnen,
    [z([intransitive,  % ik begin
    transitive,    % hij begon zijn verhaal
    vp,            % dat hij begon een boek te lezen
    aux(te_inf),   % dat hij een boek begon te lezen
                       % we mogen niet beginnen zweven  VLAAMS
        dip_sbar,      % dat is schitterend , begint hij
    np_pc_pp(met), % dat hij zijn verhaal begon met een inleiding
    pc_pp(aan),    % hij begon aan zijn verhaal
    pc_pp(met),    % hij begon met een inleiding
    pc_pp(over),   % hij begon weer over zijn broer
    mod_pp(tegen), % hij begint tegen winnaar Verkerk
    pc_pp(om),     % daar was het om begonnen
    fixed([pc(om),dat],no_passive),  % daar was het ons om begonnen
        acc_np_dip_sbar, % zo begon hij zijn verhaal
    er_pp_sbar(met)  % het begon er mee dat ...
       ])]).

"""

behalenstr = """
v(behaal,behaalt,behalen,behaald,behaalde,behaalden,
    [h([transitive,
    fixed([{[acc(succes),pc(met)]}],no_passive),
        fixed([{[acc(eer),pc(aan)]}],norm_passive)])]).
"""


beschadigenstr = """
v(beschadig,beschadigt,beschadigen,beschadigd,beschadigde,beschadigden,
  [unacc([intransitive]),       % ze beschadigen makkelijk
   h([transitive])]).

"""


bestaanstr = """
v(besta,bestaat,inflected(bestaan,bestane),bestaan,bestond,bestonden,
    [h([intransitive,
    part_intransitive(voort),
    sbar_subj,   % hoe bestaat het dat ..
    vp_obj,    % hij bestond het om ..
    fixed([subj(aandacht),pc(voor)],no_passive),
        fixed([pc(tot),subj(aanleiding)],no_passive),
        fixed([pc(voor),subj(aanleiding)],no_passive),
    fixed([subj(antwoord),pc(op)],no_passive),
    fixed([subj(behoefte),pc(aan)],no_passive),
    fixed([subj(belangstelling),pc(voor)],no_passive),
        fixed([subj(bereidheid),pc(tot)],no_passive),
    fixed([subj(bezwaar),pc(tegen)],no_passive),
    fixed([subj(bezwaar),er_pp(tegen,A),extra_sbar(A)],no_passive),
    fixed([subj(bezwaar),er_pp(tegen,A),extra_vp(A)],no_passive),
    fixed([subj(consensus),pc(over)],no_passive),
    fixed([subj(controle),pc(op)],no_passive),
    fixed([subj(discussie),pc(over)],no_passive),
    fixed([subj(duidelijkheid),pc(over)],no_passive),
    fixed([subj(draagvlak),pc(voor)],no_passive),
    fixed([subj(gebrek),pc(aan)],no_passive),
    fixed([subj(gevaar),pc(voor)],no_passive),
    fixed([subj(informatie),pc(over)],no_passive),
    fixed([subj(interesse),pc(voor)],no_passive),
    fixed([subj(kans),pc(op)],no_passive),
    fixed([subj(kritiek),pc(op)],no_passive),
    fixed([subj(literatuur),pc(over)],no_passive),
    fixed([subj(misverstand),pc(over)],no_passive),
    fixed([subj(misverstand),er_pp(over,X),extra_sbar(X)],no_passive),
    fixed([subj(noodzaak),pc(voor)],no_passive),
    fixed([subj(onduidelijkheid),pc(over)],no_passive),
    fixed([subj(overeenstemming),pc(over)],no_passive),
    fixed([subj(relatie),pc(tussen)],no_passive),
        fixed([subj(remedie),pc(tegen)],no_passive),
    fixed([subj(twijfel),pc(over)],no_passive),
    fixed([subj(twijfel),er_pp(over,X),extra_sbar(X)],no_passive),
    fixed([subj(twijfel),er_pp(over,X),extra_vp(X)],no_passive),
    fixed([subj(verschil),pc(tussen)],no_passive),
        fixed([subj(verklaring),pc(voor)],no_passive),
        fixed([subj(verplichting),pc(tot)],no_passive),
    fixed([subj(vraag),pc(naar)],no_passive),
    fixed([subj(weerstand),pc(tegen)],no_passive),
    fixed([subj(weerzin),pc(tegen)],no_passive),
        fixed([subj(wil),pc(tot)],no_passive),
    fixed([subj(woord),pc(voor)],no_passive),
    fixed([subj(zekerheid),pc(over)],no_passive),
    fixed([subj(zicht),pc(op)],no_passive),
    er_pp_vp(in),
    er_pp_sbar(in),
    pc_pp(uit),
    er_pp_sbar(uit),
    er_pp_vp(uit),
    pc_pp(van)])]).



"""


betaalstr = """
v(betaal,betaalt,betalen,betaald,betaalde,betaalden,
    [h([np_np,
    intransitive,
    transitive,
    amb_so_np_pass,    % ik word/krijg betaald
    so_pp_np,
    pc_pp(voor),       % ik betaal voor deze goederen
    np_pc_pp(voor),    % ik betaal veel geld voor deze goederen
    np_np_pc_pp(voor), % ik betaal hem veel geld voor deze goederen
    amb_so_np_pass_pc_pp(voor), % ik word/krijg betaald voor deze goederen
    np_pc_pp(over),    % ik betaal belasting/btw over deze goederen
    fixed([[leergeld]],imp_passive),
    fixed([{[[leergeld],pc(voor)]}],imp_passive),
    fixed([ap_pred,refl],no_passive), % we betalen ons blauw
    fixed([{[pc(aan),ap_pred]},refl],no_passive),
    part_np_np(door),
    part_np_np(terug),
    part_np_np(uit),
    part_intransitive(aan),
    part_intransitive(bij),
        part_intransitive(mee),
    part_intransitive(terug),
    part_intransitive(uit),
    part_amb_so_np_pass(terug), % ik word/krijg terugbetaald
    part_amb_so_np_pass(uit),   % ik word/krijg uitbetaald
    part_pc_pp(mee,aan),
        np_pc_pp(van),     % waar betaal je dat van?
    part_transitive(aan),
    part_transitive(af),
    part_transitive(bij),
    part_amb_so_np_pass(door), % word/krijg jij doorbetaald?
    part_transitive(door), % word het loon doorbetaald?
    part_transitive(mee),
    part_transitive(onder),
    part_transitive(terug),
    part_transitive(uit)])]).

"""

passerenstr = """
v(passeer,passeert,passeren,gepasseerd,passeerde,passeerden,
    [z([intransitive,
    pc_pp(voor)]),
     h([np_pc_pp(voor)]),
     b([transitive])]). % het koufront is Nederland gepasseerd

"""
