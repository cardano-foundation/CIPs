from copy import deepcopy
from dataclasses import dataclass
import random

# All undisputable input parameters go here.
UNIT_SIZE = 1_000_000
MAX_UNIT_SUPPLY = 45_000_000_000 * UNIT_SIZE
INITIAL_UNIT_SUPPLY = 31_112_484_646 * UNIT_SIZE # https://cardano.org/genesis/
INITIAL_UNIT_DIST = 25_927_070_538 * UNIT_SIZE
STAKING_REWARD_PERCENT = 0.3 # https://www.essentialcardano.io/faq/where-do-staking-rewards-come-from
STAKING_REWARD_PAY_DAY = 5
GENESIS_YEAR = 2017
STAKING_YEAR = 2020 # https://forum.cardano.org/t/the-shelley-hard-fork-all-you-need-to-know/36553
STAKING_EPOCH = 213 # https://cexplorer.io/epoch
# Accumulative. n+1 includes count of n+0
INITIAL_DIST_USERS: int = [
    4,
    31,
    102,
    238,
    480,
    895,
    1529,
    2603,
    4837,
    9912
]
# Accumulative. n+1 includes count of n+0
INITIAL_DIST_UNITS_PERCENT: int = [
    0.04,
    0.31,
    1.03,
    2.40,
    4.84,
    9.03,
    15.43,
    26.26,
    48.80,
    100.00
]
assert(len(INITIAL_DIST_USERS) == len(INITIAL_DIST_UNITS_PERCENT))


@dataclass
class UserBucket:
    users: int
    units: int


