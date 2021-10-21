#!/usr/bin/env python

"""
Create Dep Graph.

Usage:
  create_dep_graph.py [--list-next] [--list-awaiting] [--koi-list]
  create_dep_graph.py -h | --help

Options:
  -h --help         Show this screen.
  --list-next       Print all 'next' items
  --list-awaiting   Print all 'next' items
  --koi-list        Instead of plotting a graph, print Koi's todo list
"""

from typing import List, Tuple
import re
import networkx as nx
from textwrap import wrap
from docopt import docopt


def read_deps(deps_file:str) -> Tuple[List[str], List[str]]:
    """
    Return list of dependencies
    """
    
    with open(deps_file, encoding="utf-8") as f:
        lines = f.readlines()

    # convert to lower case
    lines = [l.lower() for l in lines]

    # extract node info
    node_info = extract_node_info(lines)

    # only use lines starting with "-"
    lines = filter(lambda l : l.startswith("-"), lines)

    # strip leading "-"
    lines = [re.sub("^-", "", l).strip() for l in lines] 

    # dependencies: (contain ->)
    deps_lines = list(filter(lambda l : "->" in l, lines))

    return deps_lines, node_info

# functions to aid parsing:
def is_edge_line(line:str) -> bool:
    return line.startswith("-") and "->" in line

def is_node_line(line:str) -> bool:
    return line.startswith("-") and not is_edge_line(line) and not line.replace("-","").strip() == ""

def is_comment_start_line(line:str) -> bool:
    return line.strip().startswith("\"")

def is_comment_end_line(line:str) -> bool:
    return line.strip().endswith("\"")

def get_node_name(line:str) -> str:
    line = re.sub("^-", "", line).strip()
    line = re.sub("^\[complete\]", "", line).strip()
    return line

def is_complete_line(line:str) -> bool:
    return "[complete]" in line.lower()
    
def read_comment(i:int, lines:List[str]) -> Tuple[str, int]:
    """
    Read comment starting at line i
    """
    comment_lines = []
    while True:
        comment_lines += wrap(lines[i].strip(), 30)
        if comment_lines[-1].endswith("\""):
            break
        else:
            i += 1
            
    newline = "\l" # dot notation
    return (newline.join(comment_lines).replace("\"","") + newline, i)


def extract_node_info(lines:dict) -> List[dict]:
    """
    Read node lines (define nodes)
    return dict of dicts node_name -> [complete, comment]

    Node lines may be followed by node comments
    Node comments:
    follow a node line
    Start with a "
    continue (potentially over multiple lines)
    until line ends with "
    """
    node_info = {}

    i = 0 
    while i < len(lines):
        line = lines[i]
        if is_node_line(line):
            node_name = get_node_name(line)
            assert node_name not in node_info.keys(), f"Duplicate node info found for node: {node_name}"
            complete = is_complete_line(line)
            i+=1 
            if i < len(lines) and is_comment_start_line(lines[i]):
                comment, i = read_comment(i, lines)
            else:
                comment = ""
            node_info[node_name] = dict(
                name=node_name,
                complete=complete,
                comment=comment,
            )
        else:
            i += 1

    return node_info

def print_graph_header():
    print("digraph G {")
    print("rankdir=\"LR\"")
    print()

def print_graph_footer():
    print("}")

def print_dep(dep_str: str):
    try:
        parent, child = dep_str.split("->")
    except ValueError:
        return
    print(f"   \"{parent.strip()}\" -> \"{child.strip()}\"")


def get_node_fill_color(node_str:str, G:nx.DiGraph):
    if G.nodes[node]["complete"]:
        return "lightgrey"
    elif G.nodes[node]["waiting"]:
        return "lightblue"
    elif G.nodes[node]["next"]:
        return "green"
    else:
        return "white"
        

def print_node(node:str, G:nx.DiGraph):
    fill_color = get_node_fill_color(node, G)
    label = f"""{node}\l\l{G.nodes[node]["comment"]}"""

    # # Code for anonymising the node lables, used to generate the example graph in the readme
    # import random
    # import string
    # label= "task_" + ''.join(random.choice(string.ascii_lowercase) for _ in range(5))

    print(f"    \"{node}\" [label=\"{label}\",style=filled,fillcolor={fill_color}]")

def graph_from_deps(deps:List[str]) -> nx.DiGraph:
    G = nx.DiGraph()
    for dep in deps:
        parent, child = dep.split("->")
        parent = parent.strip()
        child = child.strip()
        G.add_nodes_from([parent, child], complete=False)
        G.add_edge(parent, child)
    return G


def set_node_info(node_info:dict, G:nx.DiGraph):

    # set nodes complete and comment
    for node in G.nodes:

        if node in node_info.keys():
            complete = node_info[node]["complete"]
            comment = node_info[node]["comment"]
        else:
            complete = False
            comment = ""
    
        G.nodes[node]["complete"] = complete
        G.nodes[node]["comment"] = comment
    
    # set nodes next and waiting
    for node in G.nodes:
        
        # 'next' if not complete and all parents complete
        all_parents_complete = True
        for parent in G.predecessors(node):
            if not G.nodes[parent]["complete"]:
                all_parents_complete = False        
        is_next = (not complete) and all_parents_complete

        is_waiting = is_next and node.startswith("await")


        G.nodes[node]["waiting"] = is_waiting
        G.nodes[node]["next"] = is_next


            

def add_node_comments(G:nx.DiGraph, comments:dict()):
    for node, comment in comments.items():
        G.nodes[node]["comment"] = comment

def plot_graph(G:nx.DiGraph):
    import matplotlib.pyplot as plt
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.show()

def print_koi_todo_list(G:nx.DiGraph):
    print("Koi TODO list:")
    for node in G.successors("koi"):
        if G.nodes[node]["next"]:
            print(f" - {node}")

def print_todo_list(G:nx.DiGraph):

    print("TODO list:")
    for node in G.nodes():
        if G.nodes[node]["next"] and not G.nodes[node]["waiting"]:
            print(f" - {node}")
            # comment = G.nodes[node]["comment"]
            # if comment:
            #     print(f"    {comment}")

def print_awaiting_list(G:nx.DiGraph):

    print("Currently awaiting:")
    for node in G.nodes():
        if G.nodes[node]["next"] and G.nodes[node]["waiting"]:
            print(f" - {node}")
            # comment = G.nodes[node]["comment"]
            # if comment:
            #     print(f"    {comment}")

if __name__ == "__main__":

    arguments = docopt(__doc__)
    
    deps_file = "deps.txt"
    deps, node_info = read_deps(deps_file)

    G = graph_from_deps(deps)
    set_node_info(node_info, G)

    if arguments["--koi-list"]:
        print_koi_todo_list(G)
    elif arguments["--list-next"]:
        print_todo_list(G)
    elif arguments["--list-awaiting"]:
        print_awaiting_list(G)
    else:
        print_graph_header()

        for d in deps:
            print_dep(d)
        
        for node in G.nodes:
            print_node(node, G)

        print_graph_footer()

