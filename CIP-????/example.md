# **🧮 Example Scenario**

A **Protocol Parameter Update** governance action is submitted.  
 This action requires **CC \+ DRep \+ SPO participation**.

**Participation:**

* **CC:** 7 members voted

* **DReps:** 357 voted

* **SPOs:** 254 voted

**Deposit:**  
 `govDeposit = 100,000 ada`

**Assumed Compensation Parameters:**

* `ccCompensationRate = 0.03` (3%)

* `drepCompensationRate = 0.11` (11%)

* `spoCompensationRate = 0.11` (11%)

* **TOTAL \= 25%** (the max allowed by your guardrail)

Hybrid distribution:

* `dRepWeightFactor = 0.50`

* `spoWeightFactor = 0.50`


# **📌 STEP 1 — Ledger splits the deposit**

**Deposit:** 100,000 ada  
 **Total compensation \= 25%**

→ **25,000 ada becomes the Compensation Pot**  
 The remaining **75,000 ada** is refundable regardless  if the proposal succeeds, fails or expires.

**Compensation pot breakdown:**

| Group | Rate | Amount |
| ----- | ----- | ----- |
| CC | 3% | **3,000 ada** |
| DReps | 11% | **11,000 ada** |
| SPOs | 11% | **11,000 ada** |
| **Total** | **25%** | **25,000 ada** |

✔ The ledger has now created three internal compensation pools.


# **📌 STEP 2 — CC compensation distribution**

**CC Compensation Pool:** 3,000 ada  
 **7 CC members voted.**

CC uses **equal-share only** (per Article VII, § 8):

→ **3,000 / 7 \= 428.571428 ada per CC member**

Ledger sends:

* CC member 1: 428.571428 ada

* CC member 2: 428.571428 ada

* CC member 3: 428.571428 ada

* CC member 4: 428.571428 ada

* CC member 5: 428.571428 ada

* CC member 6: 428.571428 ada

* CC member 7: 428.571428 ada

(Any CC member who did not vote receives **0**.)


# **📌 STEP 3 — DRep compensation distribution**

**DRep Compensation Pool:** 11,000 ada

DRep distribution uses your **hybrid model**:

* **50% equal-share \= 5,500 ada**

* **50% stake-weighted \= 5,500 ada**

### **A. Equal-share portion**

357 participating DReps:

→ **5,500 / 357 \= 15.4109 ada per DRep**

Every voting DRep receives **15.4109 ada**.

### **B. Stake-weighted portion**

Ledger uses:

* the DRep governance stake snapshot

* only stake represented by **voting DReps**

* proportional distribution

**Example (hypothetical):**  
 If DRep A represents **1.5%** of the total DRep voting stake:

→ 1.5% of 5,500 \= **82.5 ada**

So DRep A receives:

* **15.4109 ada** (equal-share)

* **82.5 ada** (weighted)

* **97.9109 ada total**

Non-voting DReps receive **0**.

# **📌 STEP 4 — SPO compensation distribution**

**SPO Compensation Pool:** 11,000 ada  
 Hybrid model identical to DReps:

* **50% equal-share \= 5,500 ada**

* **50% stake-weighted \= 5,500 ada**

### **A. Equal-share portion**

254 voting SPOs:

→ **5,500 / 254 \= 21.6535 ada per SPO**

### **B. Stake-weighted portion**

Uses **block-producing active stake** (not delegated stake).

**Example:**  
 If SPO X has **2%** of total block-producing stake among participating pools:

→ 2% of 5,500 \= **110 ada**

So SPO X receives:

* **21.6535 ada** (equal-share)

* **110 ada** (weighted)

* **131.6535 ada total**

Non-voting SPOs receive **0**.


# **📌 STEP 5 — What happens to the rest of the deposit?**

* The proposer receives back **75,000 ada**

* Ledger distributes **25,000 ada** as compensation (already paid)
The compensation portion (**25,000 ada**) is **never refunded**, by design.


# **📌 SUMMARY TABLE**

| Group | Voters | Pool | Distribution Model | Payout Per Entity |
| ----- | ----- | ----- | ----- | ----- |
| **CC** | 7 | 3,000 ada | 100% equal-share | **428.5714 each** |
| **DReps** | 357 | 11,000 ada | 50/50 hybrid | **15.4109 \+ stake-share** |
| **SPOs** | 254 | 11,000 ada | 50/50 hybrid | **21.6535 \+ stake-share** |


* No smart contracts

* No manual triggers

* No multi-sig

* No treasury action

* No external scripts

This compensation system is fully determined at **protocol level**, just like staking rewards.
