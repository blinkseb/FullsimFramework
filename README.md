FullsimFramework
================

A set of script for full simulation inside CMS

## Setup

    cmsrel CMSSW_5_3_12_patch3
    cd CMSSW_5_3_12_patch3/src

    curl -s https://raw.github.com/cms-sw/genproductions/master/python/EightTeV/Hadronizer_TuneZ2star_8TeV_generic_LHE_pythia_tauola_cff.py --retry 2 --create-dirs -o  Configuration/GenProduction/python/EightTeV/Hadronizer_TuneZ2star_8TeV_generic_LHE_pythia_tauola_cff.py

    scram b -j4
