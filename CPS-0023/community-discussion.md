# Cardano Summit 2025 Day 0 Community Discussion

In Cardano Summiy 2025 Day 0 Governance Day, this topic has been widely discussed in 2 sessions:

## Governance Workshop

In morning session, we have a widespread discussion on CMAT surrounding 3 aspects:

1. Economics perspective - moderated by Shunsuke Murasaki
2. Governance perspective - moderated by Nicolas Cerny
3. Technical perspective - moderated by Hinson Wong

## Rountable

In the afternoon session, a roundtable amongst the moderators has been conducted to summarize the findings / community perspectives. In the technical perspective in governance workshop Samuel Leathers contributed significantly in different dimensions, so in the roundtable Hinson being the moderators and allow leaders in each perspective to summarize findings / perspectives from community.

### Short Summary

Overall no strong opposition at general to the CMAT itself, seems that very much each stakeholder group sees indeed strong benefit from the CMAT.

## 1. Economics

- **Hedging & stability** – Use multi-asset treasury to shift some ADA into stablecoins for predictable funding.
- **Yield & upside** – Over time hold yield-bearing RWAs and equity-like project tokens to grow the treasury.
- **Cardano-native focus** – Prioritise Cardano-native stablecoins and RWAs to keep value on-chain.
- **Phased risk** – Start with simple hedging, then consider higher-yield strategies and off-chain managers later.
- **Less ADA dependence** – Diversify away from sole ADA exposure to improve financial resilience.

## 2. Governance

- **Constitution must change** – ADA-only withdrawal rule needs amendment for multi-asset treasury.
- **Principles, not tickers** – Constitution should set guardrails, leaving asset selection to governance.
- **DReps choose assets** – New governance actions let DReps whitelist tokens for the treasury.
- **Extra load, cautious voters** – Multi-asset adds work, but DReps have shown conservative spending so far.
- **Managing token politics** – Clear objectives and criteria are needed to handle meme-token and lobbying pressure.

## 3. Technical

- **Multi-asset ledger support** – Extend rewards accounts and treasury to hold lists of native assets (CIP-159 style).
- **Ledger-level governance** – Keep treasury logic in the ledger’s epoch-based governance model, not in smart contracts.
- **Wallet opt-in** – Wallets let users opt into which tokens they can receive in reward accounts.
- **Governance-driven flows** – Donations and withdrawals of tokens are governed on-chain, with hooks to verify off-chain swaps.
- **Two-step rollout** – Use a feature-introducing hard fork, then an activation fork once guardrails are set.

### Full Recording

The full recording is avaiable at YouTube - <https://www.youtube.com/watch?v=b-Vimpso3qw>

### Full Transcript

Hinson: So yeah. So I think we could start now. So Did you give us the sign? Yeah, they gave. Yeah. So today we are very happy to have Marissa, Kisan and Sam and also Nicholas to be in this roundtable.

[02:00.0]
So we're mostly discussing a topic the Cardano Multi Assess Treasury. So before we start maybe you guys could give a quick self intro of yourself and yeah. How do you like about this topic in general? Yeah, I'll start with Masaki San.

[02:18.3]
Murasaki: My name is Murasaki, GM of the ecosystem Emago. Today I had a chance to facilitate in economic part of Multi Asset treasury discussion. I think the community was so passionate so we went through five questions but we ended up like maybe two and half of it.

[02:37.3]
In general I think I personally like really vibrant discussion and I think also the community is quite supportive of the initiative that you're putting together. Let's see. Sam.

Sam: Yeah, I'm Sam Leathers. I work at Input Output and then I'm also the chair of the product committee.

[02:56.3]
I was brought in here because I've had a lot of the discussions with the developers of the Cardano node, about how we would implement something like Multi Asset Treasury. And I brought some of those insights to the the group and shared them with people and I think we came with a good consensus of how to technically go about making Multi asset Treasury happen.

[03:19.7]
Nicholas: Yeah, my name is Nicholas. I'm the governance lead at the Cardano foundation and yestoday I was facilitating the governance discussions around the multi asset treasury and how that could look like. Personally I think it's a very necessary next evolution or next sort of improvement of Cardano's governance model and the treasury in general.

