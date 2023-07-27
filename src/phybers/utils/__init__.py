"""
Provides 4 utilities functions:
deform: Change .
intersection: Calculates intersection between 2 bundles.
dbindex: Provides statistics on the clusterings.
sample: Modifie fiber bundles from fibers of variable length to fibers of uniform length.
"""


from .utilities import deform, inter2bundles as intersection, postprocessing, sampling
