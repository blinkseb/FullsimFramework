#! /usr/bin/env python

import os, datetime, pwd, re
from subprocess import Popen, PIPE
import subprocess
import xml.dom.minidom

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--create", action="store_true", dest="create", default=False, help="run crab")
parser.add_option("", "--run", action="store_true", dest="run", default=False, help="run crab")
(options, args) = parser.parse_args()

if options.run:
    options.create = True

datasets = [

        ["/S0_S_i_M400_cpl1_pseudoscalar_15Dec13_START53_V7C-GEN/sbrochet-S0_S_i_M400_cpl1_pseudoscalar_27Dec13_START53_V19-GEN-SIM-3ad0bd52b418b283a236bea5cfe8fe4a/USER", "S0_S_i_M400_cpl1_pseudoscalar"]

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

  ui_working_dir = ("crab_%s") % (dataset_name)
  publish_name = "%s_%s_START53_V19-AOD-SIM" % (dataset_name, d)
  output_file = "crab_%s.cfg" % (dataset_name)
  python_file = "%s_cff.py" % (dataset_name)

  print("Creating config file for '%s'" % (dataset_name))
  print("\tPublish name: %s" % publish_name)
  print("")

  # Execute cmsDriver.py
  args = ["cmsDriver.py", "step3", "--filein", "file:dummy.root", "--fileout", "file:output_GEN-SIM-RAW-RECO.root", "--mc", "--eventcontent", "AODSIM", "--datatier", "AODSIM", "--conditions", "START53_V19::All", "--beamspot", "Realistic8TeVCollision", "--step", "RAW2DIGI,L1Reco,RECO", "--no_exec", "--python_file", python_file, "-n", "5"]
  with open("/dev/null", "w") as f:
    subprocess.call(args, stdout=f)

  # Create crab template
  os.system("sed -e \"s#@datasetpath@#%(datasetpath)s#\" -e \"s#@pset@#%(pset)s#\" -e \"s#@events@#%(events)s#\" -e \"s#@working_dir@#%(working_dir)s#\" -e \"s#@output_dir@#%(output_dir)s#\" -e \"s#@publish_name@#%(publish_name)s#\" -e \"s#@event_per_job@#%(event_per_job)s#\" crab.template > %(output)s" % {"pset": python_file, "output": output_file, "working_dir": ui_working_dir, "events": -1, "output_dir": "NOT_USED", "publish_name": publish_name, "event_per_job": 4300, "datasetpath": dataset_files})

  if options.create:
    cmd = "crab -create -cfg %s" % (output_file)
    os.system(cmd)

    print "Modifying list of input files..."
    # Edit arguments.xml file to hardcode input files. Allow to run at CERN!
    argFile = os.path.join(ui_working_dir, 'share', 'arguments.xml')
    dom = xml.dom.minidom.parse(argFile)
    for elem in dom.getElementsByTagName("Job"):
      inputFiles = str(elem.getAttribute('InputFiles'))
      inputFileNames = inputFiles.split(',')
      inputFileNames = ["root://ccxrpli001.in2p3.fr:1094/" + inputFileName if not "root://" in inputFileName else inputFileName for inputFileName in inputFileNames]
      elem.setAttribute('InputFiles', ",".join(inputFileNames))
    with open(argFile, 'w') as f:
      f.write(dom.toxml())
    print "Done"

  if options.run:
    cmd = "crab -submit 1-500 -c %s" % (ui_working_dir)
    os.system(cmd)

    cmd = "crab -submit 500-1000 -c %s" % (ui_working_dir)
    os.system(cmd)

    cmd = "crab -submit 1000-1500 -c %s" % (ui_working_dir)
    os.system(cmd)

    cmd = "crab -submit 1500-2000 -c %s" % (ui_working_dir)
    os.system(cmd)
