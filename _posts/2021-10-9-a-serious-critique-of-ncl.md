---
layout: post
title: "National Cyber League: A Serious Critique"
description: "A list of problems for Cyberskyline to resolve."
tags: [ctf]

---

## Introduction
I had heard about NCL through the grapevine at my high school in my sophomore year. I had played a variety of CTFs of many different formats, ranging from bog standard jeopardy style CTFs to DEFCON final's attack & defense.

However, this was my first experience with "corporate CTF", CTF designed by a "cybersecurity" company. Even though it stood in stark contrast from the CTFs organized by institutions, other CTF teams, and large tech giants, my team and I played NCL's Spring Season of 2021 where we competed in the team game together. 

Although we won first place, none of us will be returning for NCL for the time being.

## Challenge Quality

The challenge quality in NCL is nothing short of disappointing. Choosing what challenges that go into a CTF is **extremely** important, but, at best, is done haphazardly in NCL. 

### Challenges Design and Infrastructure

There were a ridiculous number of issues with a ridiculous number of challenges, ranging from a battle of GPUs for a category legitimately named "Password Cracking", to a web challenge with no solves because the vulnerability was so obscure no amount of guessing could lead to the solution.

Challenges requiring attacking a headless service were locked behind a incredibly slow terminal interface with no internet, causing many to base64 encode and paste binaries into the terminals to get their tools on the box. Boxes, when they break, can only be reset *3 times* before you're allowed no more resets and the challenge becomes unsolvable.

The crux of many challenges and the infrastructure they are supported on fail is, at best, frustrating to work with. However, a more concerning issue is the lack of lessons the challenges teach.

### Challenges Takeaways

Challenges need to teach the user something. CTF is all about learning to solve a challenge you know nothing about, rather than the traditional format of most competitions where you're expected to bring previously learned knowledge into the ring. However, what NCL teaches is close to useless in a overwhelming majority of challenges.

This becomes extremely apparent in the "Cryptography" category where players guess formats and and *especially* tools used to encode some secret data. I think having some data encoding challenges is cool! It teaches a lot about how information is communicated and utilized in computer science, something very important for beginners.

However, a majority of these "forensics" challenges boils down to downloading and trying as many tools as you could scrape together, where their difficulty was proportional to the obscurity of the tool.

Where's the problem solving? Isn't that what CTF is supposed to teach?

This was put on display during the 2021 Spring Season, where spamming random text embedding tools on images solved almost every forensics challenge. This is, blatantly, a *stupid* challenge format that teaches *nothing*, and it is insane that this composed such a enormous part of Cryptography. It doesn't help these same exact challenge formats are repeated over and over again with little to no variation in style, teaching nothing to returning users.

### Challenges are Guessy

The reoccurring theme with NCL challenges is that they are **guessy**. **Guessy**, is really, *really*, **really** bad for learning and frustrating for competitors, and it's why bigger CTFs have standards in place to catch challenges like this to ensure they don't show up in the final revision of the competition.

A document, known as the "[CTF Design Guidelines](https://bit.ly/ctf-design)", has been made by top players from top teams from around the world to separate *good* challenges and *bad* challenges, and it's shame almost every challenge in NCL falls into the latter.

A factor that adds to the ambiguity of a challenge is the lack of a certain correct answer for many questions. There isn't a flag format for many questions, which can be fine, but in the context of NCL, is an absolute nightmare to deal with. We'll talk about this when we discuss accuracy in NCL.

The CTFs I've organized have seen their fair share of bad challenges, but they almost always get tossed out before they hit the competitor. Sometimes that's not the case! And that's ok! It's not possible to catch every guessy challenge, but when an author does end up serving a guessy challenge to a competitor, it's important that steps are taken to fix the issue.

My team, redpwn, ran redpwnCTF 2021 this year and unfortunately a guessy challenge fell through the pipeline. Here's the author's response and apology:
> #### Lessons Learned
> At the end of the day, it deeply saddens me that I did not have the foresight to remove this challenge. As an experienced CTF player and challenge author, there is no excuse for something like this. The worst part is that bad challenges are the most memorable to most competitors, so people will remember me for this rather than the hours I spent debugging devnull or pickled-onions. Negativity aside, I do think there are some important lessons to be learned here.
>
> #### Do Not Rush Challenge Writing
> Every challenge, no matter how simple it may seem, MUST be thoroughly tested and reviewed by MANY people. I thought that this challenge was so easy that it didn't need to to be tested. Wrong! There are no exceptions. Plan ahead, and don't write challenges right before the CTF. **It NEVER works, and is a recipe for failure.**
>
> #### Consider the Competitors
> At every point in writing a challenge, authors MUST regularly stop and think, "if I were a competitor, would I be able to make this conclusion assuming I had the necessary experience?" If the answer is not a **RESOUNDING YES**, then the author should stop and reconsider what they are doing. Often, it is difficult or impossible for authors to judge their own challenges in this regard, so peer review is exceedingly important.
>
> #### Quality over Quantity
> This challenge was partially the result of me feeling like we didn't have enough challenges. **Having too few challenges is bad, but having low-quality challenges is even worse.** When given the choice, ALWAYS pick quality over quantity.

