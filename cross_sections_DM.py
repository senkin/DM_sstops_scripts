
cross_sections_total = {
					# mediator mass : tt_excl + off-shell V + on-shell V, xsections in pb
					'1000' : 1.3042   + 0.084606  + 0.114,
					'1500' : 0.38954  + 0.022072  + 0.01902,
					'2000' : 0.15696  + 0.0080612 + 0.0044234,
					'2500' : 0.075108 + 0.0035796 + 0.0012704,
					'3000' : 0.040244 + 0.001815  + 0.0004306,
					}

cross_sections_tt_excl = {
					# mediator mass : tt_excl xsections in pb
					'1000' : 1.3042,
					'1500' : 0.38954,
					'2000' : 0.15696,
					'2500' : 0.075108,
					'3000' : 0.040244,
					}

cross_sections_offshellV = {
					# mediator mass : off-shell V xsections in pb
					'1000' : 0.084606,
					'1500' : 0.022072,
					'2000' : 0.0080612,
					'2500' : 0.0035796,
					'3000' : 0.001815,
					}

cross_sections_onshellV = {
					# mediator mass : on-shell V xsections in pb
					'1000' : 0.114,
					'1500' : 0.01902,
					'2000' : 0.0044234,
					'2500' : 0.0012704,
					'3000' : 0.0004306,
					}

# approximate 3-sigma exclusion cross-sections for 2 TeV mass point
exclusion_cross_sections = {
					'SSee' : 0.06,
					'SSem' : 0.02,
					'SSmm' : 0.02,
					'combined_2l' : 0.06,
					}

# 308073	1.3042		1.0	pythia8
# 308074	0.38954		1.0	pythia8
# 308075	0.15696		1.0	pythia8
# 308076	0.075108		1.0	pythia8
# 308077	0.040244		1.0	pythia8
# 308078	0.084606		1.0	pythia8
# 308079	0.022072		1.0	pythia8
# 308080	0.0080612	1.0	pythia8
# 308081	0.0035796	1.0	pythia8
# 308082	0.001815		1.0	pythia8
# 308083	0.114		1.0	pythia8
# 308084	0.01902		1.0	pythia8
# 308085	0.0044234	1.0	pythia8
# 308086	0.0012704	1.0	pythia8
# 308087	0.0004306	1.0	pythia8

cross_sections_mMed1000_mX1 = {
					# automatic width of V decay (10% M_V)
					# "tt_exclusive": 13.62, 
					# "ttu_inclusive": 15.8, 
					# "ttu_offshellV": 0.8839, 
					# "ttu_onshellV": 1.207,
					"tt_exclusive": 14.22, 
					"ttu_inclusive": 17.01, 
					"ttu_offshellV": 0.9267, 
					"ttu_onshellV": 1.718
					}

cross_sections_dilep_mMed1000_mX1 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 1.391, 
					"ttu_inclusive": 1.61, 
					"ttu_offshellV": 0.08918, 
					"ttu_onshellV": 0.1211
					}

cross_sections_dilep_mMed1500_mX1 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 0.4148, 
					"ttu_inclusive": 0.4603, 
					"ttu_offshellV": 0.02336, 
					"ttu_onshellV": 0.02021

					}

cross_sections_mMed1000_mX10 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 13.62, 
					"ttu_inclusive": 15.8, 
					"ttu_offshellV": 0.8839, 
					"ttu_onshellV": 1.207
					}

cross_sections_mMed1000_mX10_mWidth5 = {
					# Smaller width of V decay (0.5% M_V)
					"tt_exclusive": 13.71, 
					"ttu_inclusive": 40.36, 
					"ttu_offshellV": 0.8893, 
					"ttu_onshellV": 25.63,
					}

cross_sections_mMed1000_mX10_mWidth50 = {
					# Medium width of V decay (5% M_V)
					"tt_exclusive": 14.25, 
					"ttu_inclusive": 17.95, 
					"ttu_offshellV": 0.9296, 
					"ttu_onshellV": 2.628
					}


cross_sections_mMed2000_mX1 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 1.703, 
					"ttu_inclusive": 1.863, 
					"ttu_offshellV": 0.08771, 
					"ttu_onshellV": 0.06284
					}

cross_sections_dilep_mMed2000_mX1 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 0.1667, 
					"ttu_inclusive": 0.1802, 
					"ttu_offshellV": 0.008515, 
					"ttu_onshellV": 0.004683
					}

cross_sections_dilep_mMed2500_mX1 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 0.0795, 
					"ttu_inclusive": 0.08513, 
					"ttu_offshellV": 0.003791, 
					"ttu_onshellV": 0.001348
					}

cross_sections_mMed2000_mX10 = {
					# automatic width of V decay (10% M_V)
					'ttu_inclusive': 1.765,
					'tt_exclusive': 1.627,
					'ttu_onshellV': 0.04636,
					'ttu_offshellV': 0.08433,
					}

cross_sections_mMed2000_mX10_mWidth10 = {
					# Smaller width of V decay (0.5% M_V)
					"tt_exclusive": 1.639, 
					"ttu_inclusive": 2.589, 
					"ttu_offshellV": 0.08505, 
					"ttu_onshellV": 0.8507,
					}

cross_sections_mMed2000_mX10_mWidth100 = {
					# Medium width of V decay (5% M_V)
					"tt_exclusive": 1.707, 
					"ttu_inclusive": 1.901, 
					"ttu_offshellV": 0.08806, 
					"ttu_onshellV": 0.09556,
					}

cross_sections_mMed3000_mX1 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 0.4357, 
					"ttu_inclusive": 0.4638, 
					"ttu_offshellV": 0.0199, 
					"ttu_onshellV": 0.005702
					}

cross_sections_dilep_mMed3000_mX1 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 0.04265, 
					"ttu_inclusive": 0.04528, 
					"ttu_offshellV": 0.001925, 
					"ttu_onshellV": 0.0004573
					}

cross_sections_mMed3000_mX10 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 0.4162, 
					"ttu_inclusive": 0.4414, 
					"ttu_offshellV": 0.01905, 
					"ttu_onshellV": 0.004542
					}

cross_sections_mMed3000_mX10_mWidth15 = {
					# Smaller width of V decay (0.5% M_V)
					"tt_exclusive": 0.4198, 
					"ttu_inclusive": 0.4989, 
					"ttu_offshellV": 0.01923, 
					"ttu_onshellV": 0.05794
					}

cross_sections_mMed3000_mX10_mWidth150 = {
					# Medium width of V decay (5% M_V)
					"tt_exclusive": 0.437, 
					"ttu_inclusive": 0.4673, 
					"ttu_offshellV": 0.02, 
					"ttu_onshellV": 0.007878,
					}

cross_sections_mMed3000_mX100 = {
					# automatic width of V decay (10% M_V)
					"tt_exclusive": 0.4162, 
					"ttu_inclusive": 0.4414, 
					"ttu_offshellV": 0.01905, 
					"ttu_onshellV": 0.004542
					}

