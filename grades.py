#!/usr/bin/python3

import os
import sys
import argparse
import re

version = "1.0"
show_warnings = True
weight_precision = 1
assignment_precision = 3
final_precision = 3

class Assignment:
	def __init__(self, name="", earned=-1.0, total=-1.0):
		self.name = name
		self.earned = earned
		self.total = total
	def __repr__(self):
		p = assignment_precision
		space = " "*(24-len(self.name))
		percent = "N/A"
		if self.total > 0.0:
			percent = "%.*f %%" % (p, 100*self.earned/self.total)
		s = "    %s%s%10.*f%16.*f%16s" % (self.name, space, p, self.earned, p, self.total, percent)
		return s
	@classmethod
	def parse(cls, line):
		assignment = cls()
		line = [word.strip(" \t%") for word in re.split("  |\t", line) if len(word.strip()) > 0]
		size = len(line)
		try:
			if size > 0:
				assignment.name = line[0]
				assignment.earned = 0.0
				assignment.total = 0.0
			if size > 1:
				assignment.earned = float(line[1])
				assignment.total = assignment.earned
			if size > 2:
				assignment.total = float(line[2])
		except Exception as e:
			if show_warnings:
				print("warning: couldn't parse assignment '" + assignment.name + "'", file=sys.stderr)
		return assignment
	@classmethod
	def is_valid(cls, a):
		other = cls()
		if a.name == other.name:
			return False
		if a.earned == other.earned:
			return False
		if a.total == other.total:
			return False
		return True

class Criteria():
	def __init__(self, name="", weight=-1.0, assignments=[], earned=-1.0, total=-1.0):
		self.name = name
		self.weight = weight
		self.assignments = assignments
	def __repr__(self):
		s = "%s (%.*f %%)\n" % (self.name, weight_precision, 100*self.weight)
		for a in self.assignments:
			s += str(a) + "\n"
		if "final" not in self.name.lower():
			s += str(Assignment("Total", self.earned, self.total)) + "\n"
		return s
	@classmethod
	def parse(cls, section):
		criteria = cls("", -1.0, [], -1.0, -1.0)
		section = section.split("\n")
		try:
			heading = section[0].split("(")
			criteria.name = heading[0].strip()
			criteria.weight = float(heading[1].strip(" \t%)"))/100.0
		except Exception as e:
			pass
		for line in section[1:]:
			criteria.add(Assignment.parse(line))
		earned = 0.0
		total = 0.0
		for a in criteria.assignments:
			earned += a.earned
			total += a.total
		criteria.earned = earned
		criteria.total = total
		return criteria
	@classmethod
	def is_valid(cls, c):
		other = cls()
		if c.name == other.name:
			return False
		if c.weight == other.weight:
			return False
		if c.assignments == other.assignments:
			return False
		return True
	def add(self, a):
		if Assignment.is_valid(a) and  "total" not in a.name.lower():
			self.assignments.append(a)

class GradeBook():
	def __init__(self, criteria=[]):
		self.criteria = criteria
	def __repr__(self):
		s = ""
		final = 0.0
		for c in self.criteria:
			if c.total > 0.0:
				final += c.weight * c.earned / c.total
			s += str(c) + "\n"
		s += "Final Grade: %.*f %%\n" % (final_precision, 100 * final)
		return s
	@classmethod
	def parse(cls, txt):
		gradeBook = cls([])
		for section in txt.split("\n\n"):
			gradeBook.add(Criteria.parse(section))
		return gradeBook
	def add(self, c):
		if Criteria.is_valid(c):
			self.criteria.append(c)

def main(argv):
	parse = argparse.ArgumentParser(description="Parse and calculate grades from file.")
	parse.add_argument("-v", "--version", action="version", version="%(prog)s " + version)
	parse.add_argument("input", metavar="<grades-file>", nargs=1, help="grades file")
	parse.add_argument("-u", "--update", dest="update", action="store_true", help="recalculate and update the grades file")
	parse.add_argument("-o", dest="output", metavar="<output-file>", nargs=1, help="optional output file")
	args = parse.parse_args(argv)

	input_file = args.input[0]
	output_file = args.output

	if output_file:
		output_file = output_file[0]

	if not os.path.exists(input_file):
		print("error: '" + input_file + "' doesn't exist", file=sys.stderr)
		exit(1)

	if args.update:
		if show_warnings and output_file:
			print("warning: not outputing to '" + output_file + "' because update flag specified", file=sys.stderr)
		output_file = input_file
	elif show_warnings and output_file and os.path.exists(output_file):
		if show_warnings:
			print("warning: '" + output_file + "' will be overwritten", file=sys.stderr)

	f = open(input_file, "r")
	txt = f.read()
	end = f.newlines
	f.close()

	grades = GradeBook.parse(txt)
	txt = str(grades)

	if output_file:
		f = open(output_file, "w", newline=end)
		f.write(txt)
		f.close()
	else:
		for line in txt.split("\n")[:-1]:
			print(line, end=end)

if __name__ == '__main__':
	main(sys.argv[1:])
