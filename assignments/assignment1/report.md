# **Analysis Report: GTEx Data Unsupervisied Clustering Analysis**

## **What is GTEx?**

The Genotype-Tissue Expression (GTEx) project aims to provide a public resource for the study of human gene expression/genetic variation across tissue and individual. The project involves a densely genotyping a small number of individuals and generating high-throughput molecular data including RNA-seq and eQTLs.  

## **Data**

For this analysis, we utilized a subset of the public GTEx v8 RNA-seq dataset subsetted to include the tissue types with the top 10 largest sample size. The data includes:
- **Features**: A gene expression matrix with 12,385 samples across top 5,000 genes by Median Average Deviation, representing normalized RNA-seq data.
- **Target**: Metadata containing tissue labels (e.g., Adipose Tissue, Blood Vessel, Heart), which served as ground truth for clustering and evaluation.
- **Feature id Annotations**: Gene ID-to-symbol mapping for improved readability of visualization.

Data preprocessing included standard z-score scaling of features to ensure comparability and the removal of features with missing or constant values.

## **Cluster Analysis**
The following unsupervised clustering functions from sci-kit learn were used:

- **KMeans**
- **AgglomerativeClustering**

to cluster the GTEx RNA-seq data into 5-14 clusters. 

For the KMeans clustering, additional 5 replications per cluster number is enforced to assess cluster stability. 

Both clustering methods were evaluated with the following sci-kit learn metrics:

- **adjusted_rand_score** (ARI) against ground truth tissue label
- **normalized_mutual_info_score** (NMI) against ground truth tissue label
- **silhouette_score** (Silhouette) against the scaled RNA-seq space
- **calinski_harabasz_score** (CH) against the scaled RNA-seq space

## **Cluster Results**

The external evaluation metrics (ARI and NMI) were consistently and positively correlated with the number of clusters in Kmeans clustering all the way from 5 clusters to 14 clusters. The Silhouette score likewise was consistently and positive correalted with the number of clusters in Kmeans, whereas the CH score decrased with increased cluster numbers but had a local peak at 10 clusters.

The external evaluation metrics suggested a local optimal cluster number of 7 for the agglomerative clustering (hierarchical clustering) method, whereas the Silhouette suggested a optimal cluster number of 12. The CH score did not indicate a meaningful optimal number of cluster as it consistently decreased with increasing cluster number. 

It appears that KMeans offered relatively better clustering by the fact that the optimal cluster number matched that of the ground truth data (of 10 tissues). But upon visually inspecting the optimal clustering result on a UMAP space both methods seemed to perform poorly in similar ways, with both method failed to separate adipose tissue from lung while clustered brain tissue into >=3 different clusters. 

## **Feature Importance Interpretation**

The important features driving both clustering methods were identified by applying a decision tree classifier of max depth of 3 on the predicted results. 

It seemed like the most important genes driving KMeans clustering were SNHG17 which results in good separation blood vessel and esophagus from the rest of the tissue and FAM189B subsequently separates esophagus and blood vessel. HDGF drives teh clustering of muscle and skin from the rest and LYNX1 subsequently drives the separation of muscle from skin. 

For the agglomerative clustering method, the important driver genes were RPS8 whic separates heart and blood vessel from the rest and subsequently RRP9 which separates heart from blood vessel. The gene PTP4A3 is important for separating adiposte tissue from the rest, and subsequently the gene RPA1 helps separate esophagus from adiposte tissue.  

Running decision tree classifier (max depth=5) against the ground truth label allowed the identification of genes driving tissue classification themselves. 
- Muscle tissue seemed to be marked by the expression of ALDH16A1. 
- Adiposte tissue seemed to be marked by the expression of PHPT1 and lack of expression of USP21 and expression of XBP1 and lack of expression of MRFAP1L1. 
- Blood vessel is marked by the expression of RPS8.
- Esophagus is marked by the expression of MMP14 and lack of expression of MED15.

The first 5 layer of the tree classifier seemed to be unable to effectively tease out the other 6 tissues. 
