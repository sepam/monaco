from monaco import Task, Project

# Create project
project = Project(name="App Development", unit='days')

# ============================================
# Phase 1: Design & Development (Parallel)
# ============================================
design_ui = Task(name="Design UI", min_duration=1, max_duration=3, estimator='uniform')

# Frontend track
develop_frontend = Task(name="Develop frontend", min_duration=7, max_duration=14, estimator='uniform')

# Backend track (parallel to frontend)
develop_backend = Task(name="Develop backend", min_duration=5, max_duration=10, estimator='uniform')

# ============================================
# Phase 2: Testing (Parallel)
# ============================================
test_frontend = Task(name="Test frontend", min_duration=1, max_duration=3, estimator='uniform')
test_backend = Task(name="Test backend", min_duration=2, max_duration=4, estimator='uniform')

# ============================================
# Phase 3: UAT (After all testing)
# ============================================
uat = Task(name="User Acceptance Testing", min_duration=2, max_duration=5, estimator='uniform')

# ============================================
# Phase 4: Release & Deployment
# ============================================
release_app = Task(name="Release app", min_duration=1, max_duration=2, estimator='uniform')
deploy_backend = Task(name="Deploy backend", min_duration=1, max_duration=1.5, estimator='uniform')
go_live = Task(name="Go live", min_duration=0.25, max_duration=0.75, estimator='uniform')

# ============================================
# Add tasks to project with dependencies
# ============================================
# Project Flow:
# Design UI → Develop Frontend → Test Frontend ↘
#                                                 UAT → Release App
# Develop Backend → Test Backend ---------------↗  ↘ Deploy Backend → Go Live
# ============================================

project.add_task(design_ui)
project.add_task(develop_frontend, depends_on=[design_ui])
project.add_task(develop_backend)
project.add_task(test_frontend, depends_on=[develop_frontend])
project.add_task(test_backend, depends_on=[develop_backend])
project.add_task(uat, depends_on=[test_frontend, test_backend])
project.add_task(release_app, depends_on=[uat])
project.add_task(deploy_backend, depends_on=[uat])
project.add_task(go_live, depends_on=[deploy_backend])

# ============================================
# Run simulation and get statistics
# ============================================
print(f"\n{'='*60}")
print(f"Project: {project.name}")
print(f"{'='*60}\n")

stats = project.statistics()

# Display key metrics
print("Project Duration Estimates:")
print(f"  • Mean (Expected):     {stats['mean']:.1f} {project.unit}")
print(f"  • Median (50th %ile):  {stats['median']:.1f} {project.unit}")
print(f"  • 90% Confidence:      {stats['percentiles']['p90']:.1f} {project.unit}")
print(f"  • Best Case (10th):    {stats['percentiles']['p10']:.1f} {project.unit}")
print(f"  • Worst Case (95th):   {stats['percentiles']['p95']:.1f} {project.unit}")
print(f"  • Std Deviation:       {stats['std_dev']:.1f} {project.unit}")

print(f"\nInterpretation:")
print(f"  There's a 50% chance this project completes in {stats['median']:.1f} days or less")
print(f"  There's a 90% chance this project completes in {stats['percentiles']['p90']:.1f} days or less")
print(f"  To be 95% confident, plan for {stats['percentiles']['p95']:.1f} days")

# Optional: Generate and save visualization
# Uncomment to display plot interactively (will block until plot window is closed):
# project.plot()
# Or save to file:
# project.plot(save_path='example/project_timeline.png')
