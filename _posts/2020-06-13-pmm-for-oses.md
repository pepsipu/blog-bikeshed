---
layout: post
title: "Writing a Physical Memory Manager for Operating Systems"
description: "Implementing a circular double linked list kernel memory allocator for my latest operating system, dbOS."
tags: [kmalloc, heap, pmm]
---
 `malloc` and `free`. The two most essential functions to dynamic memory in userland. `malloc` provides chunks of memory to the program of the request size, no questions asked. The only requirement is, when you finish using the chunk, you return it to the allocator with `free`. It's not very important to most C developers how the internals of both of these functions work, and even less important on how the counter parts of these functions, `kmalloc` and `kfree` work in ring 0, kernel land. But, when it comes time to write your own operating system, it's imperative you understand how `kmalloc` makes physical memory available to internal routines in ring 0.
 
 Physical memory is a different beast entirely when compared to the virtual memory that programs in userland utilize. `malloc` and `free` simply "request" virtual memory from the kernel and don't need to worry about the physical memory that the virtual memory maps to. Now we are writing our own physical memory allocator, we should discuss memory maps.

## Memory Maps
Memory maps provide a way for operating systems to know the layout of RAM. For example, memory maps allow the operating system to know where memory mapped peripherals, regions for free use, reserved regions, and bad/faulty memory is located. Though, how does an operating system obtain a memory map?

### Creating a Memory Map
Routines made available by the BIOS can be used to obtain information about the memory. The biggest things we will need to know are the upper bound of the memory and the lower bound of the memory.

#### Lower Memory Bound
Although it's assumed that address `0x0` should be the first memory address, it's extremely discouraged to use it. The BIOS uses a special interrupt table stored at address 0 called the interrupt vector table which handles software and hardware interrupts. If you use address 0, or any memory near to it for that matter, you'll end up smashing the IVT. So, how to do we get the lowest address in memory that the BIOS doesn't use?

To fetch the lower bound of available memory, you can call upon the BIOS to help you out. Software interrupt 0x12 will load register `AX` with the amount of KB away from address 0 the first available address is. Our assembly code would look a little something like this:

```asm
int 0x12
; AX * 1024 will be the address
```

#### Upper Memory Bound
Getting the upper memory bound is slightly more complicated. Since, as you know, physical memory is not linear and has several memory regions which are unavailable for use, getting a clear "upper bound" is not really possible.

Thankfully, the BIOS has us covered again. By raising software interrupt 0x15, as well as setting `EAX` to `0xe820`, we can get a region and it's properties provided by the BIOS.

On raising the interrupt, `ES:DI` will be used as the pointer to the buffer and `ECX` will be how many bytes to read from the memory map to the buffer.

`EBX` has a very special role in this interrupt. It is used as the "Continuation" value. Since you can only retrieve one region's information from the BIOS, `EBX` contains what is essentially a pointer to the next entry in the memory map.

The 0x15 interrupt is raised once per entry. Raising it 10 times will get you 10 entries.

From what I could get off of the 1996 GRUB specification, the entries are structured as so:

```c
struct mmap_entry {
    uint64_t start_address;
    uint64_t length;
    uint32_t type;
};
```

`type` will tell you about the region. There are different types of memory regions, but for now, you should know that a type of `1` will mean the region is free.

## Writing a memory allocator which uses memory that spans multiple non-contiguous regions

### Initialization
In userland, thanks to the magic of virtual memory, memory is almost always linear in the heap. This means that when you request more memory from the operating system, the new memory will be adjacent to the rest of the memory on the heap. We don't have these luxuries in kernel space, so we will need to make sure our allocator takes into consideration multiple regions.

This isn't as difficult as it sounds. The main thing we need to do to accommodate this change is include metadata about each region in some sort of list.

Let's make a structure that will keep tabs on each region of memory.
```c
typedef struct
{
    void *addr;
    uint64_t len;
    uint64_t used;
} region_state_t;
```
This information needs to be stored for each region, so I'll make a global variable that points to an array of `region_state_t` and another variable that holds the amount of elements in that array.

```c
region_state_t *fm_regions;
uint32_t fm_region_len;
```

We can use the memory map from before to find free regions and store those regions in an array. Since we don't have a heap yet, we can use a dynamically allocated stack array until we do get a heap.

Our init function for our physical memory manager would need to do find each free region, which has a type of one, and add it to the stack array. This is done like so:
```c
// in function void init_pmm(multiboot_memory_map_t *mmap_addr, uint32_t mmap_length);
multiboot_memory_map_t *entry = mmap_addr;
// use dynamic stack array because we don't have heap yet
multiboot_memory_map_t *free_memory_region[mmap_length / sizeof(multiboot_memory_map_t)];
int free_memory_count;
for (free_memory_count = 0; mmap_addr + mmap_length > entry;)
{
    if (entry->type == 1)
    {
        free_memory_region[free_memory_count] = entry;
        ++free_memory_count;
    }
    entry = (multiboot_memory_map_t *)((uint32_t)entry + entry->size + sizeof(entry->size));
}
```
Here, we cycle through each entry of the memory map (which GRUB provides us through the methods mentioned before) and specifically save the regions which have a type of one, meaning it is marked as available memory.

