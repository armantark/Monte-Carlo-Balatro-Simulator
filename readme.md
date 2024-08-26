# Monte Carlo Balatro Simulator

This repository contains Python scripts for simulating and optimizing poker hand strategies (specifically Balatro), focusing on achieving straights and flushes.

## Contents

1. `straight_ai.py`: Q-learning agent for optimizing straight-drawing strategy
2. `flushes_vs_straights.py`: Simulation comparing the likelihood of achieving straights vs. flushes

## Straight AI

The `straight_ai.py` script implements a Q-learning agent to optimize the strategy for drawing straights in poker. 

Key features:
- Q-learning algorithm for decision making
- State encoding based on hand composition
- Reward system for improving hand strength
- Visualization of the agent's strategy

Usage:
```
python straight_ai.py
```

The script will either load a previously trained Q-table or train a new one, then evaluate the agent's performance and visualize its strategy.

## Flushes vs. Straights

The `flushes_vs_straights.py` script simulates drawing for both straights and flushes to compare their relative likelihood.

Key features:
- Optimal (hopefully) discard strategies for both straights and flushes
- Simulation of multiple draw attempts
- Debugging output for individual attempts
- Large-scale simulation to compare success rates

Usage:
```
python flushes_vs_straights.py
```

The script will run debug simulations for both straight and flush attempts, then perform a large number of simulations to compare the success rates.

## Requirements

- Python 3.6+
- No external libraries required