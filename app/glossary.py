"""Plain-language tooltips for every technical term used in the app."""

GLOSSARY = {
    "COI": "Coefficient of inbreeding: the probability that a puppy inherits two copies of the "
    "same ancestral gene from both sides of its pedigree. Shown as a percentage.",
    "predicted COI": "The COI the puppies of this pair would have: equal to the kinship of sire "
    "and dam.",
    "kinship": "Probability that a gene picked at random from one dog is identical by descent "
    "to a gene picked at random from the other.",
    "mean kinship": "Average kinship of a dog (or a litter) with all living breeding-age dogs of "
    "the breed. Low mean kinship = carries genes that are rare in the breed today.",
    "gene diversity": "1 minus the mean kinship of the breed's breeding population: the share "
    "of genetic diversity still present relative to the founders of the recorded pedigree.",
    "Ne": "Effective population size: the size of an ideal population that would lose "
    "diversity as fast as this breed. Below 50 is critical, below 100 is a concern.",
    "Ne census": "Effective size from the number of sires and dams actually used: "
    "4 x sires x dams / (sires + dams). Usually far larger than Ne from inbreeding.",
    "fe": "Effective number of founders: how many equally contributing founders would give the "
    "same founder diversity.",
    "fg": "Founder genome equivalents: founder diversity left after unequal use and random loss "
    "of genes.",
    "EBV": "Estimated breeding value for hip dysplasia (HD) on an index scale: breed average "
    "100, higher is better. Computed from registry data only.",
    "accuracy": "Reliability of an EBV from 0 to 1: higher when the dog and its relatives have "
    "more HD results.",
    "EqG": "Equivalent complete generations: how deep the recorded pedigree is. Imports often "
    "have shallow pedigrees, so their recorded COI is underestimated.",
    "carrier": "A dog with one copy of a recessive disease variant: healthy itself, but can "
    "pass it on. Two carriers mated together give about 25% affected puppies.",
    "tier": "Overall recommendation from the weighted score: Excellent, Good, Acceptable, "
    "Caution, Not recommended. A soft-rule warning caps the tier at Acceptable.",
    "FCI 5% rule": "FCI guideline: no dog should have more offspring than 5% of the puppies "
    "registered in the breed in a 5-year period.",
    "realised IBD": "Ground truth only available in a simulation: the share of the genome a dog "
    "actually inherited identical from both parents.",
    "HD": "Hip dysplasia, graded A (free) to E (severe) under the FCI scheme.",
    "unverified": "This rule comes from a press report or a source we have not yet checked "
    "against the primary legal text. Treat it as indicative.",
    "weights": "Breeding priorities. They should be set by the breed club, not by software.",
}


def tip(key: str) -> str:
    """Tooltip text for a glossary term (KeyError if the term is missing)."""
    return GLOSSARY[key]
