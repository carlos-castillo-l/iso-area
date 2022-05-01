# Copyright (c) 2019 Yannan Wu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from accelergy.raw_inputs_2_dicts import RawInputs2Dicts
from accelergy.system_state import SystemState
from accelergy.component_class import ComponentClass
from accelergy.arch_dict_2_obj import arch_dict_2_obj
from accelergy.plug_in_path_to_obj import plug_in_path_to_obj
from accelergy.action_counts_dict_2_obj import action_counts_dict_2_obj
from accelergy.primitive_component import PrimitiveComponent
from accelergy.compound_component import CompoundComponent
from accelergy.ERT_generator import EnergyReferenceTableGenerator, ERT_dict_to_obj
from accelergy.ART_generator import AreaReferenceTableGenerator
from accelergy.energy_calculator import EnergyCalculator
from accelergy.io import generate_output_files
from accelergy.utils import *

import sys
import math
import random
from collections import OrderedDict

def parse_inputs(args, system_state):
    accelergy_version = 0.3

    # ----- Interpret Commandline Arguments
    output_prefix = args.oprefix
    path_arglist = args.files
    precision = args.precision
    desired_output_files = args.output_files

    # interpret desired output files
    oflags = {'ERT': 0, 'ERT_summary': 0, 'ART': 0, 'ART_summary': 0,
              'energy_estimation': 0, 'flattened_arch': 0}
    for key, val in oflags.items():
        if 'all' in desired_output_files or key in desired_output_files: oflags[key] = 1

    INFO("generating outputs according to the following specified output flags... \n "
         "Please use the -f flag to update the preference (default to all output files)")
    print(oflags)

    oflags['output_prefix'] = output_prefix
    # interpret the types of processing that need to be performed
    flatten_architecture = 1 if oflags['flattened_arch'] else 0
    compute_ERT = 1 if oflags['ERT'] or oflags['ERT_summary'] or oflags['energy_estimation'] else 0
    compute_energy_estimate = 1 if oflags['energy_estimation'] else 0
    compute_ART = 1 if oflags['ART'] or oflags['ART_summary'] else 0

    # ----- Global Storage of System Info
    system_state.set_accelergy_version(accelergy_version)
    # transport the input flag information to system state
    system_state.set_flag_s({'output_path': args.outdir,
                             'verbose': args.verbose})
    system_state.set_flag_s(oflags)

    # ----- Load Raw Inputs to Parse into Dicts
    raw_input_info = {'path_arglist': path_arglist, 'parser_version': accelergy_version}
    raw_dicts = RawInputs2Dicts(raw_input_info)

    # ----- Determine what operations should be performed
    available_inputs = raw_dicts.get_available_inputs() # e.g. ['architecture_spec', 'compound_component_classes']

    # ---- Detecting config only cases and gracefully exiting
    if len(available_inputs) == 0:
        INFO("no input is provided, exiting...")
        sys.exit(0)

    if flatten_architecture or (compute_ERT and 'ERT' not in available_inputs) or compute_ART:
        # architecture needs to be defined if
        #    (1) flattened architecture required output,
        #    (2) ERT needed but bot provided,
        #    (3) ART needed

        # ----- Add the Component Classes
        for pc_name, pc_info in raw_dicts.get_pc_classses().items():
            system_state.add_pc_class(ComponentClass(pc_info))
        for cc_name, cc_info in raw_dicts.get_cc_classses().items():
            system_state.add_cc_class(ComponentClass(cc_info))

        # ----- Set Architecture Spec (all attributes defined)
        arch_obj = arch_dict_2_obj(raw_dicts.get_flatten_arch_spec_dict(), system_state.cc_classes, system_state.pc_classes)
        system_state.set_arch_spec(arch_obj)

    if (compute_ERT and 'ERT' not in available_inputs) or compute_ART:
        # ERT/ERT_summary/energy estimates/ART/ART summary need to be generated without provided ERT
        #        ----> all components need to be defined
        # ----- Add the Fully Defined Components (all flattened out)

        for arch_component in system_state.arch_spec:
            if arch_component.get_class_name() in system_state.pc_classes:
                class_name = arch_component.get_class_name()
                pc = PrimitiveComponent({'component': arch_component, 'pc_class': system_state.pc_classes[class_name]})
                system_state.add_pc(pc)
            elif arch_component.get_class_name() in system_state.cc_classes:
                cc = CompoundComponent({'component': arch_component, 'pc_classes':system_state.pc_classes, 'cc_classes':system_state.cc_classes})
                system_state.add_cc(cc)
            else:
                ERROR_CLEAN_EXIT('Cannot find class name %s specified in architecture'%arch_component.get_class())

        # ----- Add all available plug-ins
        system_state.add_plug_ins(plug_in_path_to_obj(raw_dicts.get_estimation_plug_in_paths(), output_prefix))

    return raw_dicts, precision, compute_ERT, compute_energy_estimate, compute_ART

