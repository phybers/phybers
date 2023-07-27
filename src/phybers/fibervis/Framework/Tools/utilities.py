import numpy as np

def bytes2MB(bytes):
	return bytes/1024

def bytes2GB(bytes):
	return bytes/(1024*1024)

def findIntegersMultiplierFor(n, under=1):
	for i in range(under):
		tmpN = n+i
		m1 = 1
		m2 = n

		while m1<=m2:
			if tmpN%m1 == 0 and m2<=under:
				return (np.int32(m2), np.int32(m1))
			m1 += 1
			m2 = tmpN//m1

	return None