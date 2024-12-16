import os
import gc
import pandas as pd
import numpy as np
from scipy import stats

# Download GTEx v8 metadata
gtex_v8_metadata_url = 'https://storage.googleapis.com/adult-gtex/annotations/v8/metadata-files/GTEx_Analysis_v8_Annotations_SampleAttributesDS.txt'
gtex_v8_metadata = pd.read_csv(
    gtex_v8_metadata_url,
    delimiter='\t',
    header=0
)

selection = 'abundant'

if selection == 'abundant':
  # Select by most abundant tissue
  n = 10
  top_tissues = gtex_v8_metadata.groupby(['SMTS']).size().reset_index(name='counts').sort_values('counts', ascending=False).head(n).loc[:,'SMTS'].values
  gtex_v8_metadata_subset = gtex_v8_metadata.loc[gtex_v8_metadata['SMTS'].isin(top_tissues),:]
elif selection == 'blood_brain':
  # Select tissue specific samples
  tissues = ['Brain', 'Blood']
  gtex_v8_metadata_subset = gtex_v8_metadata.loc[
      gtex_v8_metadata['SMTS'].isin(tissues),
      :]
else:
    raise ValueError('Invalid selection')

sample_ids = gtex_v8_metadata_subset['SAMPID'].values
gtex_v8_metadata_subset.set_index('SAMPID', inplace=True)

gtex_v8_phenotype_url = "https://storage.googleapis.com/adult-gtex/annotations/v8/metadata-files/GTEx_Analysis_v8_Annotations_SubjectPhenotypesDS.txt"
gtex_v8_phenotype = pd.read_csv(
    gtex_v8_phenotype_url,
    delimiter='\t',
    header=0
)

gtex_v8_phenotype_url = "https://storage.googleapis.com/adult-gtex/annotations/v8/metadata-files/GTEx_Analysis_v8_Annotations_SubjectPhenotypesDS.txt"
gtex_v8_phenotype = pd.read_csv(
    gtex_v8_phenotype_url,
    delimiter='\t',
    header=0
)
gtex_v8_phenotype.head()
gtex_v8_metadata_subset['SUBJID'] = gtex_v8_metadata_subset.index.str.split('-').str[:2].str.join('-')
gtex_v8_target = pd.merge(gtex_v8_metadata_subset, gtex_v8_phenotype, on='SUBJID', how='left')
gtex_v8_target.index = gtex_v8_metadata_subset.index

gtex_v8_target.to_csv(os.path.join('.', 'gtex_v8_target.csv'), index=True)


# Download GTEx v8 TPM data
data_path = os.path.join('.', 'data')
os.makedirs(data_path, exist_ok=True)
chunksize=1e3
gtex_v8_tpm_url = 'https://storage.googleapis.com/adult-gtex/bulk-gex/v8/rna-seq/GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_tpm.gct.gz'
df = pd.read_csv(gtex_v8_tpm_url, chunksize=chunksize, delimiter='\t', skiprows=2, compression='gzip')
gene_mad_df = pd.DataFrame()
i = 1
for chunk in df:

    chunk_id = list(chunk.iloc[:,2:].columns)
    chunk_id = [x for x in chunk_id if x in gtex_v8_metadata_subset.index]

    if len(chunk_id) == 0:
      continue

    chunk = chunk.loc[:, ['Name', 'Description'] + chunk_id]

    mads = stats.median_abs_deviation(chunk.iloc[:,2:].values, axis=1)
    vars = np.var(chunk.iloc[:,2:].values, axis=1)

    ids = chunk.loc[:,'Name'].values
    chunk.to_pickle(os.path.join(data_path, f'gtex_v8_tpm_{i}.pkl'))
    chunk_stats = pd.DataFrame(
        {
            'gene_id': ids,
            'mad': mads,
            'var': vars
        }
    )
    gene_mad_df = pd.concat(
        [gene_mad_df, chunk_stats]
    )
    i += 1

gene_stats_df = pd.read_csv(
    os.path.join(data_path, 'gene_stats.csv')
)
top_n = 5000
gene_ids = gene_stats_df.sort_values('mad', ascending=False).head(top_n).loc[:,'gene_id'].values

files = os.listdir(data_path)
pkl_files = [file for file in files if file.endswith('.pkl')]
dfs = []
id_to_symbol_mapping = pd.DataFrame()
for pkl_file in pkl_files:
    chunk_df = pd.read_pickle(os.path.join(data_path, pkl_file))
    chunk_df = chunk_df.set_index('Name')
    desc = chunk_df.pop('Description').reset_index().set_index('Name').rename(columns={'Description': 'Symbol'})
    id_to_symbol_mapping = pd.concat([id_to_symbol_mapping, desc])
    chunk_df_filter = chunk_df.loc[
        chunk_df.index.isin(gene_ids),
        chunk_df.columns.isin(sample_ids)
        ]
    dfs.append(chunk_df_filter)

gtex_v8_tpm = pd.concat(dfs)
print(f'Number of genes: {gtex_v8_tpm.shape[0]}')
print(f'Number of samples: {gtex_v8_tpm.shape[1]}')
del dfs
gc.collect()
id_to_symbol_mapping = id_to_symbol_mapping.loc[gene_ids,:]

id_to_symbol_mapping.to_csv(os.path.join('.', 'gtex_v8_gene_id_to_symbol.csv'))
gtex_v8_tpm.to_csv(os.path.join('.', 'gtex_v8_features.csv'))