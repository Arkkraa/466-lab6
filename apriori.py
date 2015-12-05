import sys

def printRules(rules, goodsDb):
	"""Rules is the list containing (leftrule, rightrule, support, confidence)"""

	rules.sort(key=lambda element: len(element[0]))
	for i in range(len(rules)):
		leftside, rightside, sup, conf = rules[i]

		left = ''
		for e in leftside:
			left += goodsDb[e] + ', '
		left = left[:-2]

		right = ''
		for e in rightside:
			right += goodsDb[e]

		print 'Rule %d:     %s  -->  %s   [sup=%f conf=%f]' % (
				i + 1, left, right, sup, conf)



def confidence(f, leftside, support):
	"""Return the confidence of the rule"""
	return support[f] * 100 / support[leftside]


def genRules(F, support, minConf):
	"""return a list containing (leftrule, rightrule, support, confidence)"""

	result = []
	for f in F:
		if len(f) < 2:
			continue

		for s in f:
			right = set([s])
			left = f.difference(right)

			conf = confidence(f, left, support)
			if conf >= minConf:
				result.append((left, right, support[f], conf))
	
	return result

def skylineItemsets(F):
	"""find skyline itemsets"""

	tmpSet = F.copy()
	for element in tmpSet:
		for f in F:
			if element != f and element.issubset(f):
				F.remove(element)
				break

def apriori(filename, minSup):
	F = []
	recordCount, support = initialPass(filename)
	initialSet = set([k for k, v in support.iteritems() if v >= minSup])
	F.append(initialSet)
	k = 1

	while (len(F[k -1]) != 0):
		C = candidateGen(F[k - 1])
		counts = {}

		for line in open(filename):
			t = getTransaction(line)	
			for c in C:
				if c.issubset(t):
					counts[c] = counts.get(c,0) + 1

		Fk = set()
		for key, value in counts.items():
			sup = value * 100 / float(recordCount)
			if sup >= minSup:
				Fk.add(key)
				support[key] = sup

		F.append(Fk)
		k += 1
	
	result = set()
	for f in F:
		result = result.union(f)

	return result, support


def getTransaction(line):
	"""Get the next transaction in the line"""

	lst = line.split(',')
	transaction = set()

	for i in range(1, len(lst)):
		element = lst[i].strip()
		transaction.add(element)
	return transaction

	
def candidateGen(F):
	"""Generate candidate sets"""

	C = set()
	elements = [] # list of sets
	for e in F:
		elements.append(e)

	for i in range(len(elements)):
		for j in range(i + 1, len(elements)):
			s = elements[i].union(elements[j])
			if len(s) == len(elements[i]) + 1:
				flag = True
				for e in s:
					tmp = s.copy()
					diff = tmp.difference(set([e]))
					if diff not in F:
						flag = False
				if flag == True:
					C.add(s)
	return C


def initialPass(filename):
	"""Get the support of all items present in the transactions"""
	
	support = {}
	recordCount = 0

	for line in open(filename):
		t = line.split(',')
		itemCount = len(t)

		# make sure to skip id
		for i in range(1, itemCount):
			item = t[i].strip()
			element = frozenset([item])
			support[element] = support.get(element, 0) + 1

		recordCount += 1

	# update support
	for key in support:
		support[key] = support[key] * 100 / float(recordCount)
	
	return recordCount, support


def initialSet(support, minSup):
	"""Generate inital set"""

	s = set()
	for item in support:
		if support[item] >= minSup:
			s.add(frozenset([item]))
	return s

def getDatabase(filename):
	"""Get the goods database"""
	goods = {}

	for line in open(filename):
		record = line.split(',')
		id = record[0].strip()
		flavor = record[1].strip()
		food = record[2].strip()
		
		goods[id] = '%s %s' % (flavor, food)
	
	return goods



if __name__ == '__main__':

	if len(sys.argv) != 4:
		print 'Usage: python apriori.py <csvfile> <minSup> <minConf>'
		sys.exit(1)

	filename = sys.argv[1] 
	minSup = float(sys.argv[2]) 
	minConf = float(sys.argv[3])

	F, support = apriori(filename, minSup)
	skylineItemsets(F)
	rules = genRules(F, support, minConf)
	goodsDb = getDatabase('goods.csv')
	printRules(rules, goodsDb)