[03:43.3]
And what we did is we looked at it what and how do we need to change the governance rule set. So the let's say from the on chain perspective but also do we need to change the constitution? What language do we potentially need to include in the constitution.

[03:58.5]
So yeah it was, it was a really insightful discussion and what it showed to me is that usually people think it's a good idea it's just that they have questions about the details.

Hinson: So maybe also Before diving deep into the discussion I also give a little bit of the background information for the audience about the multi asset treasury.

[04:21.5]
So now we know that in our Cardano treasury we have a lot of adas locking but our ledger right now only support ADA ADA assets to be in our treasury so this multi asset treasury kind of topics is about how to make our ledger to enable to getting other assets as well like e.g.

[04:42.4]
stablecoins and other cardano native tokens. So for the background it's like this morning here in day zero Cardano summit we have a governance workshop discussing about this topic and we have separated the people into three groups like Sam and I was moderating the technical part of the discussion like if we are going to do it how the ledger could do it in several possible way and weighting each other slightly and then Murasaki san was moderating in the economic part of discussion like if we have it what's the implication in the kind of our Cardano economy in general and then Nicholas was moderating in the governance side of things to discuss our Is there any constitution change governance action change et cetera.

[05:27.2]
So here I actually want to pass the time back to you like Maybe to our audience to do a quick recap on in each of our breakout room what have we discussed this morning

Murasaki: starting with the workshop that I facilitated economic part of it I think we talked about the what's the objective of having multi asset treasury and we kind of talked about the short term objective and long term objective.

[05:59.3]
I think the notable discussion was short term objective is really talk about how. How we can secure annual budget because what really happened this year was every project had a different ADA USD conversion price so everyone has to kind of guess different ADA price at the time of getting funding from smart contract treasury.

[06:23.5]
So the idea is we can maybe convert what's necessary for the next year annual budget in stable so the use case or objective is really hedging some of the ADA in the treasury into stable tokens so that Cardano can secure almost like Runway to run Cardano for a year or a couple years specific years or amount of ADA to be secured in stable was to be discussed but the objective was let's hedge because it's not ideal to expose only to be ADA because ADA is a Bullasi asset like any other cryptocurrency.

[07:06.8]
So that was the short term objective but long term objective was quite vibrant discussion. Everyone had a quite you know interesting idea but the idea was almost like active treasury management. So get Cardano treasury yield itself.

[07:24.7]
So idea could be having some cryptocurrency. That was one of the idea got introduced by community members But I think majority of idea was let's consider Cardano native let's say real world asset or gold backed stable token.

[07:42.9]
So combining with some of the use cases and then having Cardano native asset yields itself and that yield coming back to the treasury. So I think those are the. I think wrap up the discussion in the economic session.

[07:58.9]
I see. So how about Sam like technical side?

Sam: Yeah so this is probably going to be a bit of a long one going off of what Murasaki said there. The purpose of it so the purpose is basically to take a native token, put it in the treasury and then allow our governance system to basically decide who those tokens go to when funds come up basically that are funded in that token's denomination.

[08:29.0]
Now a token can be anything. It can be a real world asset that basically represents gold that's locked in a vault. It can be night tokens that come from the Glacier Drop like if the midnight team decides they want to basically have Cardano handle their governance layer for them and they trust the Cardano community to make decisions on their behalf.

[08:54.4]
They could potentially lock a few hundred million a night in the treasury and basically say here through your Catalyst rounds, through your vc, things like draperyou and whatnot, figure out how you guys want to utilize these funds as well as through like open source development to continue to develop things for the Knight Protocol for instance.

[09:20.0]
So going off of that let's just take this back a little bit and talk about how this could actually work in practice. So the main reason why the treasury isn't a smart contract is because you can't calculate a vote of everyone in the system instantaneously which you have to do basically to validate a smart contract.

[09:46.6]
You can't validate a smart contract over say 48 hours. It basically freezes the system until that smart contract. And that one it's not going to freeze the system just other Things are going to get done before that smart contract executes and that one's going to go off on a fork that never happens.

