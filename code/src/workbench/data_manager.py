"""
This script contains functions to further process the input data (e.g. computing errors via standard error of means)

I admit that current data structure is rather complicated (max 4 dimensional array), and far from the optimal method.
My attempt was to minimise work load of creating raw input data file. You will notice that there are multiple functions
to remove empty nested list. This is done due to the fact that it is often the case where number of replicates are not
symmetric across the condition.
"""

from scipy.stats import sem

from src.common.functions import remove_empty


def compute_total_cells(data, conditions, num_tps, gen_per_condition):
	"""
	All parameters are output of file_reader.py object, which consists meta information about the data itself.

	:param data: (nested list) number of cells per generation (4-dimensional array) = data[icnd][itpt][irep][igen]
	:param conditions: (list) names of condition
	:param num_tps: (list) number of time points per condition
	:param gen_per_condition: (list) number of maximum generations per condition
	:return: (tuple) [average total cells, total cells with replicates, standard error of means]
	"""
	num_conditions = len(conditions)

	# this loop computes average total cells
	max_length = 0
	total_cells = [[] for _ in range(num_conditions)]
	for icnd in range(num_conditions):
		for itpt in range(num_tps[icnd]):
			cell = 0.
			for igen in range(gen_per_condition[icnd]+1):
				temp = 0.
				replicate = 0.

				size_of_data = len(data[icnd][itpt][igen])
				# check for single replicate and update
				if size_of_data == 0:
					replicate = 1.
				# loop through replicates
				for datum in data[icnd][itpt][igen]:
					if datum is not None:
						temp += datum
						replicate += 1
					# this finds maximum number of replicates in the experiment (useful for asymmetric data)
					if max_length < size_of_data:
						max_length = size_of_data
				temp = temp / replicate
				cell += temp
			total_cells[icnd].append(cell)

	filtered_total_cells = remove_empty(total_cells)

	# this loop computes total cells for EACH replicates
	total_cells_reps = [[] for _ in range(num_conditions)]
	total_cells_reps2 = [[[] for _ in range(max(num_tps))] for _ in range(num_conditions)]
	for icnd in range(num_conditions):
		for itpt in range(num_tps[icnd]):
			tmp = [0 for _ in range(max_length)]
			for igen in range(gen_per_condition[icnd]+1):
				for irep, datum in enumerate(data[icnd][itpt][igen]):
					tmp[irep] += datum
			for idx in range(len(data[icnd][itpt][igen])):
				total_cells_reps[icnd].append(tmp[idx])
				total_cells_reps2[icnd][itpt].append(tmp[idx])

	filtered_total_cells_reps = remove_empty(total_cells_reps)
	filtered_total_cells_reps2 = remove_empty(total_cells_reps2)

	# compute standard error of mean for replicates
	total_cells_sem = [[] for _ in range(num_conditions)]
	for icnd in range(num_conditions):
		for itpt in range(num_tps[icnd]):
			total_cells_sem[icnd].append(sem(filtered_total_cells_reps2[icnd][itpt]))

	filtered_total_cells_sem = remove_empty(total_cells_sem)

	return filtered_total_cells, filtered_total_cells_reps, filtered_total_cells_sem


def sort_cell_generations(data, conditions, num_tps, gen_per_condition):
	"""
	This function organises cell-generation profile.

	:param data: (nested list) number of cells per generation (4-dimensional array) = data[icnd][itpt][irep][igen]
	:param conditions: (list) names of condition
	:param num_tps: (list) number of time points per condition
	:param gen_per_condition: (list) number of maximum generations per condition
	:return: (tuple) [average cell per gen, cell per gen with replicates, standard error of means]
	"""
	num_conditions = len(conditions)

	# this loop computes average cell numbers : dynamically determines replicates
	max_length = 0
	cell_gens = [[] for _ in range(num_conditions)]
	for icnd in range(num_conditions):
		for itpt in range(num_tps[icnd]):
			gen_arr = []
			for igen in range(gen_per_condition[icnd]+1):
				cell = 0.
				replicate = 0.

				size_of_data = len(data[icnd][itpt][igen])
				if size_of_data == 0:
					replicate = 1.

				for datum in data[icnd][itpt][igen]:
					if datum is not None:
						cell += datum
						replicate += 1.
					if max_length < size_of_data:
						max_length = size_of_data
				cell = cell / replicate

				gen_arr.append(cell)
			cell_gens[icnd].append(gen_arr)

	filtered_cell_gens = remove_empty(cell_gens)

	cell_gens_reps = [[[] for _ in range(max(num_tps))] for _ in range(num_conditions)]
	for icnd in range(num_conditions):
		for itpt in range(num_tps[icnd]):
			tmp = [[] for _ in range(max_length)]
			for igen in range(gen_per_condition[icnd]+1):
				for irep, datum in enumerate(data[icnd][itpt][igen]):
					tmp[irep].append(datum)
			for idx in range(len(data[icnd][itpt][igen])):
				cell_gens_reps[icnd][itpt].append(tmp[idx])

	filtered_cell_gens_reps = remove_empty(cell_gens_reps)

	# resort filtered dataset to compute SEM : schema - [icnd][itpt][igen][irep]
	resorted_data = [
		[
			[
				[] for _ in range(max(gen_per_condition)+1)
			] for _ in range(max(num_tps))
		] for _ in range(num_conditions)
	]
	cell_gens_sem = [
		[] for _ in range(num_conditions)
	]
	for icnd in range(len(filtered_cell_gens_reps)):
		for itpt in range(len(filtered_cell_gens_reps[icnd])):
			for irep, l in enumerate(filtered_cell_gens_reps[icnd][itpt]):
				for igen, datum in enumerate(l):
					resorted_data[icnd][itpt][igen].append(datum)
			tmp = []
			for idx in range(len(resorted_data[icnd][itpt])):
				tmp.append(sem(resorted_data[icnd][itpt][idx]))
			cell_gens_sem[icnd].append(tmp)

	filtered_cell_gens_sem = remove_empty(cell_gens_sem)

	return filtered_cell_gens, filtered_cell_gens_reps, filtered_cell_gens_sem


