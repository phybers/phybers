import os
import sys
import time
import numpy as np
from .mainFFClust import ffclust

if __name__ == "__main__":
    if 3 <= len(sys.argv) <= 5:
        ffclust(*sys.argv[1:])  # type: ignore
