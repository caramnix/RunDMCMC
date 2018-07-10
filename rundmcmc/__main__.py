import functools
import networkx
import json
from rundmcmc.validity import L1_reciprocal_polsby_popper, within_percent_of_ideal_population

from rundmcmc.run import pipe_to_table
from rundmcmc.scores import efficiency_gap, mean_median, mean_thirdian

import matplotlib.pyplot as plt

from rundmcmc.make_graph import construct_graph_from_file
import json

import geopandas as gp

from rundmcmc.scores import (efficiency_gap, mean_median)
from rundmcmc.make_graph import (add_data_to_graph, construct_graph,
                                 get_assignment_dict)
from rundmcmc.partition import Partition
from rundmcmc.updaters import (Tally, votes_updaters, boundary_nodes, county_splits, cut_edges,
                               cut_edges_by_part, exterior_boundaries,
                               perimeters)
from rundmcmc.updaters import polsby_popper_updater as polsby_popper
from rundmcmc.updaters import votes_updaters
from rundmcmc.defaults import BasicChain

def main():

    #graph = construct_graph_from_file("/Users/caranix/Desktop/Alaska_Chain/AK_data.shp", geoid_col="DISTRICT")

    with open('./alaska_graph.json') as f:
        data = json.load(f)
    graph = networkx.readwrite.json_graph.adjacency_graph(data)

    df = gp.read_file("/Users/caranix/Desktop/Alaska_Chain/AK_data.shp") #    assignment = dict(zip(graph.nodes(), [graph.node[x]['HOUSEDIST'] for x in graph.nodes()]))
    add_data_to_graph(df, graph, ['join_Distr', 'POPULATION', 'join_Dem', 'join_Rep', 'perc_Dem', 'perc_Rep', 'AREA'], id_col='DISTRICT')
    data = json.dumps(networkx.readwrite.json_graph.adjacency_data(graph))
    with open('./alaska_graph.json', 'w') as f:
        f.write(data)

    assignment = dict(zip(graph.nodes(), [graph.node[x]['join_Distr'] for x in graph.nodes()]))

    updaters = {
        'population': Tally('POPULATION', alias='population'),
        'cut_edges': cut_edges,
        'cut_edges_by_part': cut_edges_by_part,
        **votes_updaters(['join_Dem', 'join_Rep'], election_name='12'),
        'perimeters': perimeters,
        'exterior_boundaries': exterior_boundaries,
        'boundary_nodes': boundary_nodes,
        'cut_edges': cut_edges,
        'areas': Tally('AREA', alias='areas'),
        'polsby_popper' : polsby_popper
    }


    p = Partition(graph, assignment, updaters)
    print("Starting Chain")


    chain = BasicChain(p, 1000000)
    allAssignments = {0 : chain.state.assignment}
    for step in chain:
        allAssignments[chain.counter+1] = step.flips
       # print(mean_median(step, 'join_Dem%'))

   # with open("chain_outputnew.json", "w") as f:
   #     f.write(json.dumps(allAssignments))



    #efficiency_gap(p)

   # mean_median(p, 'join_Dem%')

    scores = {
        'Mean-Median': functools.partial(mean_median, proportion_column_name='join_Dem%'),
        'Mean-Thirdian': functools.partial(mean_thirdian, proportion_column_name='join_Dem%'),
        'Efficiency Gap': functools.partial(efficiency_gap, col1='join_Dem', col2='join_Rep'),
        'L1 Reciprocal Polsby-Popper': L1_reciprocal_polsby_popper
    }

    initial_scores = {key: score(p) for key, score in scores.items()}

    table = pipe_to_table(chain, scores)

    fig, axes = plt.subplots(2, 2)

    quadrants = {
        'Mean-Median': (0, 0),
        'Mean-Thirdian': (0, 1),
        'Efficiency Gap': (1, 0),
        'L1 Reciprocal Polsby-Popper': (1, 1)
    }

    for key in scores:
        quadrant = quadrants[key]
        axes[quadrant].hist(table[key], bins=50)
        axes[quadrant].set_title(key)
        axes[quadrant].axvline(x=initial_scores[key], color='r')
    plt.show()





    '''
    chain, chain_func, scores, output_func, output_type = read_basic_config("alaska_config.ini")
    print("setup the chain")

    output = chain_func(chain)
    print("ran the chain")

    output_func(output, scores, output_type)
    '''


if __name__ == "__main__":
    main()

    # step.assignemnts - dictionary from each node to assignment