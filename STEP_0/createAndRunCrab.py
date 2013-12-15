#! /usr/bin/env python

import os, datetime, pwd, re
from subprocess import Popen, PIPE
import subprocess

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--run", action="store_true", dest="run", default=False, help="run crab")
(options, args) = parser.parse_args()

def findNumEventPerJob(events, start):
    # Iterate from start to 2*start, and find the optimal
    # number of events per job

    optimal = start
    rest = events
    for i in range(start, 2*start):
        mod = events % i
        if mod == 0:
            return i
        elif mod < rest:
            optimal = i
            rest = mod

    return optimal

datasets = [

    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M400_cpl1_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M400_cpl1_scalar", 2122092],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M500_cpl1_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M500_cpl1_scalar", 1990914],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M600_cpl1_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M600_cpl1_scalar", 2354636],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M700_cpl1_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M700_cpl1_scalar", 2000000],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M800_cpl1_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M800_cpl1_scalar", 2000000],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M900_cpl1_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M900_cpl1_scalar", 2000000],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M1000_cpl1_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M1000_cpl1_scalar", 2000000],

    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M400_cpl1_pseudoscalar_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M400_cpl1_pseudoscalar", 2279645],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M500_cpl1_pseudoscalar_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M500_cpl1_pseudoscalar", 2000000],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M600_cpl1_pseudoscalar_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M600_cpl1_pseudoscalar", 2000000],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M700_cpl1_pseudoscalar_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M700_cpl1_pseudoscalar", 2000000],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M800_cpl1_pseudoscalar_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M800_cpl1_pseudoscalar", 2000000],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M900_cpl1_pseudoscalar_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M900_cpl1_pseudoscalar", 2000000],
    [["/store/user/sbrochet/HTT/LHE_MADGRAPH_5/12Dec2013/2M_events/S_i_IDWTUP_minus3/gg_tt_M1000_cpl1_pseudoscalar_model_v4_S_i_unweighted_decayed_IDWTUP_minus3.lhe"], "S0_S_i_M1000_cpl1_pseudoscalar", 2000000],

    ]

# Get email address
email = "%s@ipnl.in2p3.fr" % (pwd.getpwuid(os.getuid()).pw_name)

d = datetime.datetime.now().strftime("%d%b%y")

version = 1

print("Creating configs for crab. Today is %s, you are %s and it's version %d" % (d, email, version))
print("")

for dataset_info in datasets:

  dataset_files = dataset_info[0];
  dataset_name = dataset_info[1];
  dataset_events = dataset_info[2]

  ui_working_dir = ("crab_%s") % (dataset_name)
  publish_name = "%s_%s_START53_V7C-GEN" % (dataset_name, d)
  output_file = "crab_%s.cfg" % (dataset_name)
  python_file = "%s_cff.py" % (dataset_name)

  print("Creating config file for '%s'" % (dataset_name))
  print("\tPublish name: %s" % publish_name)
  print("")

  # Format input files
  input_files_array = []
  if type(dataset_files) is list:
    input_files_array = dataset_files
  else:
    with open(dataset_files) as f:
      input_files_array = f.readlines()

  #input_files = ", ".join('"' + line.rstrip('\n') + '"' for line in input_files_array)
  input_files = " ".join(line.rstrip('\n') for line in input_files_array)

  numEventPerJob = findNumEventPerJob(dataset_events, 50000)
  # Execute cmsDriver.py
  args = ["cmsDriver.py", "Configuration/GenProduction/python/EightTeV/Hadronizer_TuneZ2star_8TeV_generic_LHE_pythia_tauola_cff.py", "--filein", input_files, "--fileout", "output_GEN.root", "--mc", "--eventcontent", "RAWSIM", "--datatier", "GEN", "--conditions", "START53_V7C::All", "--beamspot", "Realistic8TeVCollision", "--step", "GEN", "--no_exec", "--python_file", python_file, "-n", str(dataset_events)]
  subprocess.call(args)

  # Replace the PDF used by Pythia
  os.system('sed -i -e "s/MSTP(51)=10042/MSTP(51)=10800/" %s' % python_file)

  # Create crab template
  os.system("sed -e \"s#@pset@#%(pset)s#\" -e \"s#@events@#%(events)s#\" -e \"s#@working_dir@#%(working_dir)s#\" -e \"s#@output_dir@#%(output_dir)s#\" -e \"s#@publish_name@#%(publish_name)s#\" -e \"s#@event_per_job@#%(event_per_job)s#\" crab.template > %(output)s" % {"pset": python_file, "output": output_file, "working_dir": ui_working_dir, "events": dataset_events, "output_dir": "NOT_USED", "publish_name": publish_name, "event_per_job": numEventPerJob})

  cmd = "crab -create -submit -cfg %s" % (output_file)
  if options.run:
    os.system(cmd)
