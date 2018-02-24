'''
process Sinica Treebank

Hai Hu, Chien-Jer Charles Lin, Feb, 2018
'''

import re, sys

helpM='''

Usage: python3 processST.py treeFile.txt (-h)

* treeFile.txt: Sinica trees, one tree per line
OR:
* -h for help.
* -t for test.

'''

def main():
    if len(sys.argv) < 2 or '-h' in sys.argv:
        print(helpM)
    elif '-t' in sys.argv:
        test()
    else:
        readTreeFile(sys.argv[1])

def readTreeFile(fn):
    trees = open(fn, 'r', encoding='utf8').readlines()
    trees = [x.strip() for x in trees]
    pat_sem_tag = re.compile(r'([\(\|])([^:]+):') # sem tag always between '(' or '|' and ':'

    pcfg = PCFG()
    for treeStr in trees:
        treeStr_noSem = pat_sem_tag.sub(r'\1',treeStr)
        mytree = Tree()

        # --- parse the tree to my data structure --- #
        pcfg.getPCFGoneTree(treeStr_noSem, mytree)
        # --- --- #

        # IF DON'T WANT TO SEE THE TREE, COMMENT OUT THE FOLLOWING LINE
        mytree.printTree()
        print('\nmaxdepth of whole tree: {}'.format(mytree.maxDepth))
        mytree.getRC(verbose=False)
        print('number of RC in above tree: {}'.format(mytree.numRC))

    print('\n\nreading trees done!')
    print('CFG rules:')
    for k in pcfg.grm_lhss.keys():
        print('{} --> \n\t{}'.format(k, pcfg.grm_lhss[k]))

def test():
    treeStr = 'VP(Head:VC2:看|aspect:Di:著|goal:NP(predication:VP‧的(head:VP(location:NP(property:Nab:窗|Head:Ncda:外)|standard:PP(Head:P58:隨|DUMMY:NP(Head:Naa:風))|Head:VA11:飄動)|Head:DE:的)|Head:Nab:樹枝))'

    pat_sem_tag = re.compile(r'([\(\|])([^:]+):') # sem tag always between '(' or '|' and ':'

    treeStr_noSem = pat_sem_tag.sub(r'\1',treeStr)

    pcfg = PCFG()
    mytree = Tree()

    # --- parse the tree to my data structure --- #
    pcfg.getPCFGoneTree(treeStr_noSem, mytree)
    # --- --- #

    # IF DON'T WANT TO SEE THE TREE, COMMENT OUT THE FOLLOWING LINE
    mytree.printTree()
    print('\nmaxdepth of whole tree: {}'.format(mytree.maxDepth))
    mytree.getRC(verbose=False)
    print('number of RC in above tree: {}'.format(mytree.numRC))

class Node:
    '''
    A node has
    1) tag, e.g. NP
    2) word, e.g. Apple
    3) children = a list of nodes
    '''
    def __init__(self, tag, word=None):
        self.tag = tag
        self.word = word
        self.children = []
        self.depth = 0

    def __str__(self):
        if self.word:
            return '{} {}'.format(self.word,self.depth)
        else:
            return '{} {}'.format(self.tag,self.depth)

    def __repr__(self):
        if self.word:
            return '{} {}'.format(self.word,self.depth)
        else:
            return '{} {}'.format(self.tag,self.depth)

