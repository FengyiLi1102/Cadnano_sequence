# Constants

# Complementary bases to the scaffolds on the left side of the origami
# Non-modified (raw) design of the pre-determined DNA origami
# Bases start from position 23 and end on position 8
# If the origami is modified (shift 2 helix down), index should be increased by 2.
HELIX_COMPLEMENTARY_BASE_LEFT_DICT = {
    0: "GCAACTGTTGGGAAGG",
    1: "CCGGGCGTGGCTAGCG",
    2: "AGACGCAGAAACAGCG",
    3: "TTTAAATTCAAACTAG",
    4: "TGCCAACGGCAGCACC",
    5: "CCTACCGTGGTGGCTG",
    6: "GCAGTGTCACTGCGCG",
    7: "GGTGTCTCACGTGTCC",
    8: "ATTGCGTTGCGCTCAC",
    9: "CTGACCTTTCGCCCGT",
    10: "AGGGTTGAGTGTTGTT",
    11: "AGAACAAGGTTTGACC",
    12: "GAAACAAACATCAAGA",
    13: "CATTAATTAAAACAAA",
    14: "ATGCAAATCCAATCGC",
    15: "AGCGCAAGAAACAGAA",
    16: "TTCGAGCCAGTAATAA",
    17: "CCATGAAATATAAGAG",
    18: "ACCGCGCCCAATAGCA",
    19: "GATATAGACTAAACGA",
    20: "TTTACAGAGAGAATAA",
    21: "GAAGGGACAAAAATAC",
    22: "TCCTTATTACGCAGTA",
    23: "AGATGCAAACGATTGT",
}

# On the right hand side of the scaffolds
HELIX_COMPLEMENTARY_BASE_RIGHT_DICT = {
    0: "TTCGCGTCTGGCCTTC",
    1: "AATAAAAACTACCGCA",
    2: "GATAAATTAATGCCGG",
    3: "TCGATCTTGCCAACTT",
    4: "GTAGCATTAACATCCA",
    5: "ATGATAATCATCTTAA",
    6: "TTAGAGAGTACCTTTA",
    7: "AGGACTGGACAACCTC",
    8: "GTTTTGCCAGAGGGGG",
    9: "AAGAAAACGTTTTCGG",
    10: "AACTTTAATCATTGTG",
    11: "CTTTAATTTGGTAGAG",
    12: "ATTGTGTCGAAATCCG",
    13: "AATAGTCCGCTACTAT",
    14: "AGGCTTGCAGGGAGTT",
    15: "GTCGCTGGCTTATATA",
    16: "GTCTTTCCAGACGTTA",
    17: "CTGTTTTGAAATCTAG",
    18: "GTTTTGCTCAGTACCA",
    19: "GGGCGATTAGGATTAG",
    20: "AGGCAGGTCAGACGAT",
    21: "GTTGGAGGACAGTTAC",
    22: "CGTCACCAATGAAACC",
    23: "AAAGGCCGGAACGATT"
}

"""
        Type 1: Start and end are both and right-hand-side and out of the scaffold
        --------------------------------
                    -------------------|----------[]
                    |                  |
                    -------------------|------>
        --------------------------------
        
        Type 2: Start and end are both at left-hand-side and out of the scaffold 
                    --------------------------------
        <-----------|-----------------
                    |                |
         []---------|-----------------
                    --------------------------------
        
        Type 3: RHS and End is out of the scaffold 
        --------------------------------
                    --------------[]   |
                    |                  |
                    -------------------|------>
        --------------------------------
        
        Type 4: LHS and '' ''
        
        Type 5: LHS and Start is out of the scaffold
                    --------------------------------
                    |   <-------------
                    |                |
            []------|-----------------
                    --------------------------------
                    
        Type 6: RHS and Start is out of the scaffold
"""

# # Types of staples
# RIGHT_TWO_ENDS_OUT = 1
# LEFT_TWO_ENDS_OUT = 2
# RIGHT_END_OUT = 3
# LEFT_END_OUT = 4
# LEFT_START_OUT = 5
# RIGHT_START_OUT = 6

# Staple base-assignment state
ASSIGNED = 1
UNASSIGNED = 0
NOT_EXIST = 2

COMPLEMENTARY_MAP = {
    "A": "T",
    "T": "A",
    "G": "C",
    "C": "G",
}
