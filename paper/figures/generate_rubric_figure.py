#!/usr/bin/env python3
"""Generate rubric progression figure for the paper."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the data
df = pd.read_csv('/home/ubuntu/training_outputs/debate_full/rubric_progression.csv')

# Set up the style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.dpi'] = 150

# Create figure with 2 subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Colors for speech types
speech_colors = {
    'AC': '#2ecc71',   # Green (AFF constructive)
    'NC': '#e74c3c',   # Red (NEG constructive)
    '1AR': '#27ae60',  # Darker green (AFF rebuttal)
    '1NR': '#c0392b',  # Darker red (NEG rebuttal)
    '2AR': '#1abc9c',  # Teal (AFF final)
    '2NR': '#e67e22',  # Orange (NEG final)
}

# Colors for dimensions
dim_colors = {
    'tactic_execution': '#3498db',   # Blue
    'argumentation': '#9b59b6',       # Purple
    'strategic_impact': '#e74c3c',    # Red
    'opponent_modeling': '#2ecc71',   # Green
}

# ============== LEFT PANEL: By Speech Type ==============
ax1 = axes[0]

# Average across dimensions for each speech type and iteration
speech_avg = df.groupby(['iteration', 'speech_type'])['avg_score'].mean().reset_index()

for speech_type in ['AC', 'NC', '1AR', '1NR', '2AR', '2NR']:
    data = speech_avg[speech_avg['speech_type'] == speech_type]
    ax1.plot(data['iteration'], data['avg_score'],
             marker='o', markersize=4, linewidth=2,
             color=speech_colors[speech_type], label=speech_type)

ax1.set_xlabel('Training Iteration')
ax1.set_ylabel('Average Score (0-10)')
ax1.set_title('Score Progression by Speech Type')
ax1.set_xlim(0.5, 12.5)
ax1.set_ylim(3, 9)
ax1.legend(loc='lower right', ncol=2)
ax1.set_xticks(range(1, 13))

# Add annotations for key observations
ax1.annotate('NEG speeches\nconsistently higher',
             xy=(8, 8), fontsize=8, color='#c0392b',
             ha='center')
ax1.annotate('AFF rebuttals\nlag behind',
             xy=(8, 5.2), fontsize=8, color='#27ae60',
             ha='center')

# ============== RIGHT PANEL: By Rubric Dimension ==============
ax2 = axes[1]

# Average across speech types for each dimension and iteration
dim_avg = df.groupby(['iteration', 'rubric_dimension'])['avg_score'].mean().reset_index()

dim_labels = {
    'tactic_execution': 'Tactic Execution',
    'argumentation': 'Argumentation',
    'strategic_impact': 'Strategic Impact',
    'opponent_modeling': 'Opponent Modeling',
}

for dim in ['tactic_execution', 'argumentation', 'strategic_impact', 'opponent_modeling']:
    data = dim_avg[dim_avg['rubric_dimension'] == dim]
    ax2.plot(data['iteration'], data['avg_score'],
             marker='s', markersize=4, linewidth=2,
             color=dim_colors[dim], label=dim_labels[dim])

ax2.set_xlabel('Training Iteration')
ax2.set_ylabel('Average Score (0-10)')
ax2.set_title('Score Progression by Rubric Dimension')
ax2.set_xlim(0.5, 12.5)
ax2.set_ylim(5.5, 8)
ax2.legend(loc='lower right')
ax2.set_xticks(range(1, 13))

# Add shaded region for improvement
iter1_avg = dim_avg[dim_avg['iteration'] == 1]['avg_score'].mean()
iter12_avg = dim_avg[dim_avg['iteration'] == 12]['avg_score'].mean()
improvement = ((iter12_avg - iter1_avg) / iter1_avg) * 100

ax2.text(6.5, 7.7, f'+{improvement:.0f}% avg improvement',
         fontsize=10, ha='center',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('/home/ubuntu/debaterhub-monorepo/paper/figures/rubric_progression.pdf',
            bbox_inches='tight', dpi=300)
plt.savefig('/home/ubuntu/debaterhub-monorepo/paper/figures/rubric_progression.png',
            bbox_inches='tight', dpi=300)
print("Saved rubric_progression.pdf and rubric_progression.png")

# Also create a summary table
print("\n=== Summary Statistics ===")
print("\nBy Speech Type (Iter 1 → Iter 11):")
for speech in ['AC', 'NC', '1AR', '1NR', '2AR', '2NR']:
    iter1 = speech_avg[(speech_avg['speech_type'] == speech) & (speech_avg['iteration'] == 1)]['avg_score'].values
    iter11 = speech_avg[(speech_avg['speech_type'] == speech) & (speech_avg['iteration'] == 11)]['avg_score'].values
    if len(iter1) > 0 and len(iter11) > 0:
        print(f"  {speech}: {iter1[0]:.2f} → {iter11[0]:.2f} ({((iter11[0]-iter1[0])/iter1[0]*100):+.1f}%)")

print("\nBy Dimension (Iter 1 → Iter 11):")
for dim in ['tactic_execution', 'argumentation', 'strategic_impact', 'opponent_modeling']:
    iter1 = dim_avg[(dim_avg['rubric_dimension'] == dim) & (dim_avg['iteration'] == 1)]['avg_score'].values
    iter11 = dim_avg[(dim_avg['rubric_dimension'] == dim) & (dim_avg['iteration'] == 11)]['avg_score'].values
    if len(iter1) > 0 and len(iter11) > 0:
        print(f"  {dim_labels[dim]}: {iter1[0]:.2f} → {iter11[0]:.2f} ({((iter11[0]-iter1[0])/iter1[0]*100):+.1f}%)")
