import os
import subprocess as sp
from pathlib import Path

pathname = os.path.dirname(__file__)
parent_path = str(Path(pathname).parents[0])

print("How to run:")

print("python3 -m hclust <dir_raw_tractography> <MaxDistance_Threshold> <maxdist> <var> <result_path>")

print("For example, try running:")

print("python3 -m hclust " + os.path.join(parent_path, 'data','subsampling_hier.bundles ') +  "40  " + "30 " + os.path.join(parent_path, "result"))

sp.run(["xdg-open", parent_path + "/html/index.html"])
