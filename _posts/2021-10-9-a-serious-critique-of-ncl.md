---
layout: post
title: "National Cyber League: A Serious Critique"
description: "95 Theses, NCL Edition. A list of problems for Cyberskyline to resolve."
tags: [ctf]

---

## Introduction
I had heard about NCL through the grapevine at my high school in my sophomore year. I had played a variety of CTFs of many different formats, ranging from bog standard jeopardy style CTFs to DEFCON final's attack & defense. However, this was my first experience with "corporate CTF", CTF designed by a "cybersecurity" company. Although it stood in stark contrast from the CTFs organized by institutions, other CTF teams, and large tech giants, my team and I played NCL's Spring Season of 2021 where we competed in the team game together. Although we won first place, none of us will be returning for NCL for the time being.

## Challenge Quality
The challenge quality in NCL is nothing short of disappointing. Choosing what challenges that go into a CTF is **extremely** important, but, at best, is done haphazardly in NCL. 

This becomes extremely apparent in the "Cryptography" category where players guess formats and and *especially* tools used to encode some secret data. I think having some data encoding challenges is cool! It teaches a lot about how information is communicated and utilized in computer science. However, a majority of these "forensics" challenges boils down to downloading and trying as many tools as you could scrape together, where their difficulty is proportional to the obscurity of the tool.

This was put on display during the 2021 Spring Season, where spamming random text embedding tools solved almost every forensics challenge. This is, blatantly, a *stupid* challenge format that teaches *nothing*, and it is insane that this composed such a enormous part of Cryptography. It doesn't help these same exact challenge formats are repeated over and over again with little to no variation in style, teaching nothing to returning users.

There were a ridiculous number of issues with a ridiculous number of challenges, ranging from a battle of GPUs for a category legitimately named "Password Cracking", to a web challenge with no solves because the vulnerability was so obscure no amount of guessing could lead to the solution. Challenges requiring attacking a headless service were locked behind a incredibly slow terminal interface with no internet, causing many to base64 encode and paste binaries into the terminals to get their tools on the box. 

The reoccurring theme with NCL challenges is that they are **guessy**. **Guessy**, is really, *really*, **really** bad for learning and frustrating for competitors, and it's why bigger CTFs have standards in place to catch challenges like this to ensure they don't show up in the final revision of the competition. A document, known as the "(CTF Design Guidelines)[https://bit.ly/ctf-design]", has been made by top players from top teams from around the world to separate *good* challenges and *bad* challenges, and it's shame almost every challenge in NCL falls into the latter. 

The CTFs I've organized have seen their fair share of bad challenges, but they almost always get tossed out before they hit the competitor. Sometimes that's not the case! And that's ok! It's not possible to catch every guessy challenge, but when an author does end up serving a guessy challenge to a competitor, it's important that steps are taken to fix the issue.

My team, redpwn, ran redpwnCTF 2021 this year and unfortunately a guessy challenge fell through the pipeline. Here's the author's response and apology:
> # Lessons Learned
> At the end of the day, it deeply saddens me that I did not have the foresight to remove this challenge. As an experienced CTF player and challenge author, there is no excuse for something like this. The worst part is that bad challenges are the most memorable to most competitors, so people will remember me for this rather than the hours I spent debugging devnull or pickled-onions. Negativity aside, I do think there are some important lessons to be learned here.
>
> ## Do Not Rush Challenge Writing
> Every challenge, no matter how simple it may seem, MUST be thoroughly tested and reviewed by MANY people. I thought that this challenge was so easy that it didn't need to to be tested. Wrong! There are no exceptions. Plan ahead, and don't write challenges right before the CTF. **It NEVER works, and is a recipe for failure.**
>
> ## Consider the Competitors
> At every point in writing a challenge, authors MUST regularly stop and think, "if I were a competitor, would I be able to make this conclusion assuming I had the necessary experience?" If the answer is not a **RESOUNDING YES**, then the author should stop and reconsider what they are doing. Often, it is difficult or impossible for authors to judge their own challenges in this regard, so peer review is exceedingly important.
>
> ## Quality over Quantity
> This challenge was partially the result of me feeling like we didn't have enough challenges. **Having too few challenges is bad, but having low-quality challenges is even worse.** When given the choice, ALWAYS pick quality over quantity.

This is just the snippet of the entire writeup, but KFB goes into greater depth on how it was possible such a challenge ended up in the CTF with a more technical overview. This is in stark contrast to NCL's laissez faire approach with handling low quality challenges, and we'd hope to see greater time and care invested in the future.

## Accuracy
NCL has a concept seldom seen elsewhere in the CTF space, called "accuracy". Incorrect submissions will dock competitors accuracy, which although not used as a primary scoring method, is a tie breaking standard. This makes it a critical statistic for teams looking to win first place, as more than one team will gain the maximum number of points possible and will need to rely on their accuracy to keep or take the #1 spot. Unsurprisingly, this is really, *really*, bad idea.  

The standard for a majority of CTFs is to use time as the primary tiebreaker, for good reason. The concept of accuracy, unfortunately, violates the first and third pillars in the feedback of learning. If you're unfamiliar with this concept, tylerni7 from Carnegie Mellon's CTF team [wrote a brilliant article on "why CTF"](https://pwning.net/2014/04/01/why-ctf/), describing why CTFs are so great at teaching the field of computer science and cybersecurity.
> If you read about the importance of feedback in learning, you’ll notice a few things CTFs do right: feedback is immediate, feedback is individual (both on a problem and team basis), and feedback isn’t final (if you get a flag wrong, try, try again).

Accuracy forces teams to second guess every answer. You don't know if you have the flag in your hands for many challenges thanks to their guessy nature, and confirming if you do may cost your team first place. This leads to ridiculous guessing games where teams, like ours, have to ensure our answer is right before submission, often playing with ambiguity and educated guesses which may fall flat for reasons totally outside our control. This just isn't a good learning environment, much less a good competitive one! Feedback, as a result, cannot be immediate. On the same token, there are permanent consequences for making mistakes, and as a result, feedback is final. 