import os, gc, esp32

def get_flash_info():
    """Retourne la taille totale et libre du VFS (FAT ou LittleFS)."""
    stats = os.statvfs("/")
    block_size = stats[0]
    total_blocks = stats[2]
    free_blocks = stats[3]
    total = total_blocks * block_size
    free = free_blocks * block_size
    return total, free

def get_ram_info():
    """Retourne la RAM MicroPython (heap) : libre / utilisée / totale."""
    free = gc.mem_free()
    used = gc.mem_alloc()
    total = free + used
    return total, free, used

if __name__ =="__main__":
# ------------------------------
# Affichage lisible
# ------------------------------

    flash_total, flash_free = get_flash_info()
    ram_total, ram_free, ram_used = get_ram_info()
    #psram_total, psram_free, heaps = get_psram_info()

    print("\n===== FLASH =====")
    print(f"Taille totale VFS : {flash_total/1024/1024:.2f} MB")
    print(f"Espace libre VFS  : {flash_free/1024/1024:.2f} MB")

    print("\n===== RAM (Heap MicroPython) =====")
    print(f"RAM totale : {ram_total/1024:.0f} KB")
    print(f"RAM libre  : {ram_free/1024:.0f} KB")
    print(f"RAM utilisée : {ram_used/1024:.0f} KB")


