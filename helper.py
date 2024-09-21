

import re
from molmass import Formula

# Use re.sub() to replace "[number]X" where X is 1 or 2 letters with "[numberX]" formatting molmass style
def format_heavy_isotope(mf):
    return re.sub(r'\[(\d+)\]([A-Z][a-z]?)', r'[\1\2]', mf)

# Calculate monoisotopic mass based on elemental formula, work for heavy isotope-labeled compounds
def monoisotopic_mass(mf):
    mf = format_heavy_isotope(str(mf))
    try:
        mol = Formula(mf)
        mass = mol.monoisotopic_mass
        return round(mass, 4)
    except:
        print("Molecular formula not valid ! ")
        return 0

# Calculate ion formula based on adduct
def ion_formula(nf, adduct):

    nf = format_heavy_isotope(str(nf))
    mol = Formula(nf)

    try:
        match adduct:
            case "M+H":
                mol = mol + Formula("H")
            case "M-H":
                mol = mol - Formula("H")
            case "M+Na":
                mol = mol + Formula("Na")
            case "M+NH4":
                mol = mol + Formula("NH4")
            case "M+FA-H":
                mol = mol + Formula("C1H1O2")
        mf = mol.formula
        return mf

    except ValueError:
        print("Ion formula calculation not possible ! ")
        return 'nan'

#mf = "C6[13]C1H6N1[15]N2O4S2Cl1"
#mf = "C12H21O3F9Si3"

#print(monoisotopic_mass(mf))
#print(ion_formula(mf, "M+FA-H"))