class Tree:
    '''
    A tree has
    1) n = number of nodes
    2) m = number of layers
    3) root = root node
    '''
    def __init__(self, root=None):
        self.root = root
        self.n = 0
        self.m = 0
        self.leafNodes = []
        self.nonTermNodes = []
        self.maxDepth = 0
        self.RCdepths = []
        self.numRC = 0
        # contains all info of all RCs {1:{'RCdepth':3, 'numLeafNodes':4, 'numNTnodes':6}, ...}
        self.RCs = {}
    def getRC(self, verbose=False):
        ''' find depth of all RCs, and fill numRC '''
        RCcounter = 0
        for n in self.nonTermNodes:
            # if n.tag in ['V‧的']:
            if n.tag in ['ADV‧的','A‧的','DM‧的','GP‧的','NP‧的',
                'N‧的','PP‧的','S‧的','VP‧的','V‧的']:
                RCcounter+=1
                print('\nprocessing RC *{}*'.format(RCcounter))
                if verbose:
                    self.printTreeHelper(n)
                self.numRC+=1

                # -1 for numLeafNodes b/c don't want to count in the word 的
                # -1 for numNTnodes b/c don't want to count in VP‧的
                maxDepthFromNode, numLeafNodes, numNTnodes, numChar = \
                    self.traverse(n, 0, -1, -1, -1)

                # store info about this RC
                self.RCdepths.append(maxDepthFromNode-n.depth)
                self.RCs[RCcounter] = {'RCdepth':maxDepthFromNode-n.depth,
                                       'numLeafNodes':numLeafNodes,
                                       'numNTnodes':numNTnodes,
                                       'numChar':numChar}

                # print info:
                print('maxDepth of current RC:', maxDepthFromNode-n.depth)
                print('num words             :', numLeafNodes)
                print('num characters        :', numChar)
                print('num phrasal nodes     :', numNTnodes)
                print()

        print('depths all RCs:        {}'.format(self.RCdepths))
        self.numRC = len(self.RCdepths)

    def traverse(self, node, maxDepthFromNode, numLeafNodes, numNTnodes, numChar):
        if len(node.children) == 0: # leaf
            numLeafNodes+=1
            numChar+=len(node.word)
            if node.depth > maxDepthFromNode:
                return node.depth, numLeafNodes, numNTnodes, numChar
        else:
            tmp = maxDepthFromNode
            numNTnodes+=1
            for child in node.children:
                childDepth, numLeafNodes, numNTnodes, numChar = \
                    self.traverse(child, maxDepthFromNode, numLeafNodes, numNTnodes, numChar)
                if childDepth > tmp:
                    tmp = childDepth
            return tmp, numLeafNodes, numNTnodes, numChar

    def getMaxDepthRC(self):
        pass
    
    def printTree(self):
        try:
            self.printTreeHelper(self.root)
        except AttributeError:
            print('bad tree! cannot print it')
    def printTreeHelper(self, node):
        if len(node.children) == 0: # leaf
            print("{}{}".format(node.depth * '   ', node))
        else:
            print("{}{}".format(node.depth * '   ', node))
            for child in node.children:
                self.printTreeHelper(child)

