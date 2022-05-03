import matplotlib.pyplot as plt

LAYER_SHAPES = {'AlexNet': ['AlexNet_layer2', 'AlexNet_layer3', 'AlexNet_layer4', 'AlexNet_layer5'], 
                'VGG01': ['VGG01_layer1', 'VGG01_layer2', 'VGG01_layer3', 'VGG01_layer4', 'VGG01_layer5', 'VGG01_layer6',
                'VGG01_layer7', 'VGG01_layer8']}

EYERISS_SHAPES = ['eyeriss_like_84_PEs', 'eyeriss_like_98_PEs', 'eyeriss_like_112_PEs', 'eyeriss_like_126_PEs',
                'eyeriss_like_140_PEs', 'eyeriss_like_154_PEs', 'eyeriss_like_168_PEs', 'eyeriss_like_182_PEs',
                'eyeriss_like_196_PEs', 'eyeriss_like_210_PEs', 'eyeriss_like_224_PEs', 'eyeriss_like_238_PEs',
                'eyeriss_like_252_PEs', 'eyeriss_like_266_PEs', 'eyeriss_like_280_PEs', 'eyeriss_like_294_PEs',
                'eyeriss_like_308_PEs', 'eyeriss_like_322_PEs', 'eyeriss_like_336_PEs']

NUM_PES = [84, 98, 112, 126, 140, 154, 168, 182, 196, 210, 224, 238, 252, 266, 280, 294, 308, 322, 336]

ALEXNET_LAYERS = [2, 3, 4, 5]

VGG_LAYERS = [1, 2, 3, 4, 5, 6, 7, 8]

def graph_data():
    # alexnet_cycles_data = []
    # alexnet_energy_data = []
    # vgg_cycles_data = []
    # vgg_energy_data = []

    workload_num = 0
    for eyeriss_workload in EYERISS_SHAPES:
        alexnet_cycles_data = []
        alexnet_energy_data = []
        vgg_cycles_data = []
        vgg_energy_data = []
        for workload, layers in LAYER_SHAPES.items():
            for layer in layers:
                filename = './output/eyeriss_like/{}/{}/{}/timeloop-mapper.stats.txt'.format(eyeriss_workload, workload, layer)
                important_data_reached = False
                with open(filename, 'r') as file:
                    for line in file:
                        data = line.split()

                        if 'Summary' in data: important_data_reached = True

                        if important_data_reached and len(data) != 0:
                            section = data[0]

                            if section == 'Cycles:':
                                value = int(data[1])
                                if workload == 'AlexNet': alexnet_cycles_data.append(value)
                                else: vgg_cycles_data.append(value)
                            if section == 'Energy:':
                                value = float(data[1])
                                if workload == 'AlexNet': alexnet_energy_data.append(value)
                                else: vgg_energy_data.append(value)
            curr_num_pes = NUM_PES[workload_num]                    

        # 336 PEs - outlier
        plt.scatter(alexnet_cycles_data, alexnet_energy_data)
        for i in range(len(ALEXNET_LAYERS)):
            layer_num = ALEXNET_LAYERS[i]
            plt.annotate(str(layer_num), (alexnet_cycles_data[i], alexnet_energy_data[i]), textcoords="offset points", xytext=(i*4,10),  ha='center')
        graph_title = 'Latency vs Energy per Layer - AlexNet ' + str(curr_num_pes) + ' PEs'
        plt.title(graph_title)
        plt.xlabel('Latency (num cyscles)', fontweight='bold')
        plt.ylabel('Energy consumption (uJ)', fontweight='bold')
        plt.ylim(0, 5000)
        plt.xlim(0, 7900000)
        plt.savefig(graph_title + '.png')
        plt.show()

        plt.scatter(vgg_cycles_data, vgg_energy_data)
        for i in range(len(VGG_LAYERS)):
            layer_num = VGG_LAYERS[i]
            plt.annotate(str(layer_num), (vgg_cycles_data[i], vgg_energy_data[i]), textcoords="offset points", xytext=(i*4,10), ha='center')
        graph_title = 'Latency vs Energy per Layer - VGG01 ' + str(curr_num_pes) + ' PEs'
        plt.title(graph_title)
        plt.xlabel('Latency (num cycles)', fontweight='bold')
        plt.ylabel('Energy consumption (uJ)', fontweight='bold')
        plt.ylim(0, 29000)
        plt.xlim(0, 39000000)
        plt.savefig(graph_title + '.png')
        plt.show()s

        workload_num += 1

        
    
    #print('AlexNet cycles: ', alexnet_cycles_data)
    #print('AlexNet energy: ', alexnet_energy_data)
    # Plotting AlexNet data
    # plt.scatter(alexnet_cycles_data, alexnet_energy_data)
    # layer_num = 0
    # for pe in NUM_PES:
    #     plt.annotate(str(pe), (alexnet_cycles_data[layer_num], alexnet_energy_data[layer_num]))
    #     layer_num += 1
    # plt.title('Latency vs Energy per Layer - AlexNet')
    # plt.xlabel('Latency (num cycles)', fontweight='bold')
    # plt.ylabel('Energy consumption (uJ)', fontweight='bold')
    # plt.show()

    # layer_num = 0
    # num_alexnet_layers = len(LAYER_SHAPES['AlexNet'])
    # for pe in NUM_PES[0:10]:
    #     current_cycle_data = alexnet_cycles_data[layer_num:layer_num + num_alexnet_layers]
    #     current_energy_data = alexnet_energy_data[layer_num:layer_num + num_alexnet_layers]
    #     graph_label = str(pe) + ' PEs'
    #     plt.plot(current_cycle_data, current_energy_data, 'o', label=graph_label)

    #     layer_num += num_alexnet_layers
    # plt.title('Latency vs Energy per Layer - AlexNet')
    # plt.xlabel('Latency (num cycles)', fontweight='bold')
    # plt.ylabel('Energy consumption (uJ)', fontweight='bold')
    # plt.legend(loc="upper left")
    # plt.show()

    # layer_num = 0
    # for pe in NUM_PES[10:19]:
    #     current_cycle_data = alexnet_cycles_data[layer_num:layer_num + num_alexnet_layers]
    #     current_energy_data = alexnet_energy_data[layer_num:layer_num + num_alexnet_layers]
    #     graph_label = str(pe) + ' PEs'
    #     plt.plot(current_cycle_data, current_energy_data, 'o', label=graph_label)

    #     layer_num += num_alexnet_layers
    # plt.title('Latency vs Energy per Layer - AlexNet')
    # plt.xlabel('Latency (num cycles)', fontweight='bold')
    # plt.ylabel('Energy consumption (uJ)', fontweight='bold')
    # plt.legend(loc="upper left")
    # plt.show()

    # layer_num = 0
    # num_vgg_layers = len(LAYER_SHAPES['VGG01'])
    # for pe in NUM_PES:
    #     current_cycle_data = vgg_cycles_data[layer_num:layer_num + num_vgg_layers]
    #     current_energy_data = vgg_energy_data[layer_num:layer_num + num_vgg_layers]
    #     graph_label = str(pe) + ' PEs'
    #     plt.plot(current_cycle_data, current_energy_data, 'o', label=graph_label)

    #     layer_num += num_vgg_layers
    # plt.title('Latency vs Energy per Layer - VGG01')
    # plt.xlabel('Latency (num cycles)', fontweight='bold')
    # plt.ylabel('Energy consumption (uJ)', fontweight='bold')
    # plt.legend(loc="upper left")
    # plt.show()





graph_data()