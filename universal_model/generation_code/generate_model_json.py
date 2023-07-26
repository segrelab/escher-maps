# Read in the ModelSEED database and generate a COBRA model (JSON format) with
# all the reactions and metabolites in the database. The model is then saved
# as a JSON file. Takes forever to run, but hopefully you don't need to run it.

import json
import cobra
import warnings

# Read in the ModelSEED databases
with open('../ModelSEEDDatabase/biochemistry/reactions.json') as f:
    modelseed_reactions = json.load(f)
with open('../ModelSEEDDatabase/biochemistry/compounds.json') as f:
    modelseed_compounds = json.load(f)

# TODO: Filter out reactions based on the templates

# Create a new COBRA model
model = cobra.Model('ModelSEED_Universal_Model')

def stoich_string_to_dict(stoich_string):
    # Convert a ModelSEED stoichiometry string to a dictionary of metabolites
    # and stoichiometric coefficients for the COBRA Reaction object 'metabolites'
    # attribute
    stoich_dict = {}
    # Split the stoichiometry string into individual metabolites
    stoich_list = stoich_string.split(';')
    # Iterate through each metabolite in the list
    for metabolite in stoich_list:
        # Split the metabolite into the coefficient and the metabolite ID
        metabolite_split = metabolite.split(':')
        # Check that there is enough information to add the metabolite
        if len(metabolite_split) < 3:
N            raise ValueError('Reaction does not have enough information to be added to the model')
        # Get the compartment ID fromt the third, 0 is c0, 1 is e0
        compartment_code = metabolite_split[2]
        compartment_id = 'c0' if compartment_code == '0' else 'e0'
        # Add the metabolite to the dictionary
        stoich_dict[metabolite_split[1] + '_' + compartment_id] = float(metabolite_split[0])
    return stoich_dict

# Add all the metabolites to the model
for compound in modelseed_compounds:
    # Skip the metabolite if it is obsolete
    if compound['is_obsolete']:
        continue
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
    exchange_reaction = {'id': 'EX_' + compound['id'] + '_e0',
                        'name': 'Exchange reaction for ' + compound['name'],
                        'metabolites': {compound['id'] + '_e0': -1}}
    model.add_reaction(cobra.io.dict._reaction_from_dict(exchange_reaction, model))

# Add all the reactions to the model
for reaction in modelseed_reactions:
    # If the reaction is obsolete, skip it
    if reaction['is_obsolete']:
        continue
    # Parse the stoichiometry string into a dictionary of metabolites
    try:
        rxn_metabolites = stoich_string_to_dict(reaction['stoichiometry'])
    except ValueError:
        # If the stoichiometry string doesn't have the information to make a
        # reaction, skip it
        warnings.warn('Reaction ' + reaction['id'] + ' does not have enough information to be added to the model')
        continue
    # Create a new reaction dictionary
    new_reaction = {'id': reaction['id'],
                    'name': reaction['name'],
                    # TODO: Add the aliases as annotations,
                    'metabolites': rxn_metabolites}
    # Add reaction to model
    model.add_reaction(cobra.io.dict._reaction_from_dict(new_reaction, model))

# Save the model as a JSON file
cobra.io.save_json_model(model, "universal_model/modelseed_universal_model.json")