class PCFG():
    def __init__(self):
        self.pcfg = {}
        self.grm_rule = {}
        self.lex_rule = {}
        self.grm_lhss = {} # left hand side symbols for grammar rules
        # grm_lhss is a dict of dicts:
        # {S: {'NP VP':2, 'NP VP NP':3}, VP ...}
        self.sum_lhss = {} # {S: 132, VP: 122, NP: 150, ...} # counts 
        self.weight_lhss = {} # {S: 0.3, VP: 0.28, NP: 0.4}
        self.totalRuleCounts = {} # sum(sum_lhss.values())

    def addGrmRule(self, rule):
        self.grm_rule[rule] = self.grm_rule.get(rule, 0)+1
        lhs = rule.split(' -> ')[0]
        rhs = rule.split(' -> ')[1]
        if lhs in self.grm_lhss:
            self.grm_lhss[lhs][rhs] = self.grm_lhss[lhs].get(rhs, 0) + 1
        else:
            self.grm_lhss[lhs] = {rhs : 1}
    def addLexRule(self, rule):
        self.lex_rule[rule] = self.lex_rule.get(rule, 0)+1

    def getSumWt_lhss(self):
        for lhss in self.grm_lhss.keys():
            # lhss = NP, VP ...
            self.sum_lhss[lhss] = sum(self.grm_lhss[lhss].values())
        self.totalRuleCounts = sum(self.sum_lhss.values())
        for lhss in self.sum_lhss.keys():
            self.weight_lhss[lhss] = self.sum_lhss[lhss] / self.totalRuleCounts

    def getPCFGoneTree(self, treeStr, mytree, verbose=False, funcTag=False):
        # print('\n\n\n')
        # t='VP(NP(Nab:窗|Ncda:外)|PP(P58:隨|NP(Naa:風))|VA11:飄動)'
        # t='NP(NP(VH11:自大|Nab:先生)|Caa:、|NP(VP‧的(VP(VL1:愛|VP(VC31:下|NP(Nac:命令)))|DE:的)|Nab:國王))'
        # t='NP(NP(NP(VH11:自大|Nab:先生)|Caa:、|NP(VP‧的(VP(VL1:愛|VP(VC31:下|NP(Nac:命令)))|DE:的)|Nab:國王))|Caa:、|NP(VP‧的(VP(VD1:賣|NP(Nab:解渴丸))|DE:的)|Nab:商人))'
        # t='NP(NP(VP‧的(VP(VD1:賣|NP(Nab:解渴丸))|DE:的)|Nab:商人)|X:yy|VP(XX:yy))'
        # print(t)

        # -------------- #
        # pre-processing
        # -------------- #
        treeStr = '('+treeStr+')'
        print('Now building the tree:')
        print(treeStr)

        # tree 200 is bad: (新出版的書)
        if ':' not in treeStr:
            print('bad tree!')
            return

        # index of ( or )
        indBrc = [pos for pos, char in enumerate(treeStr) if char == '(' or char == ')' or char == '|']
        # print(indBrc)

        counter_ntn = 0 # non-terminal node, which includes phrasal nodes AND pos tags!
        stack = []
        
        i = 0

        while i < len(indBrc): # i is the index in indBrc[]
            # max depth
            if len(stack) > mytree.maxDepth:
                mytree.maxDepth = len(stack)
            if (treeStr[indBrc[i]] == '(') or (treeStr[indBrc[i]] == '|'): # and t[indBrc[indOfBrc+1]] == '(':
                if (treeStr[ indBrc[i+1] ] == ')') or (treeStr[ indBrc[i+1] ] == '|'):
                    # ---------------------------- #
                    # terminal node, lexical rules
                    # ---------------------------- #
                    counter_ntn += 1
                    
                    tmp = treeStr[(indBrc[i] + 1) : indBrc[i + 1]] # NR 中
                    # print(indBrc[i+1])
                    # print(tmp)
                    if ':' not in tmp:
                        print('bad tree! at {}'.format(tmp))
                        break
                    tmp = tmp.split(':')
                    node_tmp = Node(tmp[0], tmp[1]) # NR, 中
                    node_tmp.depth = len(stack)
                    mytree.leafNodes.append(node_tmp)
                    # print('terminal node:', tmp, 'No.{}'.format(counter_ntn))
                    rule = tmp[0] + ' -> ' + tmp[1]
                    # ----------------------------------------
                    self.addLexRule(rule)
                    # ----------------------------------------

                    # TODO will this happen? probably not
                    if counter_ntn == 1: # root
                        mytree.root = node_tmp

                    # add to the children of first node in stack
                    stack[-1].children.append(node_tmp)

                    if (treeStr[ indBrc[i] ] == '(') and (treeStr[ indBrc[i+1] ] == ')'):
                        i += 1 # skip the ')' in terminal node (NR 中)
                    else: # all other 3 circumstances
                        i += 1
                    continue # this is used to skip i+=1 at the end of while loop

                else:
                    # ---------------------------- #
                    # a phrasal node, grammar rule
                    # ---------------------------- #
                    counter_ntn += 1
                    tag = treeStr[ (indBrc[i] + 1) : indBrc[i+1] ]

                    node_tmp = Node(tag)
                    node_tmp.depth = len(stack)
                    mytree.nonTermNodes.append(node_tmp)
                    # print('phrasal node:', tag, 'No.{}'.format(counter_ntn))

                    if counter_ntn == 1: # root
                        mytree.root = node_tmp
                    else:
                        # if not root, append to child
                        stack[-1].children.append(node_tmp)

                    # add to stack
                    stack.append(node_tmp)

            if treeStr[indBrc[i]] == ')': # pop a node from the stack
                # print(len(stack))
                if len(stack) != 0:
                    lastNode = stack.pop(-1)
                    LHS = lastNode.tag
                    RHS = ' '.join([x.tag for x in lastNode.children])
                    rule = LHS + ' -> ' + RHS
                    # print(rule)
                    # ----------------------------------------
                    self.addGrmRule(rule)
                    # ----------------------------------------
                else:  # this always happens once at the end
                    # print('pop from empty stack')
                    pass
            i+=1

        # make sure nothing is left in stack
        # print(len(stack))
        assert len(stack) == 0

    def getPCFG(self, trees, verbose=False, funcTag=False):

        treeCounter=0
        for treeStr in trees:
            mytree = Tree()
            treeCounter+=1
            print('tree ', treeCounter)
            self.getPCFGoneTree(treeStr, mytree, verbose, funcTag)

        if verbose:
            print()

            print('\nlex_rule:')
            for k, v in self.lex_rule.items(): # key is rule, value is count
                print('{:>10}\t{}'.format(v, k))
            
            print('\ngrm_rule:')
            for k, v in self.grm_rule.items():
                print('{:>10}\t{}'.format(v, k))

            print()
            print('num of lex rules:', len(self.lex_rule))
            print('num of grm rules:', len(self.grm_rule))

if __name__ == '__main__':
    main()

