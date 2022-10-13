// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;


import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@oz/security/ReentrancyGuard.sol";


contract Dai {

    address immutable OWNER;

    mapping(address => uint256) balances;

    constructor() {
        // TODO: Must deploy from CDP
        OWNER = msg.sender;
    }

    function mint(address recipient, uint256 amount) external {
        balances[recipient] += amount;
    }

    function balanceOf(address recipient) external view returns (uint256) {
        return balances[recipient];
    }

    function burn(address caller, uint256 amount) external {
        balances[recipient] -= amount;
    }
}

Enum RepayWith {
    DAI,
    COLLATERAL
}

interface ICallbackRecipient {

    function flashMintCallback(address initiator, uint256 amount, bytes memory data) returns (RepayWith, uint256);
}

contract Cdp {
    using SafeERC20 for IERC20;

    uint256 constant MAX_BPS = 10_000;

    uint256 constant LIQUIDATION_TRESHOLD = 10_000; // 100% in BPS

    Dai immutable public DAI;

    IERC20 immutable public COLLATERAL;

    uint256 totalDeposited;

    uint256 totalBorrowed;

    // Oracle for Ratio
    uint256 ratio = 3e17; // Conversion rate

    uint256 constant RATIO_DECIMALS = 10 ** 8;

    address owner;

    constructor(IERC20 collateral) {
        DAI = new Dai();
        COLLATERAL = collateral;
    }

    // NOTE: Unsafe should be protected by governance (tbh should be a feed)
    function setRatio(uint256 newRatio) external {
        ratio = newRatio;
    }

    function flash(uint256 amount, ICallbackRecipient target, bytes memory data) external {
        // No checks as we allow minting after

        // Effetcs
        uint256 newTotalBorrowed = totalBorrowed + amount;

        totalBorrowed = newTotalBorrowed;

        // Interactions
        // Flash mint amount
        // Safe because DAI is nonReentrant as we know impl
        DAI.mint(target, amount);


        // Callback
        (RepayWith collateralChoice, uint256 repayAmount) = target.flashMintCallback(msg.sender, amount, data);


        // Check solvency
        if(totalBorrowed > maxBorrow()) {
            if(collateralChoice == RepayWith.DAI) {
                uint256 minRepay = totalBorrowed - maxBorrow();
                // They must repay
                // This is min repayment
                require(repayAmount >= minRepay);

                // TODO: This may be gameable must fuzz etc.. this is a toy project bruh
                totalBorrowed -= repayAmount;

                // Get the repayment
                // DAI Cannot reenter because we know impl, DO NOT ADD HOOKS OR YOU WILL GET REKT
                DAI.burn(target, repayAmount);
            } else {
                // They repay with collateral

                // NOTE: WARN
                // This can reenter for sure, DO NOT USE IN PROD
                deposit(repayAmount);

                assert(isSolvent());
            }
        }
    }


    // Deposit
    function deposit(uint256 amount) public {
        // Increase deposited
        totalDeposited += amount;

        if (owner == address(0)) {
            owner = msg.sender;
        }

        // Check delta + transfer
        uint256 prevBal = COLLATERAL.balanceOf(address(this));
        COLLATERAL.safeTransferFrom(msg.sender, address(this), amount);
        uint256 afterBal = COLLATERAL.balanceOf(address(this));

        // Make sure we got the amount we expected
        require(afterBal - prevBal == amount, "No feeOnTransfer");   
    }

    // Borrow
    function borrow(uint256 amount) external {
        // Checks
        uint256 newTotalBorrowed = totalBorrowed + amount;
        
        // Check if borrow is solvent
        uint256 maxBorrowCached = maxBorrow();

        require(newTotalBorrowed <= maxBorrowCached, "Over debt limit");

        // Effect
        totalBorrowed = newTotalBorrowed;

        // Interaction
        DAI.mint(msg.sender, amount);
    }

    function maxBorrow() public view returns (uint256) {
        return totalDeposited * ratio / RATIO_DECIMALS;
    }

    function isSolvent() external view returns (bool) {
        return totalBorrowed <= maxBorrow();
    }

    // Liquidate
    function liquidate() external {
        require(!isSolvent(), "Must be insolvent");

        uint256 excessDebt = totalBorrowed - maxBorrow();


        // Give the contract to liquidator
        owner = msg.sender;


        // Burn the token
        DAI.burn(msg.sender, excessDebt);
    }

}