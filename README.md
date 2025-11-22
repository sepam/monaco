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

    task = Task(name='Task', min_duration=3, mode_duration=4, max_duration=9, estimator='triangular')

<br>

**Projects** are sequences of tasks:

<h1 align="center">
<img src="example/project_estimation.png" alt="Project" height="130" width="1121" align="center"/>
</h1>

<br>

**Tasks** can be added to **Projects** with dependencies:

    # initiate a project
    project = Project(name='Web App Development', unit='days')

    # define tasks with duration estimates
    design_ui = Task(name='Design UI', min_duration=2, mode_duration=3, max_duration=5, estimator='triangular')
    develop_frontend = Task(name='Develop Frontend', min_duration=5, mode_duration=7, max_duration=10, estimator='triangular')
    develop_backend = Task(name='Develop Backend', min_duration=4, mode_duration=6, max_duration=9, estimator='triangular')
    testing = Task(name='Testing', min_duration=2, mode_duration=3, max_duration=5, estimator='triangular')
    deploy = Task(name='Deploy', min_duration=1, max_duration=2, estimator='uniform')

    # add tasks with dependencies (supports parallel and sequential execution)
    project.add_task(design_ui)
    project.add_task(develop_frontend, depends_on=[design_ui])  # frontend needs UI design first
    project.add_task(develop_backend)  # backend can run in parallel
    project.add_task(testing, depends_on=[develop_frontend, develop_backend])  # testing waits for both
    project.add_task(deploy, depends_on=[testing])
 
<br>

## Monte Carlo Simulation

Monaco can estimate the duration of a project by simulating many project cycles 
using Monte Carlo Simulation. The [central limit theorem](https://en.wikipedia.org/wiki/Central_limit_theorem) establishes that the 
sum of many independent random variables approximate a normal distribution.   

<br>

**Monte Carlo Simulation** can be done with a single line of code:

    fig = project.plot(n=10000)

<div align="center"> <img src="example/monte_carlo_estimation.png" alt="Project" height="478" width="593" align="center"/> </div>
<br>

The **likelihood of completing a project** can be read from the
cumulative distribution, accounting for both parallel and sequential task execution.

    fig = project.plot(n=10000, hist=False)

<div align="center"> <img src="example/monte_carlo_cumulative.png" alt="Project" height="478" width="593" align="center"/> </div>