def compute_accelergy_estimates(system_state, raw_dicts, precision, compute_ERT, compute_energy_estimate, compute_ART, iso_area):
    # ----- Determine what operations should be performed
    available_inputs = raw_dicts.get_available_inputs()

    # Only use the provided ERT if we are not running iso-area exploration
    if compute_ERT and 'ERT' in available_inputs and not iso_area:
        # ERT/ ERT_summary/ energy estimates need to be generated with provided ERT
        #      ----> do not need to define components
        # ----- Get the ERT from raw inputs
        ert_dict = raw_dicts.get_ERT_dict()
        system_state.set_ERT(ERT_dict_to_obj({'ERT_dict': ert_dict,
                                              'parser_version': system_state.parser_version,
                                              'precision': precision}))

    if (compute_ERT and 'ERT' not in available_inputs) or iso_area:
            # ----- Generate Energy Reference Table
            ert_gen = EnergyReferenceTableGenerator({'parser_version': system_state.parser_version,
                                                     'pcs': system_state.pcs,
                                                     'ccs': system_state.ccs,
                                                     'plug_ins': system_state.plug_ins,
                                                     'precision': precision})
            system_state.set_ERT(ert_gen.get_ERT())

    if compute_energy_estimate: # if energy estimates need to be generated
        # ----- Generate Energy Estimates
        action_counts_obj = action_counts_dict_2_obj(raw_dicts.get_action_counts_dict())
        system_state.set_action_counts(action_counts_obj)
        energy_calc = EnergyCalculator({'parser_version': system_state.parser_version,
                                        'action_counts': system_state.action_counts,
                                        'ERT': system_state.ERT})
        system_state.set_energy_estimations(energy_calc.energy_estimates)

    if compute_ART: # if ART, ART_summary need to be generated
        # ----- Generate Area Reference Table
        art_gen = AreaReferenceTableGenerator({'parser_version': system_state.parser_version,
                                               'pcs': system_state.pcs,
                                               'ccs': system_state.ccs,
                                               'plug_ins': system_state.plug_ins,
                                               'precision': precision})
        system_state.set_ART(art_gen.get_ART())

def num_PE_generator(min_PE, max_PE):
    meshX = 0
    meshY = 0
    prev_mesh = set()
    repeated = 0
    max_reps = ((max_PE - min_PE)/2)**3
    while True:
        meshX = random.randrange(2, max_PE + 1, 2)
        meshY = random.randrange(math.ceil(min_PE/meshX), math.floor(max_PE/meshX) + 1, 2)
        # Enforce even spatial dimensions for the PEs
        if (meshX,meshY) not in prev_mesh:
            repeated = 0
            prev_mesh.add((meshX,meshY))
            yield meshX*meshY, meshX
        else:
            if repeated == max_reps:
                break
            repeated += 1

