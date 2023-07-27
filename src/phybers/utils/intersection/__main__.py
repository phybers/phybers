import shlex
import sys
import time
from ..utilities import inter2bundles

#%% 7. Intersección para ello se usa la función que se muestra a continuación (inter2bundles) realizada en python y esta ejecuta un programa de c que calcula
# que se llama "fiberDistanceMax2bun.c"

# Directorios de los dos set de fibras a comprarar

dir_fib1 = sys.argv[1]
dir_fib2 = sys.argv[2]
outdir= sys.argv[3] # este dir es para guardar cálculos como la matriz

d_th = float(sys.argv[4]) # umbral de intersección en milimetros y lo define el usuario. default: 15

pinter = inter2bundles (dir_fib1, dir_fib2, outdir, d_th)
print ("Intersection in the set of fibers1 [%]: ", pinter[0])
print ("Intersection in the set of fibers2 [%]:: ", pinter[1])

t0=time.time()

print ("Demora: ", time.time()-t0 ," [s]" )
