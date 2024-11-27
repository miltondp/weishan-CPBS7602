import os
import gc
import pandas as pd 

# Read gene MAD data 
print("Loading gene MAD data")
data_path = os.path.join('.', 'data')
if os.path.exists(os.path.join(data_path, 'gene_mad.csv')):
    gene_mad_df = pd.read_csv(
        os.path.join(data_path, 'gene_mad.csv')
    )
    top_n = 5000
    gene_ids = gene_mad_df.sort_values('mad', ascending=False).head(top_n).loc[:,'gene_id'].values
else:
    print("Gene MAD data not found. Please run gtex_gene_mad.py first.")
    exit()

# load gtex metadata for sample selection 
print("Loading GTEx metadata file")
gtex_v8_metadata_url = 'https://storage.googleapis.com/adult-gtex/annotations/v8/metadata-files/GTEx_Analysis_v8_Annotations_SampleAttributesDS.txt'
gtex_v8_metadata = pd.read_csv(
    gtex_v8_metadata_url,
    delimiter='\t',
    header=0
)

# Identify top 10 tissues with most samples
top_tissues = gtex_v8_metadata.groupby(['SMTS']).size().reset_index(name='counts').sort_values('counts', ascending=False).head(10).loc[:,'SMTS'].values
sample_ids = gtex_v8_metadata.loc[gtex_v8_metadata['SMTS'].isin(top_tissues),'SAMPID'].values
print(f'Number of samples past selection: {len(sample_ids)}')
gtex_v8_metadata.set_index('SAMPID', inplace=True)
gtex_v8_metadata = gtex_v8_metadata.loc[sample_ids,['SMTS']]
# export metadata
gtex_v8_metadata.to_csv(os.path.join(data_path, 'gtex_v8_target.csv'))

# Load gene expression data
print("Loading gene expression data")
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
# export gene id to symbol mapping
id_to_symbol_mapping.to_csv(os.path.join(data_path, 'gtex_v8_gene_id_to_symbol.csv'))

# export subsetted and filtered gene expression data
gtex_v8_tpm.to_csv(os.path.join(data_path, 'gtex_v8_features.csv'))

