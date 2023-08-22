from . import atlas

for k, v in atlas.atlases.items():
    if atlas.check_atlas(v):
        setattr(atlas, k, v)
