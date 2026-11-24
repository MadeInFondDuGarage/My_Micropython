import gc

gc.collect()
print("Mémoire libre :", gc.mem_free(), "octets")