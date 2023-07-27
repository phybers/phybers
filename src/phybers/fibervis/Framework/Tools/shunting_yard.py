from collections import deque
from enum import Enum
import numpy as np


class TokenType(Enum):
	NUMBER = 0
	OPERATOR = 1
	LEFTBRACKET = 2
	RIGHTBRACKET = 3


class Associative(Enum):
	LEFT = 0
	RIGHT = 1


class Token:
	value = None
	tokenType = None

	def __init__(self, value=None):
		if value is None:
			return

		self.value = value

		if isinstance(value, str) and len(value) == 1:
			if value == '(':
				self.tokenType = TokenType.LEFTBRACKET
			elif value == ')':
				self.tokenType = TokenType.RIGHTBRACKET
			else:
				self.tokenType = TokenType.OPERATOR
		else:
			self.tokenType = TokenType.NUMBER
			

class LogicalMath:

	MathTable = {'&' : {'func' : np.logical_and, 'nOfOperand' : 2},
				'|' : {'func' : np.logical_or, 'nOfOperand' : 2},
				'!' : {'func' : np.logical_not, 'nOfOperand' : 1},
				'^' : {'func' : np.logical_xor, 'nOfOperand' : 2}}

	PrecedenceTable = {	'|' : 0,
						'^' : 0,
						'&' : 1,
						'!' : 2}

	AssociativeTable = {'&' : Associative.LEFT,
						'|' : Associative.LEFT,
						'!' : Associative.LEFT,
						'^' : Associative.LEFT}


class Math:
	MathTable = {	'^' : {'func' : lambda a,b : pow(a,b), 'nOfOperand' : 2},
					'*' : {'func' : lambda a,b : a*b, 'nOfOperand' : 2},
					'/' : {'func' : lambda a,b : a/b, 'nOfOperand' : 2},
					'+' : {'func' : lambda a,b : a+b, 'nOfOperand' : 2},
					'-' : {'func' : lambda a,b : a-b, 'nOfOperand' : 2}}

	PrecedenceTable = {	'^' : 4,
						'*' : 3,
						'/' : 3,
						'+' : 2,
						'-' : 2}

	AssociativeTable = {'(', Associative.LEFT,
						'^', Associative.RIGHT,
						'*', Associative.LEFT,
						'/', Associative.LEFT,
						'+', Associative.LEFT,
						'-', Associative.LEFT}


def infix2postfix(tokens, precedenceTable):
	if not isinstance(tokens, deque):
		print('shunting_yard: infix2postfix input is not a deque... casting into one.')
		tokens = deque(tokens)

	operatorStack = []
	outputqueue = deque()

	while len(tokens):
		token = tokens.popleft()

		if token.tokenType == TokenType.NUMBER:
			outputqueue.append(token)

		# elif token in functionTable:
			# operatorStack.append(token)

		elif token.tokenType == TokenType.OPERATOR:
			while ( len(operatorStack) and 
				operatorStack[-1].tokenType != TokenType.LEFTBRACKET and 
				precedenceTable[token.value] < precedenceTable[operatorStack[-1].value]):

				outputqueue.append(operatorStack.pop())
			operatorStack.append(token)

		elif token.tokenType == TokenType.LEFTBRACKET:
			operatorStack.append(token)

		elif token.tokenType == TokenType.RIGHTBRACKET:
			while len(operatorStack) and operatorStack[-1].tokenType != TokenType.LEFTBRACKET:
				outputqueue.append(operatorStack.pop())

			if not len(operatorStack):
				return -1

			operatorStack.pop()

	while len(operatorStack):
		outputqueue.append(operatorStack.pop())
		if outputqueue[-1].tokenType == TokenType.LEFTBRACKET:
			return -1

	return outputqueue


def postfixEvaluator(tokens, MathTable):
	if not isinstance(tokens, deque):
		print('shunting_yard: postfixEvaluator input is not a deque... casting into one.')
		tokens = deque(tokens)

	stack = []

	while len(tokens):
		token = tokens.popleft()

		if token.tokenType == TokenType.NUMBER:
			stack.append(token)

		else:
			right_operand = stack.pop()

			if MathTable[token.value]['nOfOperand'] == 1:
				stack.append(Token(MathTable[token.value]['func'](right_operand.value)))
			else:
				left_operand = stack.pop()
				stack.append(Token(MathTable[token.value]['func'](left_operand.value, right_operand.value)))

	if len(stack) == 1:
		return stack.pop()

	else:
		raise ValueError


def shuntingYard(infix, operation='Logical'):
	if operation == 'Logical':
		table = LogicalMath
	elif operation == 'Math':
		table = Math
	else:
		raise ValueError('Not recogniced.')

	infixTokens = deque([Token(i) for i in infix])
	postfixTokens = infix2postfix(infixTokens, table.PrecedenceTable)

	if postfixTokens == -1:
		raise ValueError('shunting_yard: Bracket not paired.')

	# print([i.value for i in postfixTokens])

	evaluation = postfixEvaluator(postfixTokens, table.MathTable)

	return evaluation.value