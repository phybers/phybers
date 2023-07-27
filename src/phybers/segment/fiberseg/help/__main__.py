import os
import subprocess as sp
from pathlib import Path

pathname = os.path.dirname(__file__)
parent_path = str(Path(pathname).parents[0])

print("How to run:")

print("python3 -m segmentation <number of points> <fibers .bundles path> <subj. id> <atlas dir path> <atlas info .txt> <result path>")

print("For example, try running:")

print("python3 -m segmentation 21 " + parent_path + "/data/subjects/118225/118225.bundles 118225 " + parent_path + "/data/atlas_flargas/bundles " + parent_path + "/data/atlas_flargas/atlas_info.txt " + parent_path + "/result")

sp.run(["xdg-open", parent_path + "/html/index.html"])
