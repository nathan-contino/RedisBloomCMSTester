# Using Count-Min Sketch
from redisbloom.client import Client
# pass in arguments
import sys
# random IP address generation helpers
import random
import socket
import struct
# actual counts helper
from collections import defaultdict
from collections import Counter

# help dialog
if sys.argv[1] == '--help':
	print('Arguments: \n\t-numVisitors: number of visitors\n\t-numVisits: number of visits\n\n-compare: whether or not to compare the exact visit counts to the generated sketch\n\t-cmsName: the name of the count-min sketch that the script should use\n\t-numToCompare: the number of elements to compare actual and CMS counts for')
	sys.exit(1)

# checker to make sure input is valid
if len(sys.argv) != 11 or sys.argv[1] != "-numVisitors" or sys.argv[3] != "-numVisits" or sys.argv[5] != "-compare" or sys.argv[7] != "-cmsName" or sys.argv[9] != "-numToCompare":
	print('Must pass in a *number of visitors*, a *number of visits*, whether or not to compare a non-probabilistic hash table to the generated count-min sketch, and the name of the count-min sketch that the script should use, and the number of items to compare')
	sys.exit(2)

# pull values out of command line args
numVisitors = int(sys.argv[2])
numVisits = int(sys.argv[4])
compare = bool(sys.argv[6])
cmsName = sys.argv[8]
numToCompare = int(sys.argv[10])
print('Running with numVisitors=', numVisitors, 'numVisits=', numVisits, 'compare=', compare, 'cmsName=', cmsName, 'numToCompare=', numToCompare)

# generate a pool of visitors
visitors = []
for i in range(0, numVisitors):
	visitors.append(str(socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))))

# for number of visits, add to the count-min sketch a randomly selected visitor
actual_counts = defaultdict(int)
for visitor in visitors:
	actual_counts[visitor] = 0
redis_instance = Client()
# this script assumes the cms already exists (fewer params to deal with), but this is what you'd use to init
#redis_instance.cmsInitByDim(cmsName, 1000, 10)
for i in range(0, numVisits):
	# pick a visitor ip
	visitor = random.choice(visitors)
	# add to the cms
	redis_instance.cmsIncrBy(cmsName, [visitor], [1])
	# add to the actual counts map
	actual_counts[visitor] += 1

if compare:
	# compare the top 10 visitors (actual) to their counts in the sketch, and the bottom 10 to their counts in the sketch
	counts_counter = Counter(actual_counts)
	sorted = counts_counter.most_common()
	elephants = sorted[:numToCompare]
	mice = sorted[-1*numToCompare:]

	# helper method to pad shorter IP addresses with an extra tab
	def get_tabs(ip):
		if (len(ip) >= 13):
			return "\t"
		else:
			return "\t\t"

	print('\nTop', numToCompare, '- elephants:')
	for elephant in elephants:
		print('Visitor: ', elephant[0], get_tabs(elephant[0]), 'Count-Min Sketch value: ', redis_instance.cmsQuery(cmsName, elephant[0])[0], '\tActual value: ', elephant[1])

	print('\nBottom', numToCompare, '- mice:')
	for mouse in mice:
		cms_value = redis_instance.cmsQuery(cmsName, mouse[0])
		# if no visits by this visitor, just report 0 instead of accessing into invalid return
		if cms_value != None:
			print('Visitor: ', mouse[0], get_tabs(mouse[0]), 'Count-Min Sketch value: ', cms_value[0], '\tActual value: ', mouse[1])
		else:
			print('Visitor: ', mouse[0], get_tabs(mouse[0]), 'Count-Min Sketch value: ', 0, '\tActual value: ', mouse[1])
