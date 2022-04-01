"""
This module contains various useful functions in order to process data or create repeated arrays
"""


# recursively removes empty array from an input deep nested array
def remove_empty(l):
	return list(filter(lambda x: not isinstance(x, (str, list, list)) or x, (remove_empty(x) if isinstance(x, (list, list)) else x for x in l)))


# fill list with 1s - create a check matrix
def create_check_matrix(l):
	for i, sl in enumerate(l):
		for j, ssl in enumerate(sl):
			for k, sssl in enumerate(ssl):
				for m in range(len(sssl)):
					l[i][j][k][m] = 1
	return l


def adjust_column_length(worksheet):
	for col in worksheet.columns:
		max_length = 0
		column = col[0].column  # get column name
		for cell in col:
			try:  # Necessary to avoid error on empty cells
				if len(str(cell.value)) > max_length:
					max_length = len(cell.value)
			except:
				pass
		adjusted_width = (max_length + 5) * 1.2
		worksheet.column_dimensions[column].width = adjusted_width


# TODO : REVISE THIS - I THINK IT'S REDUNDANT
def reset_global_vars(gvars):
	gvars.C1_ICND = 0
	gvars.C15_ICND = 0

	gvars.TOTAL_CELLS = []
	gvars.TOTAL_CELLS_REPS = []
	gvars.TOTAL_CELLS_SEM = []

	gvars.CELL_GENS = []
	gvars.CELL_GENS_REPS = []
	gvars.CELL_GENS_SEM = []

	gvars.CONDITIONS = []
	gvars.MAX_DIV_PER_CONDITIONS = []

	gvars.C1_PREV_SS, gvars.C1_SS = 0., 0.
	gvars.C15_PREV_SS, gvars.C15_SS = 0., 0.
	gvars.C1_CHECK, gvars.C15_CHECK = [], []