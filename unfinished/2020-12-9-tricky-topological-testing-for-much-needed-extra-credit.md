---
layout: post
title: "A Tricky Topological Test For Some Much Needed Extra Credit"
description: "Can you connect each pair of dots without passing through the box or other connections?"
tags: [math]
---

Recently, in my math class, we were given the following problem for one point of extra credit.

![problem](https://i.gyazo.com/fdf711d47f045628ca7c5edfc5deb617.png)

<small>_Can you connect each pair of dots without passing through the box or other connections?_</small>

This problem, to me anyways, was tricky! Although I couldn't find the solution instantly, I wanted to try to generalize this problem. What about N points on any surface? Even better, can we write an efficient algorithm to test for the solvability for a generalized connection problem, or perhaps even solve it?

There's a lot of questions with not many answers here, so let's jump into it.

### Approaching The Puzzle

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

Let's tackle one at a time. First, let's look at our points, since I don't know much about surfaces.

### Point Pair Classification

Let's make a simple surface now, and play with the different types of point pairs.

![lmfao](https://i.gyazo.com/c43aa8d08b81cfa45a84b71b11e22cde.png)
![sus](https://i.gyazo.com/4f17fe34eac143c39ed9c678ebcea161.png)

One is clearly solvable, the other isn't. Well, why? On the first image, all the points are on the border, so it "slices" the circle into two pieces when we connect a pair. How exactly this path is constructed doesn't really matter, in the end, we end up with two slices.

In the second, the circle isn't divided at all! When we connect the second pair, we're able to go _around_ the first pair's path. This isn't possible when the points are on the border, since we hit the border of the surface when trying to go around the first path.

Let's make this property rigorous. We'll need to classify our point pairs, so lets list them out and give them cute names.

- In the first case, both points in the pair are on the boundary of the surface. Let's call these points conjoint-conjoint, or CC.
- In the second case, one point is on the surface boundary and the second is off it. Let's call these points conjoint-disjoint, or CD. Without loss of generality, we can assume that CD = DC, since the point pairs are reflexive.
- In the last case, both points are off the surface boundary. They'll be called disjoint-disjoint, or DD.

As we discussed, some point pairs have the property that we can go _around_ their path. For DD pairs, since both points are not attached to the surface boundary, any pair P's connection that _would_ pass through a DD pair's connection can be wrapped around the path, like so:
![](https://i.gyazo.com/98444cd9d6020ee2826587902a039cec.png)

Alright, let's formalize this a bit.

_Lemma: DD points do not affect the solvability of a connection set._
We'll prove this by contradiction. First, let's say we have a set of point pairs, P, on a surface S. We can connect all the points P on the surface S without intersection. We'll start by assuming that the addition of D, some DD pair, to P causes the set to be unsolvable on S. Let's show why this is impossible.

Draw a straight line between each point in the DD pair. Odds are, you'll intersect some another path between other pairs on the surface with this line. That's ok! The crux in proving that we can "fix" these intersecting paths to not intersect is by designing a "wrapping" algorithm which will "wrap" the intersecting paths around the DD pair's path.

Let's design this algorithm. First, consider two intersecting paths.
![](https://i.gyazo.com/225453c8cb414ab467a6044c5e3ba910.png)

_Red is a DD pair, blue is some path_

This is no good! How can we "fix" the blue line? Well, since it's a DD pair and there's a finite amount of space between the point and the border, maybe we can curl the blue line around the red one? If we bring the blue line super close to the red one, infinitely close, then hug the red line all the way around the line, all the way back to the point of intersection, we'll be able to fix a line. It's a confusing process, so it'll make more sense with a visual.

Let the first line come infinitely close to the second:

![](https://i.gyazo.com/13e951a857f48b90805283fbba9ee02c.png)

Hug the wall of the second line until the point of intersection:

![](https://i.gyazo.com/1327e813b0027b27f1d26f7985bdc23c.png)

We can prove that wrapping will _always_ turn a path intersecting a DD path into a non-intersecting path through this method. Since lines have zero width, no matter how many lines we have running between a disjoint point and a border, we'll always have enough space to wrap

It's important to note that is process can be repeated for any number of lines. If, in the process of wrapping a DD path, we intersect a second path wrapping the same path, we can then _wrap the second path_ too, recursively wrapping whatever gets in our way. Here's a pretty visualization of the process

Effectively, we've proven that we can _ignore_ any DD points in our problem set.
