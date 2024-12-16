# **Analysis Report: Comparison of ensemble approaches**
This report summarizes the findings from applying dimensionality reduction and ensemble-based machine learning techniques to the GTEx gene expression dataset. The primary goals were to evaluate the impact of different dimensionality reduction methods on clustering and prediction, and to assess the performance of ensemble models for predicting tissue type and age.

## **Data**

For this analysis, we utilized a subset of the public GTEx v8 RNA-seq dataset subsetted to include the tissue types with the top 10 largest sample size. The data includes:
- **Features**: A gene expression matrix with 12,385 samples across top 5,000 genes by Median Average Deviation, representing normalized RNA-seq data.
- **Target**: Metadata containing sample specific tissue labels (e.g., Adipose Tissue, Blood Vessel, Heart), which served as ground truth for clustering and evaluation as well as subject specific categorical age information.
- **Feature id Annotations**: Gene ID-to-symbol mapping for improved readability of visualization.

Data preprocessing included standard min-max scaling of features to ensure comparability and the removal of features with missing or constant values.

### 1. Dimensionality Reduction and Clustering

#### **UMAP (Uniform Manifold Approximation and Projection)**: 

UMAP was used to reduce the dimensionality of the RNA-expression feature matrix that includes the top 5000 variable genes measured by median absolute deviation with 2 components, with parameters tuned to explore different latent spaces. 
Specifically, the parameter 'n\_neighbors' and 'learning\_rate' were tuned over a small range of values and the optimal projection is determined as the one that offers the optimal silhouette score with respect to the group truth tissue label (and reflect the degree to which the tissues are well separated). 

#### Results:
The optimal paramter for UMAP is determined to be 'n\_neighbors'=30 and 'learning\_rate'=0.1, which yields a average silhouette score of 0.498. Visually the clusters are well separated in the givne UMAP 2d space. 

#### **PCA (Principal Component Analsyis)**:
 Principal component analysis is also performed on the same feature matrix as a reference dimensionality reduction strategy. For the fairness of comparison, all later analysis were conducted on the first 2 PCs to match the 2 components of the UMAP projection. 

---

### 2. Ensemble-based Models to Predict Tissue of Origin

#### Models Used:
- **Random Forest Classifier (RF)**: Here serves as the ensemble technique with leanerr that tends to overfit individually 
- **HistGradientBoostingClassifier (GradientBoosting)**: Here serves as the ensemble technique that makes use of weak learners

#### Training Setup:
- Training and test data of dimensionality reduced dataset (PCA and UMAP) split was done with 5 fold cross validation and randomly shuffled to ensure equal representation of each tissue type in dataset. 
- Hyperparameter tuning was conducted using grid search for both classifiers, for random forest the parameters 'n\_estimators' and 'max\_depth' were tuned and for gradient boosting the parameters 'n\_estimators' and 'learning\_rate' were tuned.
- The models were evaluated using ‘classification\_report’ from sklearn to calculate precision, recall, f1-score, and accuracy for each tissue class.
- For the purpose of hyper-parameter tuning, the over-all balanced accuracy score serves as the selection criteria. 

#### Results:

| Ensembl Model | Best Balanced Accuracy from PCA | Best Balanced Accuracy from UMAP | Parameter Combination |
|----------|----------|----------|----------|
| **Random Forest Classifier**    | 0.620  | 0.981  | 'n\_estimators'=50 and 'max\_depth'=10 |
| **HistGradientBoostingClassifier**    | 0.621 | 0.981 | 'n\_estimators'=50 and 'learning\_rate'=0.05 |


**Class specific Predictions Accuracy on the optimal model##
1. **Random Forest Classifier**:
   - The worst class to be predicted is Blood Vessel and Colon, with recalls of 0.95 and 0.96 respectively. Every other tissue had a f1-score of at least 0.99

2. **HistGradientBoostingClassifier**:
   - The worst class to be predicted is Colon, with recalls of 0.95 and 0.96 respectively. Every other tissue had a f1-score of at least 0.99

---

### 3. Ensemble-based Models to Predict Age

#### Models Used:
- **Random Forest Classifier (RF)**: Again serves as the ensemble technique with leanerr that tends to overfit individually 
- **HistGradientBoostingClassifier (GradientBoosting)**: Again serves as the ensemble technique that makes use of weak learners

#### Training Setup:
- Training and test data of dimensionality reduced dataset (PCA and UMAP) subseetted to only contain the blood samples split was done with 5 fold cross validation and randomly shuffled to ensure equal representation of each tissue type in dataset. 
- Due to the non-availablitity of continuous measurement of age, the mean of the two limits of the binned age that was available were used as the continuous measurement to be predicted. 
- Hyperparameter tuning was conducted using grid search for both classifiers, for random forest the parameters 'n\_estimators' and 'max\_depth' were tuned and for gradient boosting the parameters 'n\_estimators' and 'learning\_rate' were tuned.
- The models were evaluated using ‘classification\_report’ from sklearn to calculate precision, recall, f1-score, and accuracy for each tissue class.
- For the purpose of hyper-parameter tuning, the mean MSE serves as the selection criteria. 

#### Results:

| Ensembl Model | Best MSE from PCA | Best MSE from UMAP | Parameter Combination |
|----------|----------|----------|----------|
| **Random Forest Classifier**    | 231.6  | 201.4  | 'n\_estimators'=100 and 'max\_depth'=10 |
| **HistGradientBoostingClassifier**    | 192.3 | 0177.5 | 'max\_iter'=50 and 'learning\_rate'=0.05 |

- Both RF and HGB struggled to predict age accurately. With large mean square error of more than 190. 
- Upon plotting the scatter plot of real test value and predicted value, the random forest predction appeared like random noise whereas gradient boosting just estimated everybody to be between age of 40 to 60. 

---

### Conclusions
1. **Dimensionality Reduction**:
   - UMAP successfully created meaningful latent spaces that grouped tissues visually and predction regression tasks following from UMAP all outperformed the ones following from PCA with the same number of 2 components. 

2. **Ensemble-based Tissue Prediction**:
   - Random Forest showed signs of overfitting but performed reasonably well for tissues with high representation.
   - HistGradientBoosting was more robust across tissues, and achieves the same overall performance as random forest. 

3. **Ensemble-based Age Prediction**:
   - Both models struggled predciting age. RF would predict like noise whereas HGB predicted like noise with smaller variance. 