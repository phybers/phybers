import time

def timeit(func):

	def timed(*args, **kw):
		ts = time.time()
		result = func(*args, **kw)
		te = time.time()

		print ('%r (%r, %r) %2.4f sec' % (func.__name__, args, kw, te-ts))
		return result

	return timed

def averageTimeit(func):
	n=50

	def timed(*args, **kw):
		time_average = 0
		for i in range(n):
			print('test n: ', i)
			ts = time.time()
			result = func(*args, **kw)
			te = time.time()

			time_average += te-ts

		time_average /= n

		
		print ('%r (%r, %r) %d %2.4f sec' % (func.__name__, args, kw, n, time_average))
		return result

	return timed