[10:04.9]
So what it comes down to, and the whole reason sip1694 put the treasury into the ledger is because it pulses that governance period over the course of 48 hours at the beginning of every epoch, where an epoch is five days. So basically it's voting for the previous epoch's governance decision so what actions passed, who voted on what, and tallying all that to figure out what's going to be ratified and enacted, going forward.

[10:36.1]
So that's the reason why it's pretty much all or none. You either have a completely centralized solution where you trust a small set of actors to basically do this in an off chain thing and represent the people's opinion through like Hydra or something like that, for how they get that information, but you just have a centralized set of actors that basically make it happen or you have it as part of the full governance system at the ledger.

[11:06.4]
So the way this works to start with is you have this ADA in the ledger and then basically these treasury withdrawals take that ADA out of the ledger and they put it in the reward account. And this is where the rubber meets the road with multi asset.

[11:22.7]
So now basically you have to augment the reward account which there's a SIP for it already sip159 to be a multi asset list instead of just a single value. So that's the first piece. And once you do that it's a lot simpler to have a multi asset Treasury.

[11:42.3]
So you implement SIP159. Now you can have these wallets, you have some sort of whitelisting mechanism with where a user in their wallet basically says I'm willing to accept these tokens in my reward account. And then anyone can basically send them to their reward account or the treasury can send them to the reward account, those particular token types.

[12:03.7]
Which also means you have to increase the deposits for some wallets that basically have a list of like 100 tokens that they'll accept in the reward account type thing. So then going into the treasury, how do we get these into the treasury? So now we have the reward accounts.

[12:18.9]
We've added the ability to have multi assets in the Treasury. How does the community and this goes into your governance piece here, how do they decide what assets can go into the treasury? So we already have the donation mechanism where anyone can donate ada. They don't have to ask permission to donate to the Treasury.

[12:36.1]
So what we talked about basically was having a governance action that allows the community to basically whitelist an asset that can go into the Treasury. So now like the community can vote and we want to add knight, some wrapped BTC things, some gold, plethora of other different tokens that basically we want to see in the Treasury.

[13:01.5]
And then now anyone that holds those tokens, including the main token holders that created that token can basically take a segment of that value and then throw it in the treasury and then it just sits in the treasury until someone submits an action basically to take it out and do something with it.

[13:21.3]
Whether that be asset management like we were talking about to basically make sure we're getting a yield on our treasury or whether that be I have a project and I'm looking for funding and I'm only taking funding in gold. So there's all sorts of different options along that way that now people can do treasury withdrawals for any asset that lives in the treasury or we have a way to basically get those things into the Treasury.

[13:47.4]
And it uses all the same sip 1694 logic. So it's not as heavyweight of a change as some solutions. Even though it's at the ledger layer. We already have a lot of this stuff done already. It's just some slight augmentations.

[14:02.8]
So I'm not gonna put numbers on how long it would take but it wouldn't be that heavy of a lift once we have the community governance decide we want to do this. So with that over to you Nico.

Nicholas: Thanks Sam. Yeah, we had so many discussions around. First of all how do we need to change the Constitution. Because one thing I think we need to get straight the constitution needs to be amended because in one of the guardrails it says the treasury withdrawals have to be denominated in ada. Right. So there is no way around that. So there has to be a constitutional amendment which.

[14:36.4]
Right. It's a big hurdle. 75% of D reps need to approve it. And the Constitutional committee so that's something that must happen. And then Sam already touched upon it and as well Murasaki as well is how do we decide first of all what's.

[14:52.4]
What sort of assets do we allow to be in this multi asset treasury and through which means. Right. Do we encode that into the. Maybe even hard coded into the constitution? Probably not such a good idea because we had this discussion and one thing that usually we want to avoid in the Constitution is explicitly picking winners and losers.

[15:17.9]
Because it can happen that for whatever reason that is unknown, some of the listed assets fail or there is an issue. Smart contract risk is real, it exists. So that is something that should be avoided. And rather what should be in the Constitution is language around how we govern it outside of the Constitution itself.

[15:40.4]
So either on chain via the on chain governance model or potentially you could also think about a way that is off chain. Right? And this is where we had one of the biggest. I mean there's never consensus with these kind of topics.

