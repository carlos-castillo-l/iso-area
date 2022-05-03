import matplotlib.pyplot as plt

EYERISS_LAYER_SHAPES = {'AlexNet': ['AlexNet_layer2', 'AlexNet_layer3', 'AlexNet_layer4' ,'AlexNet_layer5'], 
                        'VGG01': ['VGG01_layer1', 'VGG01_layer2', 'VGG01_layer3', 'VGG01_layer4', 'VGG01_layer5', 'VGG01_layer6', 'VGG01_layer7', 'VGG01_layer8']}

LAYER_SHAPES = {'AlexNet': ['AlexNet_layer1', 'AlexNet_layer2', 'AlexNet_layer3', 'AlexNet_layer4' 
                ,'AlexNet_layer5'], 'VGG01': ['VGG01_layer1', 'VGG01_layer2', 'VGG01_layer3', 'VGG01_layer4', 'VGG01_layer5', 'VGG01_layer6', 'VGG01_layer7', 'VGG01_layer8']}

STATIONARY_PE_SHAPES = ['_96_PEs', '_112_PEs', '_128_PEs',
                '_144_PEs', '_160_PEs', '_176_PEs', '_192_PEs',
                '_208_PEs', '_224_PEs', '_240_PEs', '_256_PEs',
                '_272_PEs', '_288_PEs', '_304_PEs', '_320_PEs',
                '_336_PEs']

EYERISS_SHAPES = ['_84_PEs', '_98_PEs', '_112_PEs', '_140_PEs', '_154_PEs', '_168_PEs', '_182_PEs', '_196_PEs',
                '_210_PEs', '_224_PEs', '_238_PEs', '_252_PEs', '_266_PEs', '_280_PEs', '_294_PEs', '_308_PEs',
                '_322_PEs', '_336_PEs']

EYERISS_NUM_PES = [84, 98, 112, 126, 140, 154, 168, 182, 196, 210, 224, 238, 252, 266, 280, 294, 308, 322, 336]

STATIONARY_NUM_PES = [96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 256, 272, 288, 304, 320, 366]

ALEXNET_LAYERS = [1, 2, 3, 4, 5]

VGG_LAYERS = [1, 2, 3, 4, 5, 6, 7, 8]

eyeriss_alexnet_cycles_data = []
eyeriss_alexnet_energy_data = []
eyersiss_vgg_cycles_data = []
eyeriss_vgg_energy_data = []
important_data_reached = False
for workload, layers in EYERISS_LAYER_SHAPES.items():
    for layer in layers:
        filename = './output/eyeriss_like/eyeriss_like_168_PEs/{}/{}/timeloop-mapper.stats.txt'.format(workload, layer)
        with open(filename, 'r') as file:
            for line in file:
                data = line.split()

                if 'Summary' in data: important_data_reached = True

                if important_data_reached and len(data) != 0:
                    section = data[0]

                    if section == 'Cycles:':
                        value = int(data[1])
                        if workload == 'AlexNet': eyeriss_alexnet_cycles_data.append(value)
                        else: eyersiss_vgg_cycles_data.append(value)
                    if section == 'Energy:':
                        value = float(data[1])
                        if workload == 'AlexNet': eyeriss_alexnet_energy_data.append(value)
                        else: eyeriss_vgg_energy_data.append(value)
alexnet_cycles_avg = sum(eyeriss_alexnet_cycles_data)/len(eyeriss_alexnet_cycles_data)
alexnet_energy_avg = sum(eyeriss_alexnet_energy_data)/len(eyeriss_alexnet_energy_data)
vgg_cycles_avg = sum(eyersiss_vgg_cycles_data)/len(eyersiss_vgg_cycles_data)
vgg_energy_avg = sum(eyeriss_vgg_energy_data)/len(eyeriss_vgg_energy_data)

