# Read in the ModelSEED database and generate a COBRA model (JSON format) with
# all the reactions and metabolites in the database. The model is then saved
# as a JSON file.

import json
import cobra

# Read in the ModelSEED databases
with open('../ModelSEEDDatabase/biochemistry/reactions.json') as f:
    modelseed_reactions = json.load(f)
with open('../ModelSEEDDatabase/biochemistry/compounds.json') as f:
    modelseed_compounds = json.load(f)

# Create a new COBRA model
model = cobra.Model('ModelSEED_Universal_Model')

# Add compartments to the model
# FIXME: This doesn't work- I'm not sure I can set the compartments directly
model.compartments = {'c0': 'cytosol', 'e0': 'extracellular'}

# Add all the metabolites to the model
for compound in modelseed_compounds:
    # Add an internal metabolite (i.e. ending with '_c0')
    model.add_metabolites(cobra.Metabolite(compound['id'] + '_c0',
                                           name=compound['name'],
                                           compartment='c0',
                                           formula=compound['formula'],
                                           charge=compound['charge'],
                                           # TODO: Add annotation with aliases
                                           ))
    # Add an external metabolite (i.e. ending with '_e0')
    model.add_metabolites(cobra.Metabolite(compound['id'] + '_e0',
                                           name=compound['name'],
                                           compartment='e0',
                                           formula=compound['formula'],
                                           charge=compound['charge'],
                                           # TODO: Add annotation with aliases
                                           ))
    # Add an exchange reaction for the external metabolite
    exchange_reaction = cobra.Reaction('EX_' + compound['id'] + '_e0')

# Add all the reactions to the model
for reaction in modelseed_reactions:
    # Create a new reaction
    new_reaction = cobra.Reaction(reaction['id'])
    new_reaction.name = reaction['name']
    new_reaction.lower_bound = reaction['minFlux']
    new_reaction.upper_bound = reaction['maxFlux']

    # Add all the metabolites to the reaction
    for metabolite in reaction['stoichiometry']:
        # Check if the metabolite already exists in the model
        new_reaction.add_metabolites({metabolite['compound_ref']:
                                      metabolite['coefficient']})

    # Add the reaction to the model
    model.add_reaction(new_reaction)

# Save the model as a JSON file
cobra.io.save_json_model(model, "universal_model/modelseed_universal_model.json")