[15:56.1]
People are usually against an aspect of it. And in our discussions what that was was this part about actively managed treasury, an active managed Treasury. And I think here what we had was just a misunderstanding or some sort of.

[16:14.9]
We tried to explain something with the wrong kind of words. Because an actively managed Treasury, I think what most people mean is an actively managed fund, right, where you take assets outside of the treasury, and then have that be managed via a professional fund manager, a group, a consortium that comes up and actually has the mission statement of generating yield for Cardano and would donate them back to the Cardano Treasury.

[16:41.7]
So very, not extremely similar but something that the defi liquidity stablecoin budget also wants to do. And one thing right, all the discussions I think in every group of ours sort of overlapped with each other and everything has to do with each other.

[16:59.7]
And one thing that I want to highlight is from James from Gimbal Labs, he brought that point up that let's keep it simple in the beginning, only allow for stablecoins because that actually really addresses the pain point we're trying to solve.

[17:15.0]
Because when we started this whole discussion it was about predictability. People that request funds from the treasury are exposed to the FX risk. So the price fluctuation and it creates uncertainty for them and for the governance system.

[17:33.6]
Because for example if you budget at 80 cents a dollar, the ADA price, then you have the, let's say in theory six epochs of a budget and then six epochs of a Treasury withdrawal, things can happen either I mean risk or things can go up or down.

[17:53.4]
And what we just thought is if, let's say the price goes down, right. We saw this in October 10th. What needs to happen then is you need to come back to the treasury, you need to do a top up proposal which would then put again more work on the D Rep shoulders on the CC on the entire governance model.

[18:13.8]
And this in theory could be avoided by having a multi asset treasury or in the beginning a stablecoin treasury in a way and one idea that I wanted actually to bounce off of you guys is right we have the rewards pods in Cardano where you have the transaction fees and the reserves and then the split is 8020 right.

[18:37.0]
In theory 80% goes to the stake pools and the delegators for the staking rewards and 20% goes to the Treasury. An idea that was brought up and I don't know how feasible it is but what if we automatically convert this 20% that goes to the treasury so you have 80% that stays in ADA and 20% that gets converted to Stablecoins.

[19:01.5]
I don't know if it's technically even feasible but that would then just. We would then start with a zero stablecoin treasury but it would slowly grow over time.

Sam: Yeah that's hard because you need some sort of outside Oracle to basically watch prices to do the conversion and you need to have a buyer for it to basically do the conversion when it goes in you're much better off just having the ADA go into the treasury and then having a Treasury proposal for someone to basically swap ADA for stablecoin and the treasury which we could do if while we're doing this change to how we're handling the governance of the Treasury.

[19:46.2]
We could potentially add some Plutus primitives that basically can validate an action actually happened. And then like pre lock the funds you want to put in the treasury and if this action passes before its action deadline anyone can execute the smart contract to basically donate all that stuff to the treasury and if that action fails the original holder basically could claim those tokens back out.

[20:16.2]
Hinson: Interesting, interesting. Actually Nicholas has just touched on a very interesting point because right now in Cardano we have seen for example the Defi liquidity proposal they want to do some sort of off chain treasury management but now we are discussing this topic as Cardano Multi Assets treasury on chain so I gotta maybe bring this question to you guys to talk about slightly how active we actually want to manage our on chain treasury and in what way like do we actually do something like Sam was just mentioned do a treasury withdrawal to convert into stables or we want some professional funds to manage it.

[20:59.0]
What is the role of the on chain treasury actually if we are holding other assets.

[21:08.1]
Murasaki: So the, the economic discussion has very extensive discussion around this so the starting from like let's just focus on ada, Nativasit but we also I think need to acknowledge the fact probably the sort of web two or traditional finance private credit product or RWA or even you know financial product is more battle tested proven yielding sustainably so it really depends on the long term active management objective but whether we should place some sort of target yield in percentage and probably that's going to determine the risk and reward.

[21:58.9]
I think the conclusion was that probably in the first couple years we should be focusing on as Nicholas said focus on very simple use case like hedging and as we see more stability in the governance and treasury system that means Cardano can spend more in an efficient fashion because we can predict the amount of USD dollar figure that we can pay out to the project because at the end of the day all the projects including us we are paid in fiat currency to pay employees and or servers and so on and so forth.