class Simulator:
    user_buckets: list[UserBucket] = []
    total_users = 0
    total_units = 0

    def __init__(self):
        self.user_buckets: list[UserBucket] = []
        self.total_users = 0
        self.total_units = 0

        for i in range(len(INITIAL_DIST_USERS)):
            self.user_buckets.append(UserBucket(users=0, units=0))
            if i == 0:
                self.user_buckets[i].users = INITIAL_DIST_USERS[i]
                self.user_buckets[i].units = INITIAL_DIST_UNITS_PERCENT[i] / 100 * INITIAL_UNIT_DIST
            else:
                self.user_buckets[i].users = INITIAL_DIST_USERS[i] - INITIAL_DIST_USERS[i-1]
                self.user_buckets[i].units = (INITIAL_DIST_UNITS_PERCENT[i] - INITIAL_DIST_UNITS_PERCENT[i-1]) / 100 * INITIAL_UNIT_DIST

            self.total_users += self.user_buckets[i].users
            self.total_units += self.user_buckets[i].units

        assert(self.total_units == INITIAL_UNIT_DIST)

        # Units to integer
        for i in range(len(self.user_buckets)):
            self.user_buckets[i].units = int(self.user_buckets[i].units)


    # Returns year when simulation has stopped.
    def Run(self, min_acceptable_unit_size: int) -> int:
        user_buckets = deepcopy(self.user_buckets)
        total_users = self.total_users
        total_units = self.total_units
        year = GENESIS_YEAR
        stake_reward_supply = int(MAX_UNIT_SUPPLY - INITIAL_UNIT_SUPPLY)
        epoch_per_year = int(365 / STAKING_REWARD_PAY_DAY)

        # Network participation begins at working age and ends when life has ended: https://en.wikipedia.org/wiki/Life_expectancy
        max_user_lifetime = 72 - 16
        # Max working age population, estimated by year 2050: https://ourworldindata.org/age-structure
        # Randomize max user count to random
        max_user_count = random.uniform(50_000_000, 7_000_000_000)

        while 1:
            # Initial population was 9,912
            # Around 5 years later population (10+ Ada) is 1,678,233 based on https://cexplorer.io/wealth
            # So population grew by around 280% a year: 9912 users * (2.8 ^ 5y)
            # Using this trajectory, we randomize with + - 50% year over year.
            user_growth_percent_in_year = random.uniform(230, 330)
            # At a minimum new users grow/shrink by this much.
            user_growth_min_percent_in_year = random.uniform(-10, 20)
            # There needs to be a user growth decay because it cannot grow exponentially forever. Speculative.
            user_growth_decay_in_year = 0.95
            # Total units lost. Speculative.
            lost_unit_percent_in_year = random.uniform(0, 2)
            # Units sent from one user bucket to the next. Generous amount and range.
            sent_unit_percent_in_year = random.uniform(10, 99)
            # Older users trickle down less. Simulates the rich accumulating wealth. Speculative.
            # Extreme: 0.95^56=0.05, 0.98^56=0.32
            sent_unit_decay_in_year = random.uniform(0.95, 1.0)
            # Supply stake is around 60% to 70% according to chart in https://cexplorer.io/epoch
            supply_stake_percent_in_year = random.uniform(60, 70)

            # Add staking rewards to users.
            if year >= STAKING_YEAR:
                # There probably is a faster way to calc this.
                stake_reward = 0
                for epoch in range(epoch_per_year):
                    stake_reward_in_epoch = int(stake_reward_supply * (STAKING_REWARD_PERCENT / 100) * (supply_stake_percent_in_year / 100))
                    stake_reward_supply -= stake_reward_in_epoch
                    stake_reward += stake_reward_in_epoch

                for user_bucket in user_buckets:
                    new_bucket_units = int(user_bucket.units / total_units * stake_reward)
                    user_bucket.units += new_bucket_units

                total_units += stake_reward

            # Onboard new users. Very optimistic.
            user_growth_decay = pow(user_growth_decay_in_year, year - GENESIS_YEAR)
            user_growth = max(1 + (user_growth_min_percent_in_year / 100), (user_growth_percent_in_year / 100) * user_growth_decay)
            new_users = user_buckets[-1].users * user_growth
            # Clamp at max users we can possibly onboard.
            new_users = min(new_users, max_user_count / max_user_lifetime)
            new_users = int(new_users)
            user_buckets.append(UserBucket(users=new_users, units=0))
            total_users += new_users

            # Expire dead users. Transfer units to next bucket.
            # Is not very sophisticated, especially in early years.
            while len(user_buckets) > max_user_lifetime:
                user_buckets[1].units += user_buckets[0].units
                user_buckets.pop(0)

            # Transfer units from each bucket to the next bucket.
            # This will slow trickle down from earlier holders to new holders.
            for n in range(1, len(user_buckets)):
                user_age = len(user_buckets) - n
                sent_units_factor = (sent_unit_percent_in_year / 100) * pow(sent_unit_decay_in_year, user_age)
                transfer_units = int(user_buckets[n-1].units * sent_units_factor)
                user_buckets[n].units += transfer_units
                user_buckets[n-1].units -= transfer_units

            # Lose units. Fairly distributed.
            for n in range(len(user_buckets)):
                lost_units = int(user_buckets[n].units * (lost_unit_percent_in_year / 100))
                user_buckets[n].units -= lost_units
                total_units -= lost_units

            # Do new users have enough units to work with?
            average_units = int(user_buckets[-1].units / user_buckets[-1].users)
            if average_units < min_acceptable_unit_size:
                break

            year += 1

            # Enough is enough.
            if year == GENESIS_YEAR + 1000:
                break

        alive_users = 0
        for user_bucket in user_buckets:
            alive_users += user_bucket.users

        print(f"Simulation has ended in year {year} with a total population of {total_users} and alive population of {alive_users}.")

        return year


def main():
    simulator = Simulator()

    years = []
    run_count = 10000
    min_acceptable_unit_size = 50_000

    for run in range(run_count):
        year = simulator.Run(min_acceptable_unit_size)
        years.append(year)

    min_year = min(years)
    max_year = max(years)
    avg_year = int(round(sum(years) / len(years)))

    print(f"Ran simulation {run_count} times.")
    print(f"Min year when min acceptable unit size ({min_acceptable_unit_size}) was hit: {min_year}")
    print(f"Max year when min acceptable unit size ({min_acceptable_unit_size}) was hit: {max_year}")
    print(f"Avg year when min acceptable unit size ({min_acceptable_unit_size}) was hit: {avg_year}")


if __name__ == "__main__":
    main()
