# FICO Segmentation Report — Draft Skeleton

## Executive Summary
- The customer base splits into 3 risk tiers; the top tier drives 60% of defaults. [VERIFY]: tier share figures
- Lifting the mid-tier by 50 points reduces expected loss by ~$1.2M annually. [VERIFY]: loss reduction estimate

## Data & Method
- Dataset: 150k records, 23 features, Jan 2024 - Dec 2025. [VERIFY]: record count and date range
- K-means clustering on PCA-transformed features, k selected via silhouette. [VERIFY]: silhouette score >= 0.5
- [VERIFY]: no data leakage between train and validation windows

## Results
- Cluster 0 (low risk): 45% of customers. [VERIFY]: cluster proportions
- Cluster 1 (mid risk): 38%. [VERIFY]
- Cluster 2 (high risk): 17%, Gini 0.71. [VERIFY]: Gini coefficient

## Recommendations
- Tighten credit limits for Cluster 2. [VERIFY]: limit reduction scenario modelled
- [VERIFY]: impact on approval rate < 8%