[22:34.9]
So in a couple of years we probably going to see more project because of sustainability of governance and treasury that's theoretically bring more project the RWA protocols and products coming to Cardano then we can see more on sort of like semi on chain treasury management but maybe extension of that is if you want to see more target basis outcome like we want to see what 7 to 8% of APY then we probably need to look for sort of kind of off chain thing because I think on chain as of today Cardano is sort of limited but if you can just withdraw some of the ADA and convert it to USD and then identify some of the credible like fund managers then we might be able to achieve high percentage of apy.

[23:28.8]
Hinson: I see so for the economics breakout room so kind of the people here we identify you probably want to have some sort of stablecoins and RWA in our multi asset treasuries. So for technical and governance point of view do you think we should actually keep this on chain or we trust someone to do it off chain for us.

[23:51.5]
Sam: Oh so I mean the actual conversion is going to be off chain. You're going to have to trust someone to do the conversion. Either they take the ADA out and they convert it and they and then they put that one back in and you trust them to do it or they have enough liquidity themselves that they can mint that coin ahead of time and contingently put it in if they get the ADA out.

[24:16.6]
Both of those are options you could do with this design. However I understand what the Economic people are saying about let's keep this sustainable. Where I think this is the killer feature, is this basically allows, projects that are being built within the ecosystem to basically give a commitment to the ecosystem that, hey, I'm providing you some equity in what I'm doing.

[24:48.5]
Whether that be like with the midnight glacier drop right now that happened and the scavenger mine, so everyone's getting all these night tokens. If the Midnight foundation, decides that, hey, we trust the Cardano community to help us manage, the Knight we want to hand out to projects to get, them to build, then, they could basically donate a significant portion in and people could vote on proposals coming out for Knight for like a Knight Fund, or something like Catalyst or something like Draper U and whatnot.

[25:21.2]
So, you, you get that there's also like, if there's a project that basically, or a company founding that basically is starting and the community is very gung ho about this potential company, the company could actually sell equity to the treasury, as a coin, if they have a coin representing the equity of the company, where basically that equity is now in the treasury.

[25:47.5]
And the community can basically choose what to do with that equity in the future. So say that company goes from like a dollar, 500 valuation to a $100 million valuation, the Cardano community could then decide, hey, we want to pull some of those tokens out and we want to sell them and get more ADA back in our treasury or we want to get a stable in our treasury and whatnot.

[26:10.6]
So I mean, I think there's a lot of value to the stablecoin piece, but I really think we should leave it up to the D reps to decide what tokens go in. And that's why I like the flexible solution of basically creating a governance action to basically vote on a token that is being submitted to the treasury and then once it's voted on, anyone can donate it.

[26:30.4]
Nicholas: Yeah, I think this is also really tying into this whole. I don't know who mentioned it today, but I think, I don't want to attribute it to the wrong person, but they said that D reps are way more conservative than they anticipate them. So there's way, way less, funds flowing out of the, let's say Treasury.

[26:49.2]
Right. We have an exchange limit in 2025 of 350 million ADA and currently only, I mean it's still a lot. 272 million ADA was withdrawn. Right. But which still lives around 75 a bit more million ADA left in this net change limit.

[27:06.9]
So I think the best way forward also from a governance perspective is enable the technology right. Introduce the changes into the node, into the Yeah into the system enabling this capability of a multi asset treasury and then as Sam said have it start with a blank sheet right.

[27:29.6]
Don't include anything immediately in there because that introduces bias in a way and we don't want to pick winners and losers. The governance system will take care of that themselves I would say so enable that and I mean if I have a crystal ball I would probably not sit here but I assume that probably most of the D reps on Cardano would want to start conservatively start with stable coins, I don't know right.

[27:56.1]
Bitcoin, some gold, I don't know right Conservatively and then it can grow right and if, and now I'm speculating and I don't really want to do that but as Sam said if then a project comes along and they say hey include my asset into the treasury and I will do, I don't know X, Y and Z and you get that much equity in my or that much of my token.

