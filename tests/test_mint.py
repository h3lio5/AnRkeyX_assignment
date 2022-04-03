from datetime import timedelta
from brownie import Wei, chain, reverts


def test_mint(owner, alice, vestingContract, dai, lusd):
    # mint 1000 DAI and 1000 LUSD to the owner address
    dai.mint(Wei(1000e18), {"from": owner})
    lusd.mint(Wei(1000e18), {"from": owner})

    # check if the said amount got minted to the owner's address
    assert dai.balanceOf(owner) == Wei(1000e18)
    assert lusd.balanceOf(owner) == Wei(1000e18)

    # owner transfers 1000 DAI and 1000 LUSD to the vesting contract
    dai.transfer(vestingContract, Wei(1000e18), {"from": owner})
    lusd.transfer(vestingContract, Wei(1000e18), {"from": owner})

    # check if transfer of said amount has occured correctly
    assert dai.balanceOf(vestingContract) == Wei(1000e18)
    assert lusd.balanceOf(vestingContract) == Wei(1000e18)

    # create linear vesting schedules for alice
    tx1 = vestingContract.mint(
        dai, alice, Wei(1000e18), Wei(86400 * 365)
    )  # 1 day = 86400 seconds
    tx1.wait(1)
    tx1_events = tx1.events["NewVestingScheduleCreated"]
    assert tx1_events["_scheduleId"] == 0
    assert tx1_events["_beneficiery"] == alice

    tx2 = vestingContract.mint(
        lusd, alice, Wei(1000e18), Wei(86400 * 365)
    )  # 1 day = 86400 seconds
    tx2.wait(1)
    tx2_events = tx2.events["NewVestingScheduleCreated"]
    assert tx2_events["_scheduleId"] == 1
    assert tx2_events["_beneficiery"] == alice


def test_redeem_before_unlock_time(owner, alice, vestingContract, dai, lusd):
    # mint 1000 DAI and 1000 LUSD to the owner address
    dai.mint(Wei(1000e18), {"from": owner})
    lusd.mint(Wei(1000e18), {"from": owner})
    # owner transfers 1000 DAI and 1000 LUSD to the vesting contract
    dai.transfer(vestingContract, Wei(1000e18), {"from": owner})
    lusd.transfer(vestingContract, Wei(1000e18), {"from": owner})
    # create linear vesting schedules for alice
    tx1 = vestingContract.mint(
        dai, alice, Wei(1000e18), Wei(86400 * 365)
    )  # 1 year = 86400 seconds
    tx1.wait(1)
    tx2 = vestingContract.mint(
        lusd, alice, Wei(1000e18), Wei(86400 * 365)
    )  # 1 year = 86400 seconds
    tx2.wait(1)

    # Alice redeems DAI 5 weeks after vesting started
    chain.mine(timedelta=86400 * 7 * 5)

    # only alice can redeem tokens corresponding to scheduleId = 0
    # i.e., TX should revert if owner is trying to redeem
    with reverts():
        vestingContract.redeem(Wei(0), {"from": owner})

    tx3 = vestingContract.redeem(Wei(0), {"from": alice})
    tx3.wait(1)
    tx3_events = tx3.events["BeneficieryRedeemedTokens"]
    assert tx3_events["_beneficiery"] == alice
    assert tx3_events["_amount"] == dai.balanceOf(alice)

    # Alice redeems LUSD after 9 weeks after vesting started
    chain.mine(timedelta=86400 * 7 * 4)  # 4 more weeks forward

    tx4 = vestingContract.redeem(Wei(1), {"from": alice})
    tx4.wait(1)
    tx4_events = tx4.events["BeneficieryRedeemedTokens"]
    assert tx4_events["_beneficiery"] == alice
    assert tx4_events["_amount"] == lusd.balanceOf(alice)


def test_redeem_after_unlock_time(owner, alice, vestingContract, dai, lusd):
    # mint 1000 DAI to the owner address
    dai.mint(Wei(1000e18), {"from": owner})

    # owner transfers 1000 DAI to the vesting contract
    dai.transfer(vestingContract, Wei(1000e18), {"from": owner})

    # create linear vesting schedules for alice
    tx1 = vestingContract.mint(
        dai, alice, Wei(1000e18), Wei(86400 * 365)
    )  # 1 year = 86400 seconds
    tx1.wait(1)

    # Alice redeems DAI 13 months after vesting started
    chain.mine(timedelta=86400 * (365 + 30))

    # only alice can redeem tokens corresponding to scheduleId = 0
    # i.e., TX should revert if owner is trying to redeem
    with reverts():
        vestingContract.redeem(Wei(0), {"from": owner})

    tx2 = vestingContract.redeem(Wei(0), {"from": alice})
    tx2.wait(1)
    tx2_events = tx2.events["BeneficieryRedeemedTokens"]
    assert tx2_events["_beneficiery"] == alice
    # redeemed amount should be equal to the total tokens available for redeem
    assert tx2_events["_amount"] == tx1.events["NewVestingScheduleCreated"]["_amount"]

    # Now alice tries to redeem again after redeeming all of her tokens
    tx3 = vestingContract.redeem(Wei(0), {"from": alice})
    tx3.wait(1)
    tx3_events = tx3.events["BeneficieryRedeemedTokens"]
    # she must be able to redeem ONLY zero tokens
    assert tx3_events["_amount"] == Wei(0)