def find_buffer_pe_comps(arch_spec, buffer_names, dummy_names):
    # Find buffer and PE components that we are allowed to modify
    buffer_components = {}
    dummy_components = {}
    pe_components = {}
    curr_num_PEs = 0
    for component_name in arch_spec.get_component_name_list():
        relative_comp_name = component_name[:]
        if relative_comp_name in buffer_names:
            buffer_components[component_name] = arch_spec.get_component(component_name)
        
        if relative_comp_name in dummy_names:
            dummy_components[component_name] = arch_spec.get_component(component_name)

        index_PE = relative_comp_name.find("PE")
        if index_PE != -1:
            if curr_num_PEs == 0:
                num_PE_str = relative_comp_name[index_PE+6:]
                j = num_PE_str.find("]")
                curr_num_PEs = int(num_PE_str[:j]) + 1
            pe_components[component_name] = arch_spec.get_component(component_name)
    return buffer_components, dummy_components, pe_components, curr_num_PEs

def change_num_components(string, new_value):
    start = string.find('[')
    end = string.find(']')
    return string[:start + 4] + new_value + string[end:]

def reset_subcomponents(component, cc_classes, pc_classes):
    component._subcomponents = {}
    component.all_possible_subcomponents = {}
    component.subcomponent_base_name_map = {}
    component._actions = []
    # Redefine subcomponents
    component.set_subcomponents(cc_classes, pc_classes)
    component.flatten_action_list(cc_classes)

def modify_PEs(system_state, pe_components, num_PEs, meshX):
    old_to_new = {}
    old_pe_names = pe_components.keys()
    for pe_name in old_pe_names:
        pe_component = pe_components[pe_name]
        # Update the name of the PE component to reflect the number of PEs
        new_pe_name = change_num_components(pe_name, str(num_PEs))
        # Update the name of the PE component
        pe_component.name = new_pe_name
        # Update the spatial dimensions of the PE object
        attributes = pe_component.get_attributes()
        attributes['meshX'] = meshX
        # Update the arch spec of the system_state
        del system_state.arch_spec.component_dict[pe_name]
        system_state.arch_spec.component_dict[new_pe_name] = pe_component # ArchComp Component
        # Update the ccs or pcs of the system_state
        if pe_name in system_state.ccs:
            ccs = system_state.ccs[pe_name]
            ccs.name = new_pe_name
            del system_state.ccs[pe_name]
            system_state.ccs[new_pe_name] = ccs
            old_to_new[pe_name] = new_pe_name, ccs
        if pe_name in system_state.pcs:
            pcs = system_state.pcs[pe_name]
            pcs._name = new_pe_name
            del system_state.pcs[pe_name]
            system_state.pcs[new_pe_name] = pcs
            # Store the old to new name map to update pe dictionary
            old_to_new[pe_name] = new_pe_name, None
    # Update the internal dict for pe_components
    new_pe_components = {}
    for old_name, (new_name, ccs) in old_to_new.items():
        pe_component = pe_components[old_name]
        new_pe_components[new_name] = pe_component
        # Reset the subcomponents of the current component
        if ccs != None:
            reset_subcomponents(ccs, system_state.cc_classes, system_state.pc_classes)
    return new_pe_components

def get_area(art_gen, components):
    art = art_gen.get_ART().get_ART()
    total_area = 0
    for table in art['ART']['tables']:
        component_name = table['name']
        if component_name in components:
            total_area += table['area']
    return total_area

def get_num_components(component_name):
    num_components = 1
    start = component_name.find('[')
    if start != -1:
        num_components = component_name[start + 4: component_name.find(']')]
    return int(num_components)

