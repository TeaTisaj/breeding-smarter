"""Coordinated sire use: optimum contributions, quotas and mate allocation (P12).

Notation (plan/13_P12_coordination.md section 2):
- candidates this year: sires S (size m), mated dams D (size n_d, fixed), one litter per dam;
- K = kinship matrix (A/2) among S and D from the recorded pedigree (or the true one, oracle);
- contributions c = (s, d), sum s = 1/2, d_j = 1/(2 n_d); sire i's expected litters
  l_i = 2 n_d s_i;
- expected coancestry of the planned matings C(c) = c'Kc;
- conservation OCS: min C(c); gain OCS: max m's subject to C(c) + tau(c) <= C_eff;
- bounds 0 <= l_i <= cap_i; youngest two age classes get >= 1 litter each; contribution-weighted
  mean EqG of sires >= the candidates' mean EqG.
"""
