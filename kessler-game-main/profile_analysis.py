import pstats

p = pstats.Stats("kessler_profile.prof")
p.strip_dirs().sort_stats("cumulative").print_stats(20)