def find_best_buffer_area(system_state, precision, buffer_components, target_area, resolution=.005):
    # Initialize estimation plugin interface
    buffer_component = buffer_components[next(iter(buffer_components))]
    # Get the memory depth of the buffer
    depth_key = 'memory_depth'
    buffer_attributes = buffer_component.get_attributes()
    for key in buffer_attributes:
        if 'depth' in key:
            depth_key = key
    # ----- Generate Area Reference Table
    art_gen = AreaReferenceTableGenerator({'parser_version': system_state.parser_version,
                                               'pcs': system_state.pcs,
                                               'ccs': system_state.ccs,
                                               'plug_ins': system_state.plug_ins,
                                               'precision': precision})
    area = get_area(art_gen, buffer_components)
    min_mem_depth = 0
    max_mem_depth = float('inf')
    mem_depth = buffer_attributes[depth_key]
    best_area = (mem_depth, abs(target_area - area))
    while area != target_area and mem_depth != 0:
        if area > target_area:
            max_mem_depth = mem_depth
            mem_depth = min_mem_depth + (max_mem_depth - min_mem_depth)/2        
        else:
            min_mem_depth = mem_depth
            if math.isinf(max_mem_depth):
                mem_depth *= 2
            else:
                mem_depth = min_mem_depth + (max_mem_depth - min_mem_depth)/2
        buffer_attributes[depth_key] = int(mem_depth)
        reset_subcomponents(system_state.ccs[buffer_component.get_name()], system_state.cc_classes, system_state.pc_classes)
        # Update the ART generator to reflect changes in memory depth
        art_gen = AreaReferenceTableGenerator({'parser_version': system_state.parser_version,
                                                'pcs': system_state.pcs,
                                                'ccs': system_state.ccs,
                                                'plug_ins': system_state.plug_ins,
                                                'precision': precision})
        area = get_area(art_gen, buffer_components)
        # Find the area difference and keep the best area
        area_diff = abs(target_area - area)
        if area_diff < best_area[1]:
            best_area = (mem_depth, area_diff)
        # Check for termination of the search
        if abs(area - target_area)/target_area < resolution: # Best area within 1% difference from target area
            break
    # Update the memory depth that provided the best area estimate
    buffer_attributes[depth_key] = int(round(best_area[0]/8)*8)
    reset_subcomponents(system_state.ccs[buffer_component.get_name()], system_state.cc_classes, system_state.pc_classes)
    # Update the ART generator to reflect changes in memory depth
    art_gen = AreaReferenceTableGenerator({'parser_version': system_state.parser_version,
                                            'pcs': system_state.pcs,
                                            'ccs': system_state.ccs,
                                            'plug_ins': system_state.plug_ins,
                                            'precision': precision})
    percent_diff = abs(target_area - get_area(art_gen, buffer_components))/target_area
    return percent_diff

def find_iso_area_designs(args, system_state):
    """Buffers names are given to us through the arguments"""
    arch_spec = system_state.arch_spec # Get the current architecture specifications
    init_num_PEs = args.num_PE # Read the number of PEs from the commandline arguments
    buffer_names = args.buffer # Read buffers from the commandline arguments
    dummy_names = args.dummy_buffer # Read dummy buffers from the commandline arguments
    
    buffer_components, dummy_components, pe_components, curr_num_PEs = find_buffer_pe_comps(arch_spec, buffer_names, dummy_names)

    if init_num_PEs == 0:
        init_num_PEs = curr_num_PEs

    # Createa ART generator to compute area estimates
    art_gen = AreaReferenceTableGenerator({'parser_version': system_state.parser_version,
                                               'pcs': system_state.pcs,
                                               'ccs': system_state.ccs,
                                               'plug_ins': system_state.plug_ins,
                                               'precision': args.precision})

    # Get area of the current architecture
    pe_area = get_area(art_gen, pe_components) # Get the area of the PEs
    buffer_area = get_area(art_gen, buffer_components) # Get the area of the buffers
    dummy_buffer_area = get_area(art_gen, dummy_components) # Get the are of the dummy buffer
    total_area = pe_area*get_num_components(next(iter(pe_components))) + buffer_area*get_num_components(next(iter(buffer_components))) + dummy_buffer_area*get_num_components(next(iter(dummy_components)))

    results = "\n\n\nTotal Area: {}".format(str(total_area))
    for num_PEs, meshX in num_PE_generator(args.min_PE, args.max_PE):
        results = "{}\nNumber of PEs: {}\tMeshX: {}\tMeshY: {}".format(results, num_PEs, meshX, num_PEs/meshX)
        # Update PE and Dummy components
        pe_components = modify_PEs(system_state, pe_components, num_PEs - 1, meshX) # Change the number of PEs
        dummy_components = modify_PEs(system_state, dummy_components, meshX - 1, meshX) # Change the DummyBuffer (Eyeriss only)
        total_pe_area = pe_area*get_num_components(next(iter(pe_components)))
        total_dummy_buffer_area = dummy_buffer_area*get_num_components(next(iter(dummy_components)))
        # Find new buffer size based on new PE number
        best_percent = find_best_buffer_area(system_state, args.precision, buffer_components, total_area - total_pe_area - total_dummy_buffer_area)

        # TODO: Write a new file architecture for Timeloop to consume
        # yaml_generator(filename, num_PEs, buffer_parameters)

        # TODO: Run Timeloop to automatically search for the best mapping and get energy and latency results

        results = "{}\tBest Percent: {}".format(results, best_percent)
        break 
    return

