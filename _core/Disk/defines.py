# Disk setup
disk_size = 1024 ** 2  # 1MB
block_size = 1024  # 1KB per block
total_blocks = disk_size // block_size
disk_name = "/Users/VICKY/PycharmProjects/NebulaOS Restart/disk.ndi"

# Superblock structure
superblock = {
    "total_blocks": total_blocks,
    "used_blocks": 0,
    "block_size": block_size,
    "free_block_map": [True] * total_blocks,  # All blocks are free initially
    "root": {  # Root directory
        "type": "dir",
        "contents": {}  # Stores files & subdirectories
    },
    "current_dir": "/"  # Start at root
}
