---
layout: post
title: "The Tale of Apple and Project Zero"
description: "The ever-evolving cat and mouse game between Apple and Project Zero for 0days."
tags: [ctf]
---

# Introduction
Project Zero has been one of the most powerful bug hunting entities in the security world, targeting a multitude of platforms. To start learning iOS pwn, I've decided to go through every one of their blog posts on the Apple platform. Unsurprisingly, a really interesting narrative written by many neat exploits and cool hackers emerged from this research.

# The Wild West of XNU Exploits
As Project Zero formed in 2014, they wasted no time getting to work. In less than a month P0 had set their eyes on Apple's vast ecosystem, targeting Safari and XNU sandboxes. Although browser is definitely for another day, let's talk about these sandbox escapes.

## launchd's launch_data_unpack
To be sandboxed, in technical terms, is to strip the rights of a process to perform certian actions. On Linux, homebrewed sandboxes with `prctl` and the more traditional `seccomp` are used to regulate and restrict possibly compromised processes from messing with other processes or data on the system.

On Darwin, 
