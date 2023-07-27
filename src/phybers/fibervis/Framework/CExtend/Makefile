CC=gcc
CFLAGS=-Wall -Ofast -fopenmp
LN_FLAGS=-lm -fopenmp
LIB=bundleCFunctions

lib:
	$(CC) $(CFLAGS) -c -fPIC -o $(LIB).o $(LIB).c
	$(CC) $(LN_FLAGS) -shared -o $(LIB).so  $(LIB).o