This is just the snippet of the entire writeup, but KFB goes into greater depth on how it was possible such a challenge ended up in the CTF with a more technical overview. This is in stark contrast to NCL's laissez faire approach with handling low quality challenges, and we'd hope to see greater time and care invested in the future.

Don't get me wrong! Some challenges in NCL are thought out and provide a wealth of insight on a certain topic in cybersecurity, however these challenges are so rare it's impossible to ignore the rest.

## Accuracy

NCL has a concept seldom seen elsewhere in the CTF space, called "accuracy". Incorrect submissions will dock competitors accuracy, which although not used as a primary scoring method, is a tie breaking standard. This makes it a critical statistic for teams looking to win first place, as more than one team will gain the maximum number of points possible and will need to rely on their accuracy to keep or take the #1 spot.

Unsurprisingly, this is really, *really*, bad idea.  

### Accuracy Inhibits Learning

The standard for a majority of CTFs is to use time as the primary tiebreaker, for good reason. The concept of accuracy, unfortunately, violates the first and third pillars in the feedback of learning. If you're unfamiliar with this concept, tylerni7 from Carnegie Mellon's CTF team [wrote a brilliant article on "why CTF"](https://pwning.net/2014/04/01/why-ctf/), describing why CTFs are so great at teaching the field of computer science and cybersecurity.

> If you read about the importance of feedback in learning, you’ll notice a few things CTFs do right: feedback is immediate, feedback is individual (both on a problem and team basis), and feedback isn’t final (if you get a flag wrong, try, try again).

Part of problem solving is utilizing verification oracles to make more educated decisions based off your previous ones! The ability to confirm or throw out your guesses is integral to understanding how systems work and how to break them, but NCL's accuracy score impedes on the development of that skill.

### Accuracy Inhibits Competition

Accuracy forces teams to second guess every answer. You don't know if you have the flag in your hands for many challenges thanks to their guessy nature, and confirming if you do may cost your team first place.

This affects far more than just competitive teams, but also teams on local leaderboards. At my school, we have a leaderboard where accuracy plays a role in rankings and is looked at by fellow students.

This leads to ridiculous guessing games where teams, like ours, have to ensure our answer is right before submission, often playing with ambiguity and educated guesses which may fall flat for reasons totally outside our control.

This just isn't a good learning environment, much less a good competitive one!

## $$$

I had talked to some friends about doing NCL, and the first question they asked was "are there any prizes?". An understandable question, as prizes can be a pretty great motivation to learn new and exciting things about cybersecurity. 

My immediate thought was to say yes, but I actually didn't know. I'd always assumed bigger CTFs have prizes. To my surprise, a scan of the website showed no trace of possible winnings.

That's alright. Not having prizes is *ok*, and a requirement to have prizes would shut down many smaller CTFs who cannot afford it. However, most people were hyped about googleCTF because of the insane prizes and trips, like competing on site in Elevat8 or Hackceler8 (you can watch our match [here](https://capturetheflag.withgoogle.com/hackceler8) 😉).

### The Role of a Company in CTF

Corporations can offer a whole lot more to CTF than independent teams can, as they have financial backing that many cannot match. This isn't limited to prizes, the infrastructure can be a whole lot faster and well designed, communicate with top CTF teams to ask them to write challenges or oversee the event, or just get the word out about the event.

Cyberskyline checks a lot of these boxes! I don't think its fair to assume NCL is a cash grab because they have registration fees or don't offer prizes, as Cyberskyline may not be familiar with what a real CTF looks like.

Companies getting into CTF is undoubtedly a good thing, as it allows CTF to become more accessible to new groups of people. Though, looking at NCL, the question becomes:

**What happened?**

## Conclusion

There is a clear disconnect between NCL and the expectations of a CTF. NCL fails to teach a quarter of what a high school run CTF like angstromCTF or hsCTF could. From what I understand, Cyberskyline didn't reach out to a single prominent CTF team, ending up adding bogus categories like password cracking and implemented scoring factors like accuracy.

A lot of inspiration can be taken from googleCTF. Working with players from top teams like LiveOverflow and Gynvael as well as consulting top teams like DragonSector allowed Google to provide an authentic CTF experience filled with learning opportunity and fantastic challenges.

I don't think NCL was rushed. The infrastructure, although many design decisions raise eyebrows (looking at you, integrated terminals), is clearly well made and much time has been invested in the event. It's important that NCL is given the benefit of the doubt, and that running a CTF is hard and mistakes are bound to happen. Rather, I hope NCL can grow from where it is right now.

As always, you can reach out to me at pepsipu@pepsipu.com for comments or concerns.

\- pepsipu