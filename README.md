
title: "Lowes"

## Solution Description:

A Continous Delivery Integration Pipeline to manage MLOps workflows. The Pipeline will consist of a bitbucket or git repository storing source code for a machine learning model. Commits will trigger a container image build that will be deployed on an OCP cluster running Cloud Pak for Data. The Container will run code to 1. Store a machine learning model in a WML repository, create a deployment in WML for the model, create an openscale subscription for the model, score the model against target data set, return the quality metrics reported by openscale and then cleanup. 

### Architecture Diagram
![Alt text](https://g.gravizo.com/source/custom_mark10/https%3A%2F%2Fraw.githubusercontent.com%2FPatrick-Harned%2Fmaster%2FREADME.md)

```
![Alt text](https://g.gravizo.com/source/custom_mark10/https%3A%2F%2Fraw.githubusercontent.com%2FPatrick-Harned%2Fmaster%2FREADME.md)
<details> 
<summary></summary>
custom_mark10

digraph boxes_and_circles {

  # a 'graph' statement
  graph [overlap = false, fontsize = 20, rankdir=TB, style=filled]

  # several 'node' statements
  node [shape = doublecircle,
        fontname = Helvetica]
        A[label='Data Scientist', shape=house]


  node [shape = record,
        fixedsize = false,
        width = 0.9] // sets as circles
  1[label ='{SrcRepository | src/model/test.py,train.py | model.py,config.json }', shape=record]
  

  
  subgraph cluster_0{
  style=filled;
		color=lightgrey;
		node [style=filled,color=white, shape=doublecircle]
		4[label='Trigger Container ', shape = doublecircle]
		label = 'OCP Platform';
		4->5 [label='Deploys Model']
		4->6 [label='Susbscribes Model']
		2[label = 'Jenkins Server', shape =doublecircle]
		subgraph cluster_1{
		style=filled;
		color=lightblue;
		label= 'CloudPak For Data'
		node[style=filled,color=white]
		5[label='WML']
		6[label='AIOS']
		7[label='ModelDeployment']
		6 -> 7 [label='AIOS gathers \n accuracy metrics']
		5->7
		}
  }
  
  B[shape=cylinder, label = 'Performance metrics and logs']

  # several 'edge' statements
  A -> 1
  1 -> 2
  2 -> 4 
  4 -> B[label = 'Output from WML/OS']
  
}
custom_mark10
</details>
```


Simple html tag

You can use Gravizo including an image tag <img src='https://g.gravizo.com/svg? follow by a graph description writed in DOT, PlantUML or UMLGraph, and then close the image tag

<img src='https://g.gravizo.com/svg?
 digraph G {
   main -> parse -> execute;
   main -> init;
   main -> cleanup;
   execute -> make_string;
   execute -> printf
   init -> make_string;
   main -> printf;
   execute -> compare;
 }
'/>

![Alt text](https://g.gravizo.com/svg?
  digraph G {
    aize ="4,4";
    main [shape=box];
    main -> parse [weight=8];
    parse -> execute;
    main -> init [style=dotted];
    main -> cleanup;
    execute -> { make_string; printf}
    init -> make_string;
    edge [color=red];
    main -> printf [style=bold,label="100 times"];
    make_string [label="make a string"];
    node [shape=box,style=filled,color=".7 .3 1.0"];
    execute -> compare;
  }
)


![Alt text](https://g.gravizo.com/svg?
digraph boxes_and_circles {

  graph [overlap = false, fontsize = 20, rankdir=TB, style=filled]

  node [shape = doublecircle, fontname = Helvetica]
  A[label='Data Scientist', shape=house]


  node [shape = record,fixedsize = false, width = 0.9]
  1[label ='{SrcRepository | src/model/test.py,train.py | model.py,config.json }', shape=record]
  

  
  subgraph cluster_0{
  style=filled;
		color=lightgrey;
		node [style=filled,color=white, shape=doublecircle]
		4[label='Trigger Container ', shape = doublecircle]
		label = 'OCP Platform';
		4->5 [label='Deploys Model']
		4->6 [label='Susbscribes Model']
		2[label = 'Jenkins Server', shape =doublecircle]
		subgraph cluster_1{
		style=filled;
		color=lightblue;
		label= 'CloudPak For Data'
		node[style=filled,color=white]
		5[label='WML']
		6[label='AIOS']
		7[label='ModelDeployment']
		6 -> 7 [label='AIOS gathers accuracy metrics']
		5->7
		}
  }
  
  B[shape=cylinder, label = 'Performance metrics and logs']

  # several 'edge' statements
  A -> 1
  1 -> 2
  2 -> 4 
  4 -> B[label = 'Output from WML/OS']
  
})




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
