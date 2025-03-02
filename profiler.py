import pstats, cProfile

import viceualize as viceualize
from viceualize import process_files, plot_data

cProfile.runctx("viceualize.process_files()", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()