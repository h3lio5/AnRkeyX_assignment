pragma solidity 0.8.11;

interface IERC20 {
    function transferFrom(
        address spender,
        address to,
        uint256 amount
    ) external returns (bool);

    function transfer(address to, uint256 amount) external returns (bool);

    function balanceOf(address account) external view returns (uint256);
}

contract LinearVestingToken {
    // Container to hold all data specific to a schedule ID
    // struct items are packed in such a way that it costs only 3 SLOADS
    struct Beneficiery {
        address to;
        uint96 startTime;
        address token;
        uint96 duration;
        uint128 totalAmount;
        uint128 alreadyClaimed;
    }
    mapping(uint256 => Beneficiery) schedules;
    // Schedule Id
    uint256 public scheduleId;

    /////////////// Custom Errors ////////
    // They are used instead of require() statements because of deploy and runtime gas efficiency
    // error MinterHasInsufficientBalance();
    error RecipientAddressNotValid();
    error RedeemerNotAuthorized();

    /////////////// Events ///////////////
    event NewVestingScheduleCreated(
        address indexed _tokenAddress,
        address _beneficiery,
        uint256 _amount,
        uint256 _duration,
        uint256 _scheduleId
    );

    event BeneficieryRedeemedTokens(
        uint256 indexed _scheduleId,
        address _beneficiery,
        uint256 _amount
    );

    /////////////// Logic ////////////////

    ///@notice function to create a linear vesting schedule
    ///@param tokenAddress The address of the token to be vesting,e.g., DAI
    ///@param to The beneficiery of the vested tokens
    ///@param amount The total amount of tokens to be vested
    ///@param duration The total duration of the vesting schedule
    ///@return scheduleId The unique Id of a vesting schedule
    function mint(
        address tokenAddress,
        address to,
        uint256 amount,
        uint256 duration
    ) public returns (uint256) {
        // NOTE: The function assumes that minter has already transfered `amount` of tokens to this contract

        // address(0) cannot redeem tokens
        if (to == address(0)) revert RecipientAddressNotValid();

        uint256 _scheduleId = scheduleId; // caching for saving on SLOADs
        // creating a mapping
        schedules[_scheduleId] = Beneficiery(
            to,
            uint96(block.timestamp),
            tokenAddress,
            uint96(duration),
            uint128(amount),
            uint128(0)
        );

        // emit the event
        emit NewVestingScheduleCreated(
            tokenAddress,
            to,
            amount,
            duration,
            _scheduleId
        );
        scheduleId = _scheduleId + 1;
        return _scheduleId;
    }

    function redeem(uint256 _scheduleId) external {
        Beneficiery memory _beneficiary = schedules[_scheduleId]; // caching for saving on SLOADS

        if (msg.sender != _beneficiary.to) revert RedeemerNotAuthorized();

        uint128 _amountToRedeem;
        if (
            uint96(block.timestamp) >=
            _beneficiary.startTime + _beneficiary.duration
        ) {
            _amountToRedeem =
                _beneficiary.totalAmount -
                _beneficiary.alreadyClaimed;
            _beneficiary.alreadyClaimed = _beneficiary.totalAmount;
            IERC20(_beneficiary.token).transfer(
                msg.sender,
                uint256(_amountToRedeem)
            );
        } else {
            // Compute the amount of tokens that can be redeemed: totalUnlocked - alreadyClaimed
            _amountToRedeem =
                ((_beneficiary.totalAmount *
                    uint128(
                        (uint96(block.timestamp) - _beneficiary.startTime)
                    )) / uint128(_beneficiary.duration)) -
                _beneficiary.alreadyClaimed;
            // Update the amount claimed so far
            _beneficiary.alreadyClaimed += _amountToRedeem;
            // Transfer the redeemed amount of tokens to the beneficiary
            IERC20(_beneficiary.token).transfer(
                msg.sender,
                uint256(_amountToRedeem)
            );
        }
        // Update the information related to the scheduleId in the persistent storage
        schedules[_scheduleId] = _beneficiary;
        // emit the event
        emit BeneficieryRedeemedTokens(
            _scheduleId,
            msg.sender,
            uint256(_amountToRedeem)
        );
    }
}
