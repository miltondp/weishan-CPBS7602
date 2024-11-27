import os
import pandas as pd 
import numpy as np
from scipy import stats

data_path = os.path.join('.', 'data')
os.makedirs(data_path, exist_ok=True)
chunksize=1e6
gtex_v8_tpm_url = 'https://storage.googleapis.com/adult-gtex/bulk-gex/v8/rna-seq/GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_tpm.gct.gz'
df = pd.read_csv(gtex_v8_tpm_url, chunksize=1000, delimiter='\t', skiprows=2, compression='gzip')
gene_mad_df = pd.DataFrame()
i = 1
for chunk in df:
    mads = stats.median_abs_deviation(chunk.iloc[:,2:].values, axis=1)
    ids = chunk.loc[:,'Name'].values
    chunk.to_pickle(os.path.join(data_path, f'gtex_v8_tpm_{i}.pkl'))
    chunk_stats = pd.DataFrame(
        {
            'gene_id': ids,
            'mad': mads
        }
    )
    gene_mad_df = pd.concat(
        [gene_mad_df, chunk_stats]
    )    
    i += 1

gene_mad_df.to_csv(
    os.path.join(data_path, 'gene_mad.csv')
)