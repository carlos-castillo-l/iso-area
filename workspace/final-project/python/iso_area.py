import random
import yaml

def num_PE_generator(meshX, min_PE, max_PE):
  return random.randint(min_PE/meshX, max_PE/meshX) * meshX

def yaml_generator(filename, output_filename, num_PEs, buffer_parameters):
   with open(filename, 'r') as file:
      data = yaml.safe_load(file)
   
   # Update the number of PEs in the architecture
   data['architecture']['subtree'][0]['subtree'][0]['subtree'][0]['name'] = 'PE[0..' + str(num_PEs) + ']'

   # Update the number global buffer
   shared_glb = data['architecture']['subtree'][0]['subtree'][0]['local'][0]
   shared_glb_attr = shared_glb['attributes']

   for key, val in buffer_parameters.items():
      shared_glb_attr[key] = val

   with open(output_filename + '.yaml', 'w', encoding='utf8') as file:
      yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
      