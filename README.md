# Dependency Tracking Tool

Script for parsing task dependencies as captured in a workflowy list export, and creating a dot dependency graph.

Includes logic for determining/presenting which tasks are complete, which can be done next, and which are awaiting external events.

## Notation:

The graph is represented in workflowy in dot notation, where each workflowy list entry represents one node or edge.

For instance, the dependency of task A on task B can be captured in a workflowy item as
```text
task A -> task B
```

The node for task A can be created independently of an edge by entering it on it's own line:

```text
task A
```

Some additional mark up is supported for adding task metadata:

* a task can be specified as complete by entering the task on it's own as a workflowy item, then setting it as complete in workflowy (ctrl-enter)
* a task will be recognised as awaiting some external event if it's name starts with 'await'
* additional information about the task can be added as workflowy comments on the task item, which will be converted into node labels on that task in the dot graph representation

## Usage:

1) In workflowy, select the task list, then `export` -> `plain text`
2) Copy/paste from the export window into a file in this directory named `deps.txt`
3) Run `./create_dep_graph.py | xdot -` to generate the graph and view in `xdot` interactive visualiser.

See also `./create_dep_graph.py -h` for options for generating lists of next items and awaitables.