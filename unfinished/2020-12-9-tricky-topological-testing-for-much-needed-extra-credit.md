---
layout: post
title: "A Tricky Topological Test For Some Much Needed Extra Credit"
description: "Can you connect each pair of dots without passing through the box or other connections?"
tags: [math]
---

As an occasional Instagram doomscroller, I've encountered this sort of ad more than a few times.

<img src="https://i.redd.it/uiksegu951n81.jpg" width="200"/>

Although I love the disingenuity of corporations exploiting the concept of "nerd sniping" to boost consumer engagement and downloads, they're definitely a little late to the party.

![](https://imgs.xkcd.com/comics/nerd_sniping.png)

An Instagram ad certianly wasn't enough to send me down the rabbit hole of topology and complex analysis, but recently, in my math class, we were given the following problem for one point of extra credit.

![problem](https://i.gyazo.com/fdf711d47f045628ca7c5edfc5deb617.png)

<small>_Can you connect each pair of dots without passing through the box or other connections?_</small>

This problem, to me anyways, was tricky! Although I couldn't find the solution in class, I wanted to try to generalize this problem. What about N points on any surface? Even better, can we write an efficient algorithm to test for the solvability for a generalized connection problem, or perhaps even solve it?

There's too many questions with not many answers, so let's dive right in.

## Approaching The Puzzle

The first step with any puzzle is to play with it. Let's try some weirder surfaces and make some observations.

![lol](https://i.gyazo.com/6d9937e9287082c1e22012f739897499.png)

Let's take a look at this croissant looking shape. There's a few things to notice here:

- Blue looks awfully easy to connect.
- Yellow looks even easier.
- Dots on the border just look.. plain harder to connect.
- If our croissant looked like this, not much would change.
  ![lol](https://i.gyazo.com/dee83fd8d62dd7f29b4be3839d70639c.png)

From our recorded observations, there's two notable takeaways:

- There seems to be a difference between points on the border and points off the border.
- Some changes to the surface don't change the solvability of the problem.

This inspires a few questions! First, what's the difference between off and on border point pairs? Does moving a point off or on a border change solvability? What changes to the surface change solvability?

Let's tackle one at a time. First, let's look at how different surfaces affect the solvability of the problem.

## Surfaces Affecting Solvability

We've noticed that there exist ways to modify a surface such that it doesn't affect the solvability of the problem. It would then follow that we'd need to figure out what modifications to the surface cause a problem set to go from _solvable_ to _unsolvable_.

The answer, surprisingly, lies deep within the realm of complex analysis. Let's take a look.

_Theorem: If point pairs P are solvable on a proper non-empty simply connected open subset of C, P is solvable on **every** proper non-empty simply connected open subset of C._

Woah, bold claim, I know. Essentially, what we're saying is if we can draw the P's solution on one surface, it implies we can draw P's solution on any surface! Well, how is this possible?

Let's make the question more rigorous. What we're essentially saying is that there exists some transformation from from S1 to S2 such that non-intersecting curves drawn on S1 _stay_ non-intersecting after the transformation. How do we prove this?

### Conformal Maps

If you're familiar with complex analysis, you've likely heard of _[conformal maps](https://en.wikipedia.org/wiki/Conformal_map)_. If not, conformal maps are a special type of transformation from one complex set to another complex set such that _angles_ and _orientations_ are preserved. This means two intersecting lines will also intersect at the same angle after the transformation, even if these lines get distorted.

![A conformal map](https://i.gyazo.com/5ade11d5e37cca26d0bcbf446fb2f067.png)

However, there's absolutely no reason conformal maps need to ensure that non-crossing lines will stay non-crossing. We'd need a new transformation with a slighlty stricter definition to prove this.

### Biholomorphic Maps

Enter the _[biholomorphic map](https://en.wikipedia.org/wiki/Biholomorphism)_, a specific type of conformal map whose inverse map, the map which reverses the effect of the original map, is also conformal. Let's try to prove that this transformation will not cross non-crossing lines!

We'll do this with contradiction. Let's say we have a biholomorphic map M : A -> B st. A, B e C. Assume M causes non-crossing lines in A to cross in B. It would then follow that M^-1(M(A)) would uncross those lines since A has no crossed lines. However, since M^-1 is a conformal map, crossing lines would need cross at the same angle they were originally intersecting at. Therefore, M cannot cause non-crossing lines in A to cross in B, and as a result cannot cause a problem set to go from solvable to unsolvable! Of course, since M is conformal, it can't uncross lines either, which means an unsolvable set won't become solvable after applying M.

Cool! Now that we've proved biholomorphic maps don't change the solvability of a problem set on different surfaces, we just need to prove a biholomorphic map exists between those surfaces. How do we do that?

### The Riemann Mapping Theorem

The [Riemann mapping theorem](https://en.wikipedia.org/wiki/Riemann_mapping_theorem) states that for every proper non-empty simply connected open subset of the complex plane (what we've been calling a surface), there exists a biholomorphic mapping from that subset to the unit disk. Consider the mappings guarenteed by the RMT for both A and B, which we'll call M_a and M_b respectively. Applying M_b^-1(M_a(A)) will take A to B, without affecting solvability.

![](https://upload.wikimedia.org/wikipedia/commons/e/e9/Illustration_of_Riemann_Mapping_Theorem.JPG?20110405093707)
<small>_Example of Riemann mapping_</small>

Therefore, any problem set solvable on one surface is solvable on every other surface! Pretty neat, huh?

<small>A bit of a nitpick, but RMT only applies to _open_ subsets without a boundary. However, you might have noticed that our surfaces contain points on the boundary, so we need to ensure we have a mapping which includes the boundary. [Carathéodory's theorem](<https://en.wikipedia.org/wiki/Carath%C3%A9odory%27s_theorem_(conformal_mapping)>) tells us that the mapping will still exists as long as the boundary is a [Jordan curve](https://en.wikipedia.org/wiki/Curve#Jordan). We won't get into the specifics of Jordan curves, but essentialy this means that our boundary must be a closed loop with no self intersection. Since all our surfaces have this property, RMT still applies.</small>

## Point Pair Classification

Let's work on the unit disk now since it's the simplest surface we can find and play with the different types of point pairs.

![CC point circle](https://i.gyazo.com/c43aa8d08b81cfa45a84b71b11e22cde.png)
![DD point circle](https://i.gyazo.com/4f17fe34eac143c39ed9c678ebcea161.png)

One is clearly solvable, the other isn't. Well, why? On the first image, all the points are on the border, so it "slices" the circle into two pieces when we connect a pair. How exactly this path is constructed doesn't really matter, in the end, we end up with two slices.

In the second, the circle isn't divided at all! When we connect the second pair, we're able to go _around_ the first pair's path. This isn't possible when the points are on the border, since we hit the border of the surface when trying to go around the first path.

Let's make this property rigorous. We'll need to classify our point pairs, so lets list them out and give them cute names.

- In the first case, both points in the pair are on the boundary of the surface. Let's call these points conjoint-conjoint, or CC.
- In the second case, one point is on the surface boundary and the second is off it. Let's call these points conjoint-disjoint, or CD. Without loss of generality, we can assume that CD = DC, since the point pairs are reflexive.
- In the last case, both points are off the surface boundary. They'll be called disjoint-disjoint, or DD.

### Disjoint-Disjoint Solving: The Minimum Spanning Tree

Let's explore the DD points first. As seen in the example above, they seem to affect solvability signficantly less than CC points, and probably CD points by extension.

One property we noted of DD connections was the ability to "wrap" potentially blocking paths: A DD pair's path may cross over another DD pair's path, but one of the paths may always be "wrapped" around the other in order to fix the intersection.

What would happen if, for every DD pair, we drew a straight line connecting both points, wrapping the path around every other DD pair path in it's way? Well, we'd end up with a rather interesting construction. Let's take a closer look.

Consider the following problem set.

![DD unconnected problem set](https://i.gyazo.com/d08b2f762626501ae6d47b978cb863c3.png)

We can start by drawing every straight line, completely ignoring intersection.

![DD connected intersecting line](https://i.gyazo.com/fa0633723f63d9cfa3fc0b448d101e59.png)

Not too interesting. Let's try fixing these intersections with iterated wrapping.

![DD connected wrapped](https://i.gyazo.com/55e74f4095295355c0ce0df142e1e955.png)

Interesting! Although this is a valid solution to this set of DD points, the image itself is a little misleading. Here, using my imperfect trackpad skills, I've drawn the lines with a bit of width and spacing. In reality, lines have no width and wouldn't be spaced apart at all. If we remove the color and consider what it would look like in the limiting case, it would look more like this.

![DD connected wrapped limit](https://i.gyazo.com/4dffaefab18225ba6424968aa7725afb.png)

Although this idea of "wrapping" is cool and all, it's by no means rigorous. Can we prove this structure, which we'll call the DD tree, is always constructable?

Yes! First, we'll need to analyze the DD tree further and establish some properties, which we can then use for the proof.

First, the DD tree will never intersect the border. Because lines have no width, the closest the the DD tree will ever be to the border is whatever DD point happens to be closest.
