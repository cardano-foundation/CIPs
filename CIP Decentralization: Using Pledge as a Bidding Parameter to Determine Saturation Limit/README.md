---
CIP: TBD  
Title: Decentralization: Using Pledge as a Bidding Parameter to Determine Saturation Limit  
Author: Jay Pseudonym Cappucino <jycappucino@gmail.com>
Comments-URI: https://forum.cardano.org/t/cip-stake-decentralization-using-pledge-as-a-bidding-parameter-to-determine-saturation-limit/95936  
Status: Draft  
Type: Process  
Created: 2022-02-28  
---
# **Abstract**
With the current saturation limit set at 68 M per pool and with 3119 pools (epoch 321), the current staking mechanism can accommodate a total stake of 212.1 B ADA (68M*3119). This amount of ADA is 543% in excess of the current circulating supply of 33B. Because of this substantial saturation limit, one can set up a few pools and offer lucrative rewards to capture a sizeable amount of stake (_e.g._, Binance APY is 17.7%). This leads to centralization and weakening of the ecosystem against Sybil attack. Here, we describe a mechanism that uses pledge as a stake-bidding parameter under a close system, _i.e._, the total saturation limit is always equal to the total ADA in circulation. The proposed mechanism ensures that no single entity can get away with excessive stake without putting up a hefty pledge and expending for computing and related infrastructure. This expense, likewise, confers the ecosystem a very high resistance against Sybil attack. For epoch 321, the cost to conduct a Sybil attack under this CIP is millions in plege and at least 1108 adversarial pools. We dare say that the cost to conduct a Sybil attack under the current protocol is 0 pledge in ADA and at least 177 adversarial pools only. This number of adversarial pools needed to attack the ecosystem under the current protocol does not change even if the total number of pools increases, unless the saturation limit (68 M) is decreased. These pools can be readily saturated using lucrative ISPOs and had been demonstrated during the Sundaeswap ISPO which involved 98 pools that were at or near saturation. We, therefore, posit that the this CIP is not only fair to all but also enhances decentralization and better security than the current protocol. 
  
  
# **Motivation**
This proposal attempts to solve the ongoing stake centralization by allocating pool saturation limit in proportion to pool pledge while at the same time guaranteeing that the total saturation limit is always equal to the circulating supply regardless of the number of pools and pledge status, _i.e._, whether the ecosystem is under-pledged, fully pledged, or over-pledged. The specification under this proposal is governed in a very dynamic manner using a set of well-defined equations which allows the staking mechanism to operate without the need for frequent network consensus.
  
    
# **Specification**
## **Nonmathematical Description**
Under this CIP, there is no barrier to entry to set up a pool, but there exists an **optimal pledge** which is used as a yardstick to determine pool saturation limit in proportion to pledge.
* Individual pool saturation limit decreases exponentially when **pool pledge < optimal pledge**.
* Individual pool saturation limit increases **only incrementally** when **pool pledge > optimal pledge**.
* The ecosystem is **under-pledged** when the **total saturation limit < circulating supply**. Under this condition, pools can over-pledge to “borrow” additional saturation limit unclaimed by the under-pledged pools. If there is still remaining saturation limit even after some pools have over-pledged, the unclaimed saturation limit will be distributed in accordance with Equation 1. However, the distributed unclaimed limit can still be claimed by any pool by continuing to pledge.
* The ecosystem is in **equilibrium** when the **total saturation limit = circulating supply**. Under this condition, only the under-pledged pools can continue to pledge to take back the borrowed saturation limit allocated for them. The over-pledge pools’ excess saturation limit, likewise, will continue to decrease until all excess had been returned. This and the proposition from the previous bullet point ensures that:
  - a **close system** is maintained, _i.e._, the total saturation limit is always equal to the total ADA in circulation regardless of the pledge status of the ecosystem, _i.e._, under-pledged, fully pledged, or over-pledged.
  - no single pool has a saturation limit that dwarfs other pools’ limits, encouraging decentralization.
