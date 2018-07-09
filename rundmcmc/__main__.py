
from rundmcmc.make_graph import construct_graph_from_file
import json

import geopandas as gp

from rundmcmc.make_graph import (add_data_to_graph, construct_graph,
                                 get_assignment_dict)
from rundmcmc.partition import Partition
from rundmcmc.updaters import (Tally, boundary_nodes, county_splits, cut_edges,
                               cut_edges_by_part, exterior_boundaries,
                               perimeters)
from rundmcmc.updaters import polsby_popper_updater as polsby_popper
from rundmcmc.updaters import votes_updaters
from rundmcmc.defaults import BasicChain

def main():

    graph = construct_graph_from_file("/Users/caranix/Desktop/Alaska_Chain/merged_alaska.shp", geoid_col="GEOID10")
    df = gp.read_file("/Users/caranix/Desktop/Alaska_Chain/merged_alaska.shp")
    add_data_to_graph(df, graph, ['HOUSEDIST','POPULATION'], id_col='GEOID10')

    assignment = dict(zip(graph.nodes(), [graph.node[x]['HOUSEDIST'] for x in graph.nodes()]))

    updaters = {
        'population': Tally('POPULATION', alias='population'),
        'cut_edges': cut_edges,
        'cut_edges_by_part': cut_edges_by_part
    }

    p = Partition(graph, assignment, updaters)
    print("Starting Chain")


    chain = BasicChain(p, 1000)
    allAssignments = {0 : chain.state.assignment}
    for step in chain:
        allAssignments[chain.counter+1] = step.flips

    with open("chain_output.json", "w") as f:
        f.write(json.dumps(allAssignments))
        #step.assignemnts - dictionary from each node to assignment
        

    '''
    chain, chain_func, scores, output_func, output_type = read_basic_config("alaska_config.ini")
    print("setup the chain")

    output = chain_func(chain)
    print("ran the chain")

    output_func(output, scores, output_type)
    '''


if __name__ == "__main__":
    main()
