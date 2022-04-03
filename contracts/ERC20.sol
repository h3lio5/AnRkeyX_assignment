// SPDX-License-Identifier: MIT
pragma solidity 0.8.11;

// Minimal implementation of an ERC20 only for the purpose of this technical assignment
contract ERC20 {
    // Storage variables
    mapping(address => mapping(address => uint256)) private _allowances;
    mapping(address => uint256) private _balances;

    string public name;
    string public symbol;

    uint256 public decimals;
    uint256 public totalSupply;

    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _decimals
    ) {
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
    }

    // NOTE: For the purposes of this technical assignment anyone can mint the tokens
    function mint(uint256 amount) public {
        _balances[msg.sender] += amount;
        totalSupply += amount;
    }

    function balanceOf(address account) external view returns (uint256) {
        return _balances[account];
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) external returns (bool) {
        // spend the allowance
        _allowances[from][msg.sender] -= amount;
        _transfer(from, to, amount);
        return true;
    }

    function _transfer(
        address from,
        address to,
        uint256 amount
    ) internal {
        uint256 _fromBalance = _balances[from];
        require(
            _fromBalance >= amount,
            "ERC20: transfer amount exceeds balance"
        );
        unchecked {
            _balances[from] = _fromBalance - amount;
        }
        _balances[to] += amount;
    }
}
