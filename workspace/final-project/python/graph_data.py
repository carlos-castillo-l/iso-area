import matplotlib.pyplot as plt

LAYER_SHAPES = {'AlexNet': ['AlexNet_layer1', 'AlexNet_layer2', 'AlexNet_layer3', 'AlexNet_layer4', 'AlexNet_layer5'], 
                'VGG01': ['VGG01_layer1', 'VGG01_layer2', 'VGG01_layer3', 'VGG01_layer4', 'VGG01_layer5', 'VGG01_layer6',
                'VGG01_layer7', 'VGG01_layer8']}

def graph_data():
    utilization_data = {}
    cycles_data = {}
    energy_data = {}
    area_data = {}

    for workload, layers in LAYER_SHAPES.items():
        for layer in layers:
            filename = './output/eyeriss_like_252_PEs/{}/{}/timeloop-mapper.stats.txt'.format(workload, layer)
            important_data_reached = False
            with open(filename, 'r') as file:
                for line in file:
                    data = line.split()

                    if 'Summary' in data: important_data_reached = True

                    if important_data_reached and len(data) != 0:
                        section = data[0]

                        if section == 'Utilization:':
                            utilization_data[layer] = data[1]
                        if section == 'Cycles:':
                            cycles_data[layer] = data[1]
                        if section == 'Energy:':
                            energy_data[layer] = data[1]
                        if section == 'Area:':
                            area_data[layer] = data[1]
        break # only becuase VGG01 data is not available yet

    # for _, layer_num in LAYER_SHAPES.items():

    #     plt.plot(x, y, label=str(layer_num))
    #     plt.title()
    #     plt.xlabel()
    #     plt.ylabel()
    #     plt.legend(loc="upper left")
    #     plt.show()

    #     plt.bar() # <--- if we want to use a bar graph

graph_data()