def run_accelergy(args):
    # Create Global Storage of System Info
    system_state = SystemState()
    raw_dicts, precision, compute_ERT, compute_energy_estimate, compute_ART = parse_inputs(args, system_state) # Updates the system state as well

    if not args.iso_area:
        # Original usage of Accelergy
        compute_accelergy_estimates(system_state, raw_dicts, precision, compute_ERT, compute_energy_estimate, compute_ART, args.iso_area)

        find_iso_area_designs(args, system_state)
        # ----- Generate All Necessary Output Files
        generate_output_files(system_state)
    else:
        find_iso_area_designs(args, system_state)

def accelergy_wrapper(args):
    try:
        run_accelergy(args)
    except Exception as e:
        import sys
        import traceback
        from traceback import linecache
        import re
        tb = sys.exc_info()[2]

        print('\n' * 5 + '=' * 60)
        print(f'Accelergy has encountered an error and crashed. Error below: ')
        print('=' * 60)
        print('|| ' + traceback.format_exc().strip().replace('\n', '\n|| '))
        print('=' * 60)
        print(f'Stack with local variables (most recent call last):')
        stack = []
        while tb:
            stack.append((tb.tb_frame, tb.tb_lineno))
            tb = tb.tb_next

        frameno = 3
        current_frame = frameno
        contextrange = 3
        for frame, lineno in stack[-frameno:]:
            current_frame -= 1
            line = linecache.getline(frame.f_code.co_filename, lineno, frame.f_globals)
            context = []
            for i in range(lineno - contextrange, lineno + contextrange + 1):
                try:
                    l = linecache.getline(frame.f_code.co_filename, i, frame.f_globals)
                    context.append((i, l))
                except:
                    pass
            stripamount = min(len(c[1]) - len(c[1].lstrip()) for c in context)
            context = [('         ' if c[0] != lineno else 'ERROR >> ') + str(c[0]) + ': ' + c[1][stripamount:] for c in context]
            
            if current_frame != frameno:
                print('=' * 60)
            print(f'Frame {current_frame}')
            print('=' * 60)
            print(f'| {frame.f_code.co_filename}:{lineno}')
            print(f'| {type(e).__name__}: {e}')
            contextlines = '\n'.join(context)
            for k, v in frame.f_locals.items():
                if re.findall(r'\W' + k + r'\W', contextlines):
                    startline = f'Local var {k} ='
                    try:
                        strv = str(v)
                    except:
                        strv = '<Unable to print this variable]>'
                    print(f'| {startline:<40} {strv}')
            for c in context:
                print('| ' + c, end='')
            

        print('=' * 60)

        exit(-1)