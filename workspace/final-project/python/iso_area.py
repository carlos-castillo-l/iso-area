from accelergy.utils import create_folder
import os
import random
import ruamel.yaml

def num_PE_generator(meshX, min_PE, max_PE):
  return random.randint(min_PE/meshX, max_PE/meshX) * meshX

def yaml_generator(in_file, out_file, num_PEs, buffer_parameters):
   """
   Returns name of the new modified file.
   """
   config, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(open(in_file))
   # Update the number of PEs in the architecture
   config['architecture']['subtree'][0]['subtree'][0]['subtree'][0]['name'] = 'PE[0..' + str(num_PEs) + ']'
   # Update the global buffer attributes
   shared_glb = config['architecture']['subtree'][0]['subtree'][0]['local'][0]
   shared_glb_attr = shared_glb['attributes']
   for key, val in buffer_parameters.items():
      shared_glb_attr[key] = val

   # Overwrite output file
   if os.path.exists(out_file):
        os.remove(out_file)
   create_folder(os.path.dirname(out_file))

   yaml = ruamel.yaml.YAML()
   yaml.indent(mapping=2, sequence=4, offset=2) 
   with open(out_file, 'a', encoding='utf8') as fp:
      yaml.dump(config, fp)