Now, we need to find a memory region to store our metadata about all the regions. We can't keep using a stack array, since that won't last outside the initialization function. To do this, we simply cycle through each region, looking for a region large enough to house the metadata. Once we find a region like that, we move information from the stack array to the new array in the region. Then, we can shrink the region by the size of the metadata array, so we can use the rest of the region without modifying the metadata.

We can do this like so:
```c
fm_region_len = free_memory_count;
// find region who can store metadata
int metadata_chunk_index = 0;
size_t size_needed = sizeof(region_state_t) * fm_region_len;
while (metadata_chunk_index < fm_region_len)
{
    multiboot_memory_map_t *region = free_memory_region[metadata_chunk_index];
    if (region->len > size_needed)
    {
        fm_regions = region->addr;
        // shift over usable memory so we dont overwrite the region metadata
        region->addr += size_needed;
        for (int i = 0; fm_region_len > i; ++i)
        {
            region_state_t *new_region = fm_regions + i * sizeof(region_state_t);
            *new_region = (region_state_t){
                .addr = region->addr,
                .len = region->len,
                .used = 0,
            };
        }
        break;
    }
    ++metadata_chunk_index;
}
```

Now that we've saved all our information about the regions into an array in one of the regions, we can finally use this data in our `kmalloc` and `kfree` functions.
### Chunk Structures
First, let's define a structure of an allocated chunk.
```c
typedef struct
{
    size_t size;
    uint8_t data[];
} allocated_chunk_t;
```
All it'll contain is the size of the chunk and user data after it. Pretty simple, right?

Now, we need to define how our freed chunks are going to look like.
```c
struct free_chunk
{
    size_t size;
    struct free_chunk *fd;
    struct free_chunk *bk;
};
typedef struct free_chunk free_chunk_t;
```
It's the same as the allocated chunk, but where the data once was, we now have forward and backward pointers for our double linked list. The forward pointer will point to the next free chunk, and the backward pointer will point to the freed chunk before it.

I'm also going to make a global variable called `free_bin`, which will contain the forward and backward starting pointers for the free chunks.
```c
free_chunk_t free_bin = (free_chunk_t) {
    .size = 0,
    .fd = &free_bin,
    .bk = &free_bin,
};
```
Since this is a circularly linked list, it's forward and backward pointers are going to be itself.
## kmalloc
`kmalloc` is going to be the function that the kernel will be calling when it needs memory.

First, we should define the order of which `kmalloc` will look for free memory. The first thing it should do is search through the list of free chunks, looking for a free chunk which is exactly the size of the requested chunk. If it is, we can just return the free chunk. If the free chunk is bigger, we can split the chunk into two chunks and return the one that is the request size. If we can't find a free chunk like that, we can simply use a region's memory. Let's implement that in code.

```c
void *kmalloc(size_t requested_size)
{
    if (requested_size == 0)
        return NULL;
    // round to nearest multiple of 8 so we get alignment
    size_t aligned_size = (requested_size  + sizeof(allocated_chunk_t) + 7) & -8;
    // ensure size is big enough to fit a free chunk
    size_t size = aligned_size < sizeof(free_chunk_t) ? sizeof(free_chunk_t) : aligned_size;
    free_chunk_t *ptr = free_bin.fd;
    while (ptr != &free_bin)
        {
            if (ptr->size == size)
            {
                // unlink from free list
                ptr->bk->fd = ptr->fd;
                ptr->fd->bk = ptr->bk;
                return ptr + sizeof(allocated_chunk_t);
            }
            // ensure we can split chunk and still have space for a free chunk
            if (ptr->size > size && ptr->size - size - sizeof(allocated_chunk_t) > sizeof(free_chunk_t))
            {
                ptr->size -= size + sizeof(allocated_chunk_t);
                allocated_chunk_t *new_chunk = ptr + ptr->size + sizeof(allocated_chunk_t);
                new_chunk->size = size;
            }
            ptr = ptr->fd;
        }
    // if we can't find a free chunk, we can make a new chunk from the memory regions
    for (int i = 0; i < fm_region_len; i++)
    {
        region_state_t *region = &fm_regions[i];
        if (region->len - region->used > size)
        {
            allocated_chunk_t *new_chunk = region->addr + region->used;
            new_chunk->size = size;
            region->used += size + sizeof(allocated_chunk_t);
            return &new_chunk->data;
        }
    }
    // uh oh
    return NULL;
}
```

## kfree
`kfree` is pretty easy to implement. All we have to do is add the given chunk to the free list. We insert at the start of the list, changing `free_bin`'s forward and backward pointers.
```c
void kfree(void *chunk) {
    free_chunk_t *chunk_to_free = chunk - sizeof(allocated_chunk_t);
    // link chunk to free list
    chunk_to_free->bk = free_bin.fd->bk;
    free_bin.fd->bk = chunk_to_free;
    chunk_to_free->fd = free_bin.fd;
    free_bin.fd = chunk_to_free;
}
```
