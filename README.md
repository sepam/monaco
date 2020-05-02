![](https://img.shields.io/github/license/sepam/monaco?style=flat-square)

<h1 align="left">
monaco
<img src="roulette.jpg" alt="monaco" height="120" width="120" align="right"/>
</h1>

<br>
<br>
<br>
<br>


Estimating the time it takes to complete a task or project is one the 
biggest challenges in task and project planning. Monaco helps you make 
better task estimations by modeling tasks as **random processes**.

<h1 align="center">
<img src="example/task_definition.png" alt="Task" height="395" width="698" align="center"/>
</h1>
<br>

Defining a **Task** is easy:

    task = Task(name='Task', min=3, mode=4, max=9, estimator='triangular')

<br>

**Projects** are sequences of tasks:

<h1 align="center">
<img src="example/project_estimation.png" alt="Project" height="130" width="1121" align="center"/>
</h1>

<br>

**Tasks** can be added to **Projects**:

    # initiate a project
    project = Project(name='Build Machine Learning App')

    # define tasks and duration (in this case: number of days)
    task1 = Task(name='Train model', min=1, max=5, estimator='uniform')
    task2 = Task(name='Deploy Application', min=1, mode=2, max=3, estimator='uniform')
    
    # define task sequence
    project.add_task(task1)
    project.add_task(task2)
 
<br>

## Monte Carlo Simulation

Monaco can estimate the duration of a project by simulating many project cycles 
using Monte Carlo Simulation. The [central limit theorem](https://en.wikipedia.org/wiki/Central_limit_theorem) establishes that the 
sum of many independent random variables approximate a normal distribution.   

<br>

**Monte Carlo Simulation** can be done with a single line of code:

    plot = p.plot(n=10000)
    plot.show()

<div align="center"> <img src="example/monte_carlo_estimation.png" alt="Project" height="478" width="593" align="center"/> </div>
<br>

The **likelihood of completing a project** can be read from the 
cumulative distribution. In this example there is an 80% chance that the 
project will be completed under 23 days.

    plot = p.plot(n=10000, hist=False)
    plot.show()

<div align="center"> <img src="example/monte_carlo_cumulative.png" alt="Project" height="478" width="593" align="center"/> </div>