def graph_data(output):
    alexnet_normalized_energy = []
    alexnet_normalized_cycles = []
    vgg_normalized_cycles = []
    vgg_normalized_energy = []

    output_to_name = {'weight': 'simple_weight_stationary', 'output': 'simple_output_stationary', 'eyeriss': 'eyeriss_like'}
    output_to_pes = {'weight': STATIONARY_NUM_PES, 'output': STATIONARY_NUM_PES, 'eyeriss': EYERISS_NUM_PES}
    output_to_pe_shapes = {'weight': STATIONARY_PE_SHAPES, 'output': STATIONARY_PE_SHAPES, 'eyeriss': EYERISS_SHAPES}
    output_to_layer_shapes = {'weight': LAYER_SHAPES, 'output': LAYER_SHAPES, 'eyeriss': EYERISS_LAYER_SHAPES}

    current_output = output_to_name[output]
    NUM_PES = output_to_pes[output]
    PE_SHAPES = output_to_pe_shapes[output]
    CURR_LAYER_SHAPES = output_to_layer_shapes[output]

    
    workload_num = 0
    for pe_shape in PE_SHAPES:
        alexnet_cycles_data = []
        alexnet_energy_data = []
        vgg_cycles_data = []
        vgg_energy_data = []
        for workload, layers in CURR_LAYER_SHAPES.items():
            for layer in layers:
                filename = './output/{}/{}/{}/{}/timeloop-mapper.stats.txt'.format(current_output, current_output+pe_shape, workload, layer)
                important_data_reached = False
                with open(filename, 'r') as file:
                    for line in file:
                        data = line.split()

                        if 'Summary' in data: important_data_reached = True

                        if important_data_reached and len(data) != 0:
                            section = data[0]

                            if section == 'Cycles:':
                                value = int(data[1])
                                if workload == 'AlexNet': alexnet_cycles_data.append(value) #alexnet_cycles_data.append(value/alexnet_cycles_avg)
                                else: vgg_cycles_data.append(value)
                            if section == 'Energy:':
                                value = float(data[1])
                                if workload == 'AlexNet': alexnet_energy_data.append(value)
                                else: vgg_energy_data.append(value)
            curr_num_pes = NUM_PES[workload_num]

        alexnet_normalized_cycles.append(sum(alexnet_cycles_data)/alexnet_cycles_avg)
        alexnet_normalized_energy.append(sum(alexnet_energy_data)/alexnet_energy_avg)
        vgg_normalized_cycles.append(sum(vgg_cycles_data)/vgg_cycles_avg)
        vgg_normalized_energy.append(sum(vgg_energy_data)/vgg_cycles_avg)

        # FOR REGULAR GRAPHS

        # 336 PEs - outlier
        # plt.scatter(alexnet_cycles_data, alexnet_energy_data)
        # for i in range(len(ALEXNET_LAYERS)):
        #     layer_num = ALEXNET_LAYERS[i]
        #     plt.annotate(str(layer_num), (alexnet_cycles_data[i], alexnet_energy_data[i]), textcoords="offset points", xytext=(i*4,10),  ha='center')
        # graph_title = 'Latency vs Energy per Layer - AlexNet ' + str(curr_num_pes) + ' PEs - normalized'
        # plt.title(graph_title)
        # plt.xlabel('Latency (num cycles)', fontweight='bold')
        # plt.ylabel('Energy consumption (uJ)', fontweight='bold')
        # # plt.ylim(0, 5000)
        # # plt.xlim(0, 7900000)
        # plt.ylim(0, 12) # normalized
        # plt.xlim(0, 5.4) # normalized
        # plt.savefig(graph_title + '.png')
        # plt.show()

        # plt.scatter(vgg_cycles_data, vgg_energy_data)
        # for i in range(len(VGG_LAYERS)):
        #     layer_num = VGG_LAYERS[i]
        #     plt.annotate(str(layer_num), (vgg_cycles_data[i], vgg_energy_data[i]), textcoords="offset points", xytext=(i*4,5), ha='center')
        # graph_title = 'Latency vs Energy per Layer - VGG01 ' + str(curr_num_pes) + ' PEs - normalized'
        # plt.title(graph_title)
        # plt.xlabel('Latency (num cycles)', fontweight='bold')
        # plt.ylabel('Energy consumption (uJ)', fontweight='bold')
        # # plt.ylim(0, 29000)
        # # plt.xlim(0, 39000000)
        # plt.ylim(0, 29) # normalized
        # plt.xlim(0, 5.4) # normalized
        # plt.savefig(graph_title + '.png')
        # plt.show()

        workload_num += 1
    
    # BAR GRAPHS
    graph_title = 'Number of PEs vs Normalized Energy - AlexNet'
    plt.bar([i for i in range(len(NUM_PES))],  alexnet_normalized_energy, tick_label=[str(j) for j in NUM_PES])
    plt.title(graph_title)
    plt.xlabel('Number of PEs', fontweight='bold')
    plt.ylabel('Energy consumption (uJ)', fontweight='bold')
    plt.savefig(graph_title + '.png')
    plt.show()

    graph_title = 'Number of PEs vs Normalized Energy - VGG01'
    plt.bar([i for i in range(len(NUM_PES))],  vgg_normalized_energy, tick_label=[str(j) for j in NUM_PES])
    plt.title(graph_title)
    plt.xlabel('Number of PEs', fontweight='bold')
    plt.ylabel('Energy consumption (uJ)', fontweight='bold')
    plt.savefig(graph_title + '.png')
    plt.show()

    graph_title = 'Number of PEs vs Normalized Latency - AlexNet'
    plt.bar([i for i in range(len(NUM_PES))],  alexnet_normalized_cycles, tick_label=[str(j) for j in NUM_PES])
    plt.title(graph_title)
    plt.xlabel('Latency (num cycles)', fontweight='bold')
    plt.ylabel('Energy consumption (uJ)', fontweight='bold')
    plt.savefig(graph_title + '.png')
    plt.show()

    graph_title = 'Number of PEs vs Normalized Latency - VGG01'
    plt.bar([i for i in range(len(NUM_PES))],  vgg_normalized_cycles, tick_label=[str(j) for j in NUM_PES])
    plt.title(graph_title)
    plt.xlabel('Latency (num cycles)', fontweight='bold')
    plt.ylabel('Energy consumption (uJ)', fontweight='bold')
    plt.savefig(graph_title + '.png')
    plt.show()

    

    





graph_data('eyeriss')