* Optimal pledge decreases down to a minimum as the total number of pools increases but increases exponentially as the total number of pools decreases. This mechanism addresses Sybil attack:
  - optimal pledge becomes expensive when the total number of pools decreases, thereby increasing the expense to conduct a Sybil attack.
  - expense to conduct Sybil attack also increases as the total number of pools increases because although the optimal pledge is low, the attacker needs to setup a large number of pools in order to obtain 51% of delegated ADA.
  
## **Mathematical Description**
### _**Calculating Optimal Pledge**_
  
![equation1](https://drive.google.com/uc?export=view&id=1O_gmZ9LwpVV3xs2RVNqaXLh3um3zfFKs)

where **_p<sub>opt</sub>_** is the optimal pledge, **φ** is the amount of ADA in circulation (currently 33B), **_k_** is the total number of pools, and **_n_** is a variable that is determined via consensus to warrant an economically viable optimal pledge (**_p<sub>opt</sub>_**). Therefore, it appears that **_n_** is a variable that the community can vote for adjustment to increase or decrease **_p<sub>opt</sub>_**. In effect, it can be used to control the total number of pools (**_k_**) so that at some value **_n_**, the ecosystem gradually settles to some value **_k_** which the community thinks is the optimal value. It is very important that **_k_** is tightly controlled by **_n_**, and **_k_** should only increase according to some parameters, for example, with increasing user demand. So that even if **_k_** is large, all pools are still minting blocks because of high user demand.
  
If we set **_n_** =15,

**scenario 1** (very small number of pools):  
* **_k_** = 500,
* **_p<sub>opt</sub>_**  = ~ 774,763 ADA per pool

**scenario 2** (current number of pools):
* **_k_** = 3119 (epoch 321)
* **_p<sub>opt</sub>_**  = 47,205 ADA per pool

**scenario 3** (very large number of pools):  
* **_k_** = infinity
* **_p<sub>opt</sub>_**  = 27,440 ADA per pool  
  

**Conclusion**: **_p<sub>opt</sub>_** becomes cheaper as the total number of pools (**_k_**) increases, but more expensive as the total number of pools decreases. Setting **_n_** = 15 is only for illustration purposes. The Cardano scientists and engineers may want to place a more restrictive value of this parameter. For example, at **_n_** = 14 and **_k_** = 3119, **_p<sub>opt</sub>_** = 124k ADA.<br>
<br>
### **_Calculating Saturation Limit (α)_**

**case 1: _p<sub>a</sub> ≤ p<sub>opt</sub>_**  
![equation2](https://drive.google.com/uc?export=view&id=1vwM9i8voMM6AnNtlxIzuwu8mQj1ntgi5) 
  
where:  
**_p<sub>a</sub>_** = actual pool pledge  
**_p<sub>opt</sub>_** = optimal pledge  
**_α<sub>unc</sub>_**  = saturation limit left unclaimed even after some pools have over-pledged. This variable is defined in Equation 7.  
**_T<sub>a</sub>_** = pool accumulated time of operation (in days) counting from day 1 of operation (read explanation below).  
**_T<sub>tot</sub>_**= total accumulated time of operation (in days) of all nonover-pledging pools only (read explanation below).

The first term of Equation 2 allocates saturation limit based on pledge, and ensures that saturation limit increases or decreases exponentially with pledge.  
  
 It is ideal that **_α<sub>unc</sub>_** = 0, but if **_α<sub>unc</sub>_** > 0, the second term of Equation 2 ensures its distribution. The distributed **_α<sub>unc</sub>_**, however, can still be claimed by any pool by increasing its pledge.  
  
Distribution of **_α<sub>unc</sub>_** based, yet again, on pledge will further disadvantage those who are under-pledged. Therefore, we use accumulated time of operation,**_T<sub>a</sub>_**, as a parameter for the distribution of **_α<sub>unc</sub>_** which, in turn, ensures that the unclaimed saturation limit is distributed into pools that had been securing the ecosystem for the longest time. This manner of distribution prevents any would-be attacker, likely someone who had just registered a pool (or pools), from getting a significant portion of **_α<sub>unc</sub>_**. This mechanism is very important when the number of pools (**_k_**) is suddenly decreases to a very low number, making **_p<sub>opt</sub>_** very expensive and leading to significant under-pledging. Under this condition, pools that are under-pledged but had been in operation for a significant amount of time will be rewarded with a significant portion of **_α<sub>unc</sub>_**.

**Example 1**
* **_k_** = 3119 (epoch 321)
* **_p<sub>opt</sub>_** = 47,205 ADA (at **_n_** = 15, see calculation in the previous section)
* **_p<sub>a</sub>_** = 47,205 ADA
* **_α<sub>unc</sub>_**  = 0 (we will deal with nonzero values later)
* **_φ_** = 33B (current ADA in circulation)  
  
**_α_** = $\frac{33B}{3119}$ $e^{1 - 47,205/47,205}$ = $\frac{33B}{3119}$ = 10.6M  
  
**Conclusion**: Epoch 321 saturation limit for pools with at least 47,205 ADA in pledge is 10.6M (at **_n_** = 15). Setting the saturation limit to 10.6M would make some large pools to become oversaturated which will encourage delegators of these pools to move their stakes to small pools. It is very important that the number of pools (**_k_**) is properly controlled by the parameter **_n_** so that **_k_** remains optimal - _i.e._, even if **_k_** is large but optimal, no pool will be devoid of blocks.

**Example 2** (same variable values as in example 1 but lower **_p<sub>a</sub>_**).
* **_k_** = 3119 (epoch 321)
* **_p<sub>opt</sub>_** = 47,205 ADA
* **_p<sub>a</sub>_** = 30,000 ADA (for example)
* **_α<sub>unc</sub>_**  = 0 (we will deal with nonzero values later)
* **_φ_** = 33B (current ADA in circulation)  
  
**_α_** = $\frac{33B}{3119}$ $e^{1 - 47,205/30000}$ = 6.0 M  
  
**Conclusion**: 
Saturation limit decreases exponentially when **_p<sub>a</sub>_**<**_p<sub>opt</sub>_**, encouraging pools to achieve **_p<sub>opt</sub>_**. In an under-pledged ecosystem, pools can over-pledge to borrow saturation limit unclaimed by the under-pledged pools (see next case).<br>
<br>
  
**case 2: _p<sub>a</sub>_>_p<sub>opt</sub>_ (<span style="background-color: yellow; color: black">**the equation is quite complex so please bear with me**</span>)**.

![equation3](https://drive.google.com/uc?export=view&id=1852sEfSyWtUbJPzyJ5Nbp8P4nafsMLfx)  
where:  
![equation4](https://drive.google.com/uc?export=view&id=1JhEh0dmbdUaENq512t_ftz3HyI-EY0x6)  
  
* **_n_** = (**_p<sub>a</sub>_**\\**_p<sub>opt</sub>_**) is an integer division (example: 4\3 = 1).
* **$\frac{(x-|x|)}{2}$** returns 0 when x is positive, otherwise it returns the value of x.
* The first term in equation 3 (<span style="color: #0000FF">**blue**</span> text) is the guaranteed saturation limit since the pool exceeded **_p<sub>opt</sub>_**.
* The second term in equation 3 (<span style="color: #FF0000">**red**</span> + <span style="color: #008000">**green**</span> text) calculates saturation limit in excess of the guaranteed limit.
* The second factor of the second term in equation 3 (<span style="color: #008000">**green**</span> text), is the penalty factor that is accounted when the ecosystem is over-pledged. This factor decreases as under-pledge pools continue to increase their pledges. The decrease in the penalty factor, in turn, leads to a decrease in the excess saturation limit (<span style="color: #FF0000">**red**</span> text) of all over-pledged pools. Therefore, the penalty factor ensures that over-pledged pools "return" the borrowed saturation limit even without further intervention.  
  
  
**Example 1**: **ecosystem is not over-pledged**.
* **_p<sub>a</sub>_** = 110,000 ADA
* **_p<sub>opt</sub>_** = 47,205 ADA (**_n_** = 15)
* **Δ=1**  (Please accept this for now. Proof is provided later.)
* current circulation supply (**_φ_**) = 33B ADA
* current total number of pools (**_k_**, epoch 321) = 3119  
  
Because the system is not overpledged, Equation 3 is reduced to:  
  
![sample1](https://drive.google.com/uc?export=view&id=1cJg4uaHTGhaKv4pZvL5win3sTbOJeYoo)  
  
Plugging in the values,  
  
![sample2](https://drive.google.com/uc?export=view&id=1HUxMMwBfo8hAcHH8gAQn6rCboPvR3pkW)  
  
**Conclusion**: Since **_p<sub>a</sub>_**/**_p<sub>opt</sub>_** = $\frac{110000}{47205}$ = 2.33, the pool is guaranteed a saturation limit that is twice of $\frac{33B}{3119}$. The other additional limit $\frac{33B}{3119}$ $e^{-2.028}$ comes from the 0.33 fractional excess and is penalized exponentially.<br>
<br>

**Example 2**: **ecosystem is over-pledged**.  
Here, we will provide the derivation for the penalty factor (<span style="color: #008000">**Δ**</span>) and we will prove that it leads to a close system, _i.e._, the total saturation limit is always equal to the circulation supply no matter how under-pledged or over-pledged the ecosystem is. The penalty factor (<span style="color: #008000">**Δ**</span>) has the following characteristics:
* <span style="color: #008000">**Δ**</span> = 1, when the ecosystem is either under-pledged or at equilibrium. Under this condition, the excess saturation limit of over-pledged pools are unaffected. In essence, they are not yet "returning" any of the borrowed excess.
* <span style="color: #008000">**Δ**</span> ⟶ 0, when the ecosystem is over-pledged and under-pledged pools keep pledging. Under this condition, the excess saturation limit of over-pledged pools decreases and approaches zero. In essence, they are "returning" the borrowed excess.  
  
We first calculate the total saturation limit (**_α<sub>total</sub>_**) excluding:
  - <span style="background-color:yellow; color:black">saturation limit from over-pledges.</span>
  - <span style="background-color:yellow; color:black">unclaimed saturation limit (**_α<sub>unc</sub>_**, see second term in Equation 1).</span>
 
![Equation5](https://drive.google.com/uc?export=view&id=19VQyenWAntcKh8VavMpJxscc4scqT6_O)  
  
where **_p<sub>ai</sub>_** is the actual pledge of pool _i_. Since the total saturation limit (**_α<sub>total</sub>_**) can never exceed circulating supply (**_φ_**), the unclaimed saturation limit (**_α<sub>unc</sub>_**) is then calculated as follows:  
  
![Equation6](https://drive.google.com/uc?export=view&id=1JcYX5u499lXnhN9Ha7WSeN49d1WcSbtz)  
  
Realistically, some pools will be over-pledged and their total excess saturation limit (**_α<sub>ovp</sub>_**) may be added as follows:  
  
![Equation7](https://drive.google.com/uc?export=view&id=1Yj-_PGbl1WcWttDMX1acEex0e7ZFHWDM)  
  
Solving for **_α<sub>ovp</sub>_** we have,  
  
![Equation8](https://drive.google.com/uc?export=view&id=1NnoNPLEhp8cihYNvscXdXKP8lPikuADQ)  
  
Now, we have to remember that the second term in Equation 3 calculates the excess saturation limit of an over-pledged pool. Therefore, the total excess saturation limit (**_α<sub>ovp</sub>_**) can also be expressed as the sum of the second term of Equation 3 of all over-pledged pools and is given as follows:  
  
![Equation9](https://drive.google.com/uc?export=view&id=15FezfQXXCskq6rblQdauD1jJOEtCFSpH)  
  
where _j_ is any over-pledging pool. Plugging in Equation 9 into Equation 8, we have:  
  
![Equation10](https://drive.google.com/uc?export=view&id=15iwumKXAAhPy6t98uHZpiJk0CsltAWkd)  
  
Dividing both sides of Equation 10 by the right-hand side of Equation 9 and simplifying, we have:  
  
![Equation10](https://drive.google.com/uc?export=view&id=1lQYewlKuCotMs0QQ8I3xJcc4rfddyHk3)  
    
  
**Now, we will prove that Equation 11 guarantees a close system, _i.e._,**

<span style="color: #008000">**Δ**</span> = 1, when the ecosystem is either under-pledged or at equilibrium.  
<span style="color: #008000">**Δ**</span> ⟶ 0, when the ecosystem is over-pledged, and under-pledged pools continue to pledge.<br> 
<br>

**Case 1**: Ecosystem is under-pledged and over-pledged pools keep over-pledging to borrow additional saturation limit: the denominator is going to increase (<span style="color:red">red</span> arrow) while the numerator is going to increase by the same magnitude through a decrease (<span style="color: #0000FF">blue</span> arrow) in the unclaimed saturation limit (**_α<sub>unc</sub>_**) :  
    
  ![logic1](https://drive.google.com/uc?export=view&id=1-vvc_xUd8KSY5zmkR9xXP8ebZ_re3y6h)<br>
  <br>
    
  **Case 2**: Ecosystem is under-pledged and under-pledged pools keep pledging to claim the remaining saturation limit: the second term in the numerator is going to increase (<span style="color:red">red</span> arrow) while the third term is going to decrease by the same magnitude (<span style="color: #0000FF">blue</span> arrow):  
  
![logic2](https://drive.google.com/uc?export=view&id=1XK1F2zG1zyaLPn2sz8rrISKPFEI0_r8B)<br>
<br>
  
**Case 3**: Ecosystem is over-pledged (**_α<sub>unc</sub> = 0_**) and under-pledged pools keep pledging to take back the borrowed saturation limit: the total saturation limit of under-pledging pools increases (<span style="color:red">red</span> arrow) which causes a decrease in the numerator and, therefore, a decrease in the penalty factor (<span style="color: #0000FF">blue</span> arrow). The decrease in the penalty factor, in turn, causes a decrease in an over-pledged pool’s excess saturation limit (see Equation 3). In this scenario, an over-pledged pool is simply returning the “borrowed” excess.  
  
![logic2](https://drive.google.com/uc?export=view&id=182u2H0u72eDxSX04vjulPkeXWzjEdZmW)<br>
<br>
**Case 4**: Ecosystem is over-pledged (**_α<sub>unc</sub> = 0_**) and over-pledged pools keep over-pledging even when there’s no longer any saturation limit left for them to borrow: the denominator increases which causes the penalty factor to decrease. This, in turn, decreases the excess saturation limit of an over-pledge pool but leave the saturation limit of all under-pledged pools unaffected. This situation will cause the total saturation limit to go below the circulation supply (**_α<sub>total</sub> < φ_**) even if the ecosystem is over-pledged. This decrease should be sufficient to prevent over-pledged pools from continuing to over-pledge when **_α<sub>unc</sub> = 0_**. However, such weakness may possiby be exploited. Hence, when **_α<sub>unc</sub> = 0_**, any continuing pledge from an over-pledged pool should be rejected.  
  
![logic2](https://drive.google.com/uc?export=view&id=1j45ZEEhqwDDJoXcVxs4p1NqixegXGbmM)  
  
## **_Sybil Attack_**

We can calculate the total pledge to conduct a Sybil attack using the following equation:

![cost](https://drive.google.com/uc?export=view&id=1cqZJ7y9oBi1bA6rOYWzlseUAIyOH3avg)

We consider a scenario where some pools turn adversarial (**_k<sub>adversarial</sub>_**), and we can give the best scenario for the attackers by assuming that their pools are fully saturated. We can then plot the total pledge to conduct a Sybil attack as a function of the number of pools (**_k_**).

![costfuncpools](https://drive.google.com/uc?export=view&id=1lW93crB3YIFeOd4Y8iG0fxkmKHZKlrgr)

Notice the existence of a minimum in the plot at around 1600 pools. The total pledge to conduct a Sybil attack at this minimum is 45 M ADA in pledge (when **_n_** = 15) and at least 600 pools turning adversarial. The total pledge to conduct a Sybil attack increases as the number of pools either decreases or increases from this minimum. For epoch 321 at **_n_** = 15, the total pledge to conduct a Sybil attack is 52 M ADA in pledge and at least 1108 adversarial pools. We dare say that the total pledge to conduct a Sybil attack under the current protocol is 0 ADA in pledge and only 177 adversarial pools. This number of adversarial pools needed to attack the ecosystem under the current protocol does not change even if the total number of pools increases, unless the saturation limit (68 M) is decreased. These pools can easily get saturated by implementing lucrative (and maybe fake) ISPOs. This mechanism of stake centralization had already been demonstrated during the Sundaeswap ISPO which involved 98 pools that were at or near saturation.

## **_New Reward Structure_**
This CIP describes a protocol that attempts to enhance decentralization but is vastly different from the current protocol that uses a reward structure which is a function of stake, pledge, and saturation limit. The current reward structure has known issues (described below) that is actually antagonistic to decentralization. While the current protocol is formulated based on game theory, the would-be protocol from this CIP is not. The reason is because there are only two decisions that a pool need to choose: to pledge or not to pledge, and these decisions are not influenced by the decision of any other pool. Here, we propose a simple reward structure (in general terms) that is fair to all.

Currently, pool operators are paid a fixed cost of 340 ADA plus a margin per epoch. As long as a pool is minting even just a block in an epoch, the pool gets the fixed cost plus the margin of which both are subtracted from the total reward before the rest is distributed to the pool delegators. This mechanism appears to be not sustainable for small pools because the pool reward erodes the already meager delegators reward - _i.e._, a fixed cost of 340 ADA plus a margin is going to take a significant portion from the delegators reward since small pools mint fewer blocks.

Because we no longer need the current reward structure and it is expected that pools would have more or less the same delegation under this CIP, we propose that pool operators are paid for each block they minted. First, the **reward per block** is calculated by dividing the **reward pot (reserve + fees)** by the number of blocks in an epoch. Then, the reward for the pool operator for a block he minted is a FEW PERCENT of the **reward per block** which is further multiplied by the "fullness" of the minted block - _i.e.,_ if the minted block is only 80% filled, then the operator reward for that block is multiplied by 0.8. This multiplier has an effect of decreasing the operator reward from minting a block if the pool fails to completely fill the block to maximum capacity. In this manner, pools are encouraged to fill each block up to maximum capacity. Then, after deducting the total reward allocated to all operators, 20% of the **reward pot** is then allocated to the treasury and the rest are allocated to the delegators with the delegator reward capped at 0.616% per epoch (or 4.5% annually) regardless of which pool the delegators are staked, except if they are in oversaturated pools. If there remains an undistributed reward, this must be redirected to the treasury or returned to the reserve. The 4.5% reward declines exponentially for delegators in an oversaturated pool according to the following equation:

![reward](https://drive.google.com/uc?export=view&id=1B32FcDnIPnkl2aqMLTv-Ul2Sfc7QBsDy)<br>
where 
* **_r<sub>d</sub>_** is the delegator reward
* **_δ_** is the pool delegation
* **_α_** is the pool saturation limit
* the factor 10 in the exponent ensures that the reward drops by ~60% when pool delegation exceeds by 10% of the saturation limit.

The mechanism described above further enhance decentralization. In the current protocol, delegators are biased towards nearly saturated pools because these pools generate better rewards just because of how the reward is structured in the current protocol. This bias causes centralization of stake towards pools that are at near saturation. In this CIP, such bias is eliminated because it no longer matter which pool a delegator is staked - all delegators are getting the same reward of 4.5% unless they are staked in oversaturated pools. Finally, the delegator reward should increase as Cardano adoption increases. This increase in the reward is expected to encourage more and more delegation which will further enhance the security of the ecosystem. There may come an instance when Cardano is able to increase the delegator reward to a point when it becomes more profitable to delegate ADA than to use it as a medium of exchange. Thereby, reducing the amount of liquid ADA in the ecosystem. This mechanism is akin to coin burning but in a rather more meaningful manner. Under this instance, ADA is then used as a security coin, and the medium of exchange will shift to stable coins.

# **Rationale**
The steady centralization of stake concentrated to only a few MPOs primarily arises from the substantial saturation limit (68M) allocated for each pool. This large allocation allows moneyed MPOs to gain substantial delegation simply by setting up multiple pools and offering lucrative rewards. If left unchanged, the current state of affairs deters would-be SPOs from setting up pools and discourages current SPOs from continuing to operate because, for a significant number of them, the cost/reward is economically disadvantageous. This only leads to further centralization.

To mitigate the problem outlined above, we recognized that saturation limit needs to get decreased to some minimum that allow fair distribution of stake but avoids the potential risk of oversaturation. We may do this by allocating saturation limit based on pledge. This idea was first explored by Casey Gibson in his CIP which you may find <a href="https://github.com/cardano-foundation/CIPs/pull/163">here</a>. We found that there may be potential weaknesses to his ideas, but the same weaknesses are addressed in our proposal. These weaknesses are:
* **The Gibson proposal appears to be less effective at solving stake centralization.**  
To illustrate this argument, let's detemine how the Gibson proposal would affect a current MPO that has 60 pools and controls 2.8B ADA. First, we take note that this MPO has total control of the stakes delegated to it. The Gibson proposal, in its current form, allocates 100% of K (65M in stake) for every 500,000 ADA in pledge. Therefore, each pool from this MPO requires 65.5M to setup and get fully saturated. The number of pools that this MPO needs to retain all 2.8B stakes is just 43 pools ($\frac{2.8B}{65.5M}$), which is lower than the MPOs current number of pools (60 pools). The total pledge would amount to 21.5M (43*500,000) but this pledge is irrelevant for this MPO because it has total control of the stake delegated to it.

  The numbers from our proposal would be 282 pools and 12.8M in pledge to retain all 2.8B in stake at **_n_** = 15 and **_k_** = 3119 (epoch 321). The calculation is as follows  
  
  **_p<sub>opt</sub>_** = 33B*$e^{1-15*(1+erf(-100/(3119-60+pools)))}$  
  **_α_** = $\frac{33B}{3119-60+pools}$  
  **_pools_** = 2.8B/(**_α_**+**_p<sub>opt</sub>_**)
  
  We have three equations and three unknowns which resolves to **_pools_** = 282 and total pledge to 12.8M (282 pools * 45.5K in pledge). These numbers will increase as the number of pools increases.
  
* **The Gibson proposal may disenfranchise a significant portion of ADA in circulation from getting staked at low pool number.**  
Because the Gibson proposal does not gurantee that the total saturation limit of all pools is equal to the amount of ADA in circulation, there exists a significant risk of disenfranchising some portion of ADA in circulation. For example, if the number of pools abruptly drops to 500, all pools need to pledge at maximum (500,000 ADA to get 65M saturation limit) so that the ecosystem can achieve a total saturation limit that is approximately equal to the total ADA in circulation. However, all pools pledging at maximum is a very unlikely scenario, leaving some ADA disenfranchised. Risk of disenfranchisement exists even at the current number of pools. <span style="background-color:yellow; color:black">In contrast, the total saturation limit under our proposal is always equal to ADA in circulation regardless of the pledge status in the ecosystem.</span>
  

* **The Gibson proposal may be less effective in dealing with abrupt changes in the staking parameters.**  
Since the Gibson proposal rely on parameters that can only be changed when there is network consensus, such design is less robust against abrupt changes in the ecosystem, _e.g._, when there is a need for the number of validators to scale up with demand or when the number of pools declines abruptly due to extreme events. <span style="background-color:yellow; color:black">Our proposal scales up and down without further intervention because the protocol is governed by equations.</span>


Finally, **this CIP effectively increases the **_k<sub>effective</sub>_** parameter.**  
The **_k<sub>effective</sub>_** is a parameter that attempts to measure decentralization, and is defined by the equation shown as follows:
![k-effective](https://drive.google.com/uc?export=view&id=1A_foc_uYzkbSG3lJlcQt5F2IMh5T-e1z)<br>
The parameter **_k<sub>effective</sub>_** should increase as decentralization increases. However, recently it had plateaued between the values 40 to 43. The strategy described in this CIP effectively increases this parameter as the number of pools increases. This is due to the fact as the number of pools increases, the saturation limit (**_α_**) decreases. This decrease in the saturation limit, in turn, should decrease the ratio of group stake to total stake in Equation 14, which then leads to the increase of **_k<sub>effective</sub>_**.
# **Copyright**
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
  