[28:18.4]
I mean that's also a way for the Cardano treasury to become more self sustainable.

Hinson: Yeah, yeah. So we have a quite of a bullish kind of atmosphere today I think in all of the breakout rooms although I'm also kind of supporting this thing so that's why I'm driving the standard.

[28:38.0]
But actually there's one comment that I hear just around our community which is quite concerning about these things so I also want to brought into here maybe to we have a more all rounder discussion of the thing. The concern is namely right now we are still in a kind of a chaotic situation about our governance like if we introduce the possibility to having other tokens in the treasury, perhaps a lot of different projects, perhaps Hosky or Snag will fight into getting the whitelisting into the multi asset treasury and we may be further deviating our focus into solving the problem that we want to solve.

[29:19.9]
So in terms of this concern do any one of you have any idea whether this, do you have any mitigation on this or. Yeah. How do you think about this from a community point of view?

Sam: First off I'm going to make a little bit of a joke around here so I think if someone submitted a action to add Hosky to the Treasury, Hosky would probably be the first one to basically vote no But no I mean that's why you give it to the D rats, that's why you don't have any authoritative body decide how we're going to do this.

[29:58.8]
And I mean whether you like snack or not, I mean they're part of the community, they have a following if they can get. And that's the other thing that you're on the governance side you need to figure out, not you but like the people working on the governance, the people running these workshops need to figure out when we get to the point of this being implemented, what threshold do we want for a whitelist?

[30:21.9]
Is 51% enough for a whitelist is 67. My opinion, probably a simple majority is fine for a whitelist because basically the only point of the white list is to keep garbage tokens out of the treasury that people don't want to manage.

[30:39.0]
But yeah, I mean it's up to the community so the community can decide. And if they lose a huge project like SNEC because they vote no on allowing it to be in the treasury and SNEC takes their ball and goes home, I mean that's going to be sad to the community, but it's what the community decided.

[30:57.9]
So I mean that's why I say leave it up to the D reps, let them make the decisions.

Nicholas: Yeah, I absolutely agree with that. I mean one thing though, right, and as you mentioned Tinsen, about having a nuanced discussion, a balanced discussion is the thing.

[31:15.4]
If we now introduce another governance action type, there's more governance actions, more things to vote on, more work for the D reps, for the CC in theory. Right. So I think it needs to be done in a. Yeah, I mean in a very well thought out way.

[31:35.4]
And if we change, I mean this is going to be a big change to Cardano if we introduce that. Right. And I mean there is a problem, so there is a pain that is being solved or a pain that is being addressed. So from that side I think, we could sort of the cost benefit analysis is in favor in my opinion of implementing that.

[31:59.6]
But I can see why people would say no, it's too complicated, let's just do it off chain. We entrust a very competent fund manager, very competent company to just, let's say get 200 million ADA, actively manage it and send funds back to the treasury.

[32:18.4]
But for me it's not an end and, or thing or. Yeah, but I think we can pursue both things at the same time.

Hinson: Yeah, I see. Anything to add from Saki

Murasaki: so economic the discussion really talked about this and I think that's why the agreement on a definition is very important.

[32:44.1]
We really try to focus on economic parameter but oftentimes it's was to governance and technical I'm not sure how we're going to agree on this whether it's going to be a constitution level or some sort of governance action but like what are we going to focus on?

[33:01.1]
Like what's the purpose of this treasury management whether it's passive or active and then that actually deliver the outcome or the methodology or the type of token to be whitelisted. So I think that is really up to D Rep in a community but the first and foremost like we need to agree on the definition then that naturally that leads the way whether we should be focusing on state war or some other more speculative asset.

[33:34.1]
So that was I think the conclusion and the view from the Participants from the economic discussion

Nicholas: and if I could just add one thing to that. Right. And I completely agree with Murasaki and Sam who say that it's the D Rep who make the decisions. I think what like we as a group and let's say proposers in general of such big changes need to do is provide the D reps with enough information to make an educated decision not just on what assets to add to the treasury but also when it comes to the hard fork where this change is being introduced.

