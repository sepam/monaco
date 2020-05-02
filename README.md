![](https://img.shields.io/github/license/sepam/monaco?style=flat-square)

<h1 align="left">
monaco
<img src="roulette.jpg" alt="monaco" height="100" width="100" align="right"/>
</h1>

Monaco helps you make better estimations for the duration of your tasks and projects.

---

## Estimating tasks and projects
Estimating the time it takes to complete a task or project is one the most 
biggest challenges in task and project planning.

The time it takes to complete as task is dependent on many factors 
that can not always be controlled or foreseen.

Monaco helps you make better task estimations by modeling tasks as a stochastic process:

<h1 align="center">
<img src="tutorial/task_definition.png" alt="Task" height="493" width="873" align="center"/>
</h1>
<br>

    task = Task(name='Task', min=3, mode=4, max=9, estimator='triangular')

<br>

Projects are sequences of tasks:

<h1 align="center">
<img src="tutorial/project_estimation.png" alt="Project" height="344" width="2242" align="center"/>
</h1>

<br>

    # initiate project
    p = Project(name='My Example Project')

    # define tasks and duration in number of days
    t1 = Task(name='Problem definition', min=1, max=5, estimator='uniform')
    t2 = Task(name='EDA', min=1, mode=2, max=3, estimator='uniform')
    
    # define task sequence
    p.add_task(t1)
    p.add_task(t2)
 
<br>

## Monte Carlo Simulation

Monaco can estimate the duration of a project through Monte Carlo Simulation 
of many project cycles. The central limit theorem guarantees that the sum of 
many independent random processes approaches a normal distribution.   

Projects can be simulated easily:

    plot_data = p.plot(n=10000)

<br>
<div> <img src="tutorial/project_estimation.png" alt="Project" height="478" width="593" align="center"/> </div>
<br>

Visualizing the cumulative distribution allows to easily read out the 
likelihood of completing withing a number of days:

<br>
<div> <img src="tutorial/monte_carlo_cumulative.png" alt="Project" height="478" width="593" align="center"/> </div>
<br>
