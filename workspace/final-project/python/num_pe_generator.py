import random
def num_PE_generator(meshX, min_PE, max_PE):
  return random.randint(min_PE/meshX, max_PE/meshX) * meshX

if __name__ == "__main__":
  for _ in range(10):
    print (num_PE_generator(14, 168/2, 168*2))