[34:08.1]
Right. Because I think it's sometimes unfair if D reps only hear from the proposers who of course they are incentivized to sell it, sell the hell out of the proposal. Maybe don't talk about the how do you say that?

[34:23.8]
The things that could go wrong or the What's the opposite of benefits? The. Yeah, the cost. The cost. Exactly. And so I think this is something where we just need to be really transparent because there are potentially some negative consequences for D reps more work another thing that they need to keep an eye on the Constitutional Committee would then maybe have to also track the asset amounts of whatever is in the treasury besides ada.

[35:02.8]
So what about the net change limit? Do we set the net change limit? Net change limit for these assets Is it only. Do we look at the net change limit now only from a USD amount or yen or Euro? There's many implications to that.

[35:19.0]
So I think we need to have more discussions also with experts, get as many people in as we can and then present the whole thing to the drips.

Hinson: Yeah. So I think today says we about time to wrap the discussion before we actually close any other final thoughts

Sam: I think we need to talk about next steps a little bit and how we actually get there from.

[35:41.7]
So like we had some good discussions today but how do we actually get this into the ledger? Did you want to talk a little bit about what you're proposing right now for that process?

Hinson: Yeah. So maybe just for record I update a little bit on the status this thing.

[35:57.0]
Actually we started this discussion since 12 months ago and right now we have a draft cardano problem statement. So after today I taking all the feedback and input I will do a final revisions and I will turn it into an open pull request and from there probably I will start to draft the skeleton of the CIP and probably from there we welcome all community member whoever found this meaningful to do to work on it together.

[36:26.2]
And then from there with the draft we will submit info actions probably just to get a sense check on the community whether we want to do it and then from there we will follow probably by changing the constitution and then the huff for initiation as well.

[36:43.2]
Yeah this is roughly the plan but there are a lot of things to do like both in the socializing element of it and technical side of it and governor discussion side at 51 or 67 there are a lot of discussion to be followed.

[36:59.2]
Sam: So for the rollout once we get the thing developed and how we get it on chain, I think we've already established a good way of handling that with how we rolled out sip 1694 where we basically do two hard forks.

[37:15.7]
The first hard fork introduces the feature and basically but has it deactivated but then gives a window for the constitution to be updated with the guardrails, gives a window for the protocol parameters to be set where people want them to be set, gives a window for any parameters that need to change in the Plutus cost model, things like that.

[37:38.9]
So basically you have hard fork one, then you have a little window for all these actions that need to happen. And then once all these actions happen then you do an intra era hard fork, that basically takes that feature that we had and enables it permanently for people.

[37:54.3]
Then that also gives you some time in that window to make some slight variations in the design. Not the design but in the implementation if you have to. Like we did with SIP 1694 where we made some fixes and whatnot. But ideally you can support doing both of those hard forks in the same code base without having to go back and make changes like that.

[38:19.4]
Hinson: Roughly one more minute and your final sentence from Masaki and Nicholas.

Murasaki: More we talk like we found more things to be defined so I think you know it's really an endless discussion but I think the short term objective it's probably beneficial for Cardano to you know just embark on the first step as soon as possible because rely on ADA single handedly is not a very unique situation with this amount of asset side so we cannot go fast but at the same time I think it's probably the best interest of the community and Cardano to move on as soon as possible.

[39:10.0]
Nicholas:One thing that I think is super important and I'll try to be as fast as I can is we can still experiment with the off chain fund management currently Right. We have the stablecoin DeFi liquidity proposal. Who wants to request 50 million ADA and then we'll see are they able to actually generate yield and contribute back to the treasury?

[39:30.9]
Because you can already donate to the treasury. That's possible and I think right now we should not just stop and do nothing until that two hard forks potentially get implemented because that probably takes a lot of time but we can already start with small experiments right now and yeah that's what I think.

[39:49.0]
Sam: Yeah, absolutely. Sounds good. That's kind of the trusting a centralized source approach that I was talking about. It's kind of all or nothing. Well the nothing is the centralized source. It's like we're going to take this money out, experiment with this. But yeah, thank you very much for putting this together and bringing us all together here.

[40:08.7]
Thank you. That's great. Yeah, thank you. Yeah, always. It's good. Absolutely. Thank you.
