import streamlit as st
from streamlit_ketcher import st_ketcher
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski
import joblib
import pandas as pd
import numpy as np
#to run: python -m streamlit run molecular_descriptors.py
st.set_page_config(layout="wide")
st.title("🧪 Interactive Molecular Descriptor Calculator")

# 1. Embed the drawing interface
st.subheader("Draw your molecule below:")
# The widget returns the SMILES string whenever the user modifies the drawing
smiles = st_ketcher() 

# 2. Process the structure dynamically with RDKit
if smiles:
    st.subheader("Calculated Properties")
    
    # Check if the SMILES string is valid
    mol = Chem.MolFromSmiles(smiles)
    if mol is not None:
         # Calculate properties using the functions from the first response
        mol_weight = Descriptors.MolWt(mol)
        mol_logp = Descriptors.MolLogP(mol)
        rotatable_bonds = Lipinski.NumRotatableBonds(mol)        
        heavy_atom_count = Lipinski.HeavyAtomCount(mol)
        
        aromatic_atoms = len([atom for atom in mol.GetAtoms() if atom.GetIsAromatic()])
        aromatic_proportion = (aromatic_atoms / heavy_atom_count) if heavy_atom_count > 0 else 0.0
        H_Acceptors = Lipinski.NumHAcceptors(mol)
        H_Donors = Lipinski.NumHDonors(mol)
        Nitrogen_Oxygen = Lipinski.NOCount(mol)


        
        # Display results in structured columns
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Molecular Weight", f"{mol_weight:.2f} g/mol")
        col2.metric("Rotatable Bonds", rotatable_bonds)
        col3.metric("Aromatic Proportion", f"{aromatic_proportion * 100:.1f}%")
        col4.metric("logP", f"{mol_logp:.1f}")

        

        st.info(f"**Generated SMILES:** `{smiles}`")

        pipeline = joblib.load("solubilityML_grid_search_4")
        
        mol_params = pd.DataFrame([[rotatable_bonds, H_Acceptors, H_Donors, Nitrogen_Oxygen, mol_weight, mol_logp, aromatic_proportion]], columns=['num_Rotatable_Bonds','num_H_Bond_Acceptors',  'num_H_Bond_Doners', 'num_Nitrogen_Oxygen', 'mol_weight', 'LogP', 'aromatic proportion'])
       # x_pred = np.array(mol_params).reshape(1,-1)
        solubility_prediction = pipeline.predict(mol_params)
        col5.metric("Predicted logS", f"{solubility_prediction[0]}")
        col6.metric("Predicted water solubility (moldm^3)", f"{pow(10,solubility_prediction[0])}")
        col6.metric("Predicted water solubility (gdm^3)", f"{pow(10,solubility_prediction[0])*mol_weight}")

        print (mol_params)
        mol_params





    else:
        st.error("The drawn structure is not completely recognized yet. Keep drawing!")



