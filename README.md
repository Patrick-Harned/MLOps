---
title: "Lowes"
output:
  html_document:
    keep_md: true
---

## Solution Description:

A Continous Delivery Integration Pipeline to manage MLOps workflows. The Pipeline will consist of a bitbucket or git repository storing source code for a machine learning model. Commits will trigger a container image build that will be deployed on an OCP cluster running Cloud Pak for Data. The Container will run code to 1. Store a machine learning model in a WML repository, create a deployment in WML for the model, create an openscale subscription for the model, score the model against target data set, return the quality metrics reported by openscale and then cleanup. 

### Architecture Diagram

<!--html_preserve--><div id="htmlwidget-e3f1b2f85509e281b4d4" style="width:960px;height:960px;" class="grViz html-widget"></div>
<script type="application/json" data-for="htmlwidget-e3f1b2f85509e281b4d4">{"x":{"diagram":"\ndigraph boxes_and_circles {\n\n  # a \"graph\" statement\n  graph [overlap = false, fontsize = 20, rankdir=TB, style=filled]\n\n  # several \"node\" statements\n  node [shape = doublecircle,\n        fontname = Helvetica]\n        A[label=\"Data Scientist\", shape=house]\n\n\n  node [shape = record,\n        fixedsize = false,\n        width = 0.9] // sets as circles\n  1[label =\"{SrcRepository | src/model/test.py,train.py | model.py,config.json }\", shape=record]\n  \n\n  \n  subgraph cluster_0{\n  style=filled;\n\t\tcolor=lightgrey;\n\t\tnode [style=filled,color=white, shape=doublecircle]\n\t\t4[label=\"Trigger Container \", shape = doublecircle]\n\t\tlabel = \"OCP Platform\";\n\t\t4->5 [label=\"Deploys Model\"]\n\t\t4->6 [label=\"Susbscribes Model\"]\n\t\t2[label = \"Jenkins Server\", shape =doublecircle]\n\t\tsubgraph cluster_1{\n\t\tstyle=filled;\n\t\tcolor=lightblue;\n\t\tlabel= \"CloudPak For Data\"\n\t\tnode[style=filled,color=white]\n\t\t5[label=\"WML\"]\n\t\t6[label=\"AIOS\"]\n\t\t7[label=\"ModelDeployment\"]\n\t\t6 -> 7 [label=\"AIOS gathers \n accuracy metrics\"]\n\t\t5->7\n\t\t}\n  }\n  \n  B[shape=cylinder, label = \"Performance metrics and logs\"]\n\n  # several \"edge\" statements\n  A -> 1\n  1 -> 2\n  2 -> 4 \n  4 -> B[label = \"Output from WML/OS\"]\n  \n}\n","config":{"engine":"dot","options":null}},"evals":[],"jsHooks":[]}</script><!--/html_preserve-->


## Project Structure

```project
|   README.md
|   Dockerfile
|   bin/
|    |  - __init__.py/init.sh 
|    |
|   model/
|       |
|       src/
|         | -  model.py
|         | -  config.json
|         | -  train.py
|         | -  test.py
```
