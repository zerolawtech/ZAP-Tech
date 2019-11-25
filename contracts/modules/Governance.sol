pragma solidity 0.4.25;

import "../OrgCode.sol";
import "../open-zeppelin/SafeMath.sol";


interface IMultiCheckpointModule {
    function checkpointExists(address, uint256) external view returns (bool);
    function totalSupplyAt(address, uint256) external view returns (uint256);
    function balanceAt(address, address, uint256) external view returns (uint256);
    function custodianBalanceAt(address, address, address, uint256) external view returns (uint256);
}


/**
    @title Governance Module
    @dev Attaches to OrgCode and MultiCheckpointModule
*/
contract GovernanceModule {

    using SafeMath for uint256;

    OrgCode public org;
    IMultiCheckpointModule public checkpoint;

    mapping (address => mapping (bytes => bool)) approval;
    mapping (bytes32 => Proposal) proposals;

    /**
        states:
            0 = undeclared
            1 = pending
            2 = active
            3 = closed (failed to reach quorum)
            4 = closed (did not pass)
            5 = closed (passed)
     */
    struct Proposal {
        uint8 state;
        uint64 checkpoint;
        uint64 start;
        uint64 end;
        Vote[] votes;
        string description;
        address approvalAddress;
        bytes approvalCalldata;
        /* holder => custodian address (0x00 if none) */
        mapping (address => mapping (address => uint256)) hasVoted;
    }

    struct Vote {
        uint16 requiredPct;
        uint16 quorumPct;
        uint256 totalVotes;
        uint256[2] counts;
        Share[] shares;
    }

    struct Share {
        address addr;
        uint16 multiplier;
    }

    event NewProposal(
        bytes32 id,
        string description,
        uint64 checkpoint,
        uint64 start,
        uint64 end,
        address approvalAddress,
        bytes approvalCalldata
    );

    event NewVote(
        bytes32 id,
        uint256 voteIndex,
        uint16 requiredPct,
        uint16 quorumPct,
        address[] shares,
        uint16[] multipliers
    );

    event ProposalClosed(
        bytes32 id,
        uint256 result,
        uint256[] voteResults
    );

    /**
        @notice Base constructor
        @param _org OrgCode contract address
     */
    constructor(OrgCode _org, IMultiCheckpointModule _checkpoint) public {
        org = _org;
        checkpoint = _checkpoint;
    }

    /**
        @notice Checks that a call comes from a permitted module or the org
        @dev If the caller is the org, requires multisig approval
        @return bool multisig approved
     */
    function _checkPermitted() internal returns (bool) {
        return org.checkMultiSigExternal(
            msg.sender,
            keccak256(msg.data),
            msg.sig
        );
    }


    /**
        @notice get the current state of a proposal
        @param _id Proposal ID
        @return uint8 state
     */
    function getProposalState(bytes32 _id) external view returns (uint8) {
        return proposals[_id].state;
    }

    /**
        @notice get the result of a proposal vote as a state value
        @param _id Proposal ID
        @param _voteIndex Index of proposal vote
        @return uint8 result
     */
    function getVoteResult(
        bytes32 _id,
        uint256 _voteIndex
    )
        external
        view
        returns (uint8)
    {
        Proposal storage p = proposals[_id];
        require (p.state > 2);
        return _getVoteResult(p.votes[_voteIndex]);
    }

    /**
        @notice get the percentage result of a proposal vote
        @dev Percentages are expressed as integers * 100 (eg. 50% is 5000)
        @param _id Proposal ID
        @param _voteIndex Index of proposal vote
        @return yes % of vote, quorum % of vote
     */
    function getVotePct(
        bytes32 _id,
        uint256 _voteIndex
    )
        external
        view
        returns (uint256 _votePct, uint256 _quorumPct)
    {
        Vote storage v = proposals[_id].votes[_voteIndex];
        if (v.quorumPct > 0) {
            uint256 _total = v.counts[0].add(v.counts[1]);
            _quorumPct = _total.mul(10000).div(v.totalVotes);
        } else {
            _total = v.totalVotes;
        }
        return (v.counts[1].mul(10000).div(_total), _quorumPct);
    }


    /**
        @notice Create a new proposal
        @dev
            The ID should be a hash generated from legal documents pertaining
            to the proposal.
        @param _id Proposal ID
        @param _checkpoint Epoch time for balance snapshot that votes are based on
        @param _start Epoch time that voting begins
        @param _end Epoch time that voting closes (leave as 0 to never close)
        @param _description String description of proposal
        @param _approvalAddress Optional - permissioned address if proposal passes
        @param _approvalCalldata Optional - Permissioned calldata if proposal passes
        @return bool success
     */
    function newProposal(
        bytes32 _id,
        uint64 _checkpoint,
        uint64 _start,
        uint64 _end,
        string _description,
        address _approvalAddress,
        bytes _approvalCalldata
    )
        external
        returns (bool)
    {
        if (!_checkPermitted()) return false;
        Proposal storage p = proposals[_id];
        require(p.state == 0); // dev: proposal already exists
        require(now < _start); // dev: start < now
        require(_checkpoint <= _start); // dev: start < checkpoint
        require(_end == 0 || _start < _end); // dev: end < start
        p.state = 1;
        p.checkpoint = _checkpoint;
        p.start = _start;
        p.end = _end;
        p.description = _description;
        if (_approvalAddress != 0x00) {
            p.approvalAddress = _approvalAddress;
            p.approvalCalldata = _approvalCalldata;
        }
        emit NewProposal(
            _id,
            _description,
            _checkpoint,
            _start,
            _end,
            _approvalAddress,
            _approvalCalldata
        );
        return true;
    }

    /**
        @notice Create a new vote within a proposal
        @param _id Proposal ID
        @param _requiredPct Required % for vote to pass, as int * 100
        @param _requiredPct Quorum % (leave as 0 for no quorum requirement)
        @param _shares Array of share contract addresses
        @param _multipliers Array of vote multipliers
        @return bool success
     */
    function newVote(
        bytes32 _id,
        uint16 _requiredPct,
        uint16 _quorumPct,
        address[] _shares,
        uint16[] _multipliers
    )
        external
        returns (bool)
    {
        if (!_checkPermitted()) return false;
        Proposal storage p = proposals[_id];
        require(p.state == 1); // dev: wrong state
        require(_shares.length > 0); // dev: empty share array
        require(_shares.length == _multipliers.length); // dev: array length mismatch
        require(_requiredPct <= 10000); // dev: required pct too high
        require(_quorumPct <= 10000); // dev: quorum pct too high
        p.votes.length += 1;
        Vote storage v = p.votes[p.votes.length-1];
        v.requiredPct = _requiredPct;
        v.quorumPct = _quorumPct;
        v.shares.length = _shares.length;
        for (uint256 i; i < _shares.length; i++) {
            for (uint256 x = i + 1; x < _shares.length; x++) {
                require(_shares[x] != _shares[i]); // dev: share repeat
            }
            /**
                checkpoint must exist when the vote is declared
                possible TODO - allow this contract to create the checkpoint
             */
            require(checkpoint.checkpointExists(_shares[i], p.checkpoint)); // dev: no checkpoint
            v.shares[i] = Share(_shares[i], _multipliers[i]);
        }
        emit NewVote(
            _id,
            p.votes.length - 1,
            _requiredPct,
            _quorumPct,
            _shares,
            _multipliers
        );
        return true;
    }

    /**
        @notice Cast a vote on a proposal
        @param _id Proposal ID
        @param _vote Vote boolean as an integer (0=no, 1=yes)
        @return bool success
     */
    function voteOnProposal(bytes32 _id, uint8 _vote) external returns (bool) {
        require(_vote < 2); // dev: invalid vote
        Proposal storage p = proposals[_id];
        require(p.state > 0); // dev: invalid id
        require(p.state < 3); // dev: proposal has closed
        require(p.end >= now || p.end == 0); // dev: voting has finished
        require(p.hasVoted[msg.sender][0x00] == 0); // dev: already voted
        if (p.state == 1) _openVote(p);
        p.hasVoted[msg.sender][0x00] = _vote + 1;
        for (uint256 i; i < p.votes.length; i++) {
            p.votes[i].counts[_vote] = p.votes[i].counts[_vote].add(_getVotes(
                p.votes[i].shares,
                p.checkpoint
            ));
        }
        /** No event is emitted, cuz privacy */
        return true;
    }

    /**
        @notice Cast a vote on a proposal with custodied shares
        @dev voteForProposal must be called before this method, to log the vote
        @param _id Proposal ID
        @param _custodian Custodian contract address
        @return bool success
     */
    function custodialVoteOnProposal(
        bytes32 _id,
        address _custodian
    )
        external
        returns (bool)
    {
        Proposal storage p = proposals[_id];
        require(p.state == 2); // dev: proposal not active
        require(p.end >= now || p.end == 0); // dev: voting has finished
        require(p.hasVoted[msg.sender][0x00] != 0); // dev: has not voted
        require(p.hasVoted[msg.sender][_custodian] == 0); // dev: has voted with custodian
        uint256 _vote = p.hasVoted[msg.sender][0x00] - 1;
        p.hasVoted[msg.sender][_custodian] = _vote + 1;
        for (uint256 i; i < p.votes.length; i++) {
            p.votes[i].counts[_vote] += _getCustodianVotes(
                p.votes[i].shares,
                _custodian,
                p.checkpoint
            );
        }
        /** No event is emitted, cuz privacy */
        return true;
    }

    /**
        @notice Close a proposal
        @param _id Proposal ID
        @return bool success
     */
    function closeProposal(bytes32 _id) external returns (bool) {
        if (!_checkPermitted()) return false;
        Proposal storage p = proposals[_id];
        require(p.end < now); // dev: voting has not finished
        if (p.state == 1) _openVote(p);
        require(p.state == 2); // dev: proposal not active
        
        uint256 _state = 5;
        uint256[] memory _results = new uint256[](p.votes.length);
        for (uint256 i; i < p.votes.length; i++) {
            _results[i] = _getVoteResult(p.votes[i]);
            if (_results[i] < _state) {
                _state = _results[i];
            }
        }
        /** if proposal has no end time, may only be closed once it passes */
        if (p.end == 0) {
            require(_state == 5); // dev: proposal has not passed
        }
        p.state = uint8(_state);

        if (_state == 5 && p.approvalAddress != 0x00) {
            approval[p.approvalAddress][p.approvalCalldata] = true;
        }
        emit ProposalClosed(_id, _state, _results);
    }

    /* query checkpoint totalSupply and set total possible votes */
    function _openVote(Proposal storage p) internal {
        require(now >= p.start); // dev: vote has not started
        p.state = 2;
        for (uint256 i; i < p.votes.length; i++) {
            p.votes[i].totalVotes = _getTotalVotes(
                p.votes[i].shares,
                p.checkpoint
            );
        }
    }

    /**
        @notice Internal - calculate total votes possible
        @dev
            TODO - This method and the following two can be combined to a single
            one using .call() with solidity 0.5.x - but first brownie needs to
            support multiple compiler versions on a project
        @param t Storage marker for Share struct
        @param _time Checkpoint time
        @return uint256 total possible votes
     */
    function _getTotalVotes(
        Share[] storage t,
        uint256 _time
    )
        internal
        view
        returns
        (uint256 _total)
    {
        for (uint256 i; i < t.length; i++) {
            uint256 _ts = checkpoint.totalSupplyAt(t[i].addr, _time);
            _total = _total.add(_ts.mul(t[i].multiplier));
        }
        return _total;
    }

    /**
        @notice Internal - calculate total votes for an investor
        @param t Storage marker for Share struct
        @param _time Checkpoint time
        @return uint256 total votes
     */
    function _getVotes(
        Share[] storage t,
        uint256 _time
    )
        internal
        view
        returns (uint256 _total)
    {
        for (uint256 i; i < t.length; i++) {
            uint256 _bal = checkpoint.balanceAt(t[i].addr, msg.sender, _time);
            _total = _total.add(_bal.mul(t[i].multiplier));
        }
        return _total;
    }

    /**
        @notice Internal - calculate total votes for an investor via custodian
        @param t Storage marker for Share struct
        @param _cust Custodian contract address
        @param _time Checkpoint time
        @return uint256 total custodied votes
     */
    function _getCustodianVotes(
        Share[] storage t,
        address _cust,
        uint256 _time
    )
        internal
        view
        returns (uint256 _total)
    {
        for (uint256 i; i < t.length; i++) {
            uint256 _bal = checkpoint.custodianBalanceAt(
                t[i].addr,
                msg.sender,
                _cust,
                _time
            );
            _total = _total.add(_bal.mul(t[i].multiplier));
        }
        return _total;
    }

    /**
        @notice Internal - get the results of a single vote
        @param v Vote struct storage marker
        @return uint8 vote result (3=below quorum, 4=failed, 5=passed)
     */
    function _getVoteResult(Vote storage v) internal view returns (uint8) {
        if (v.quorumPct > 0) {
            uint256 _total = v.counts[0].add(v.counts[1]);
            if (_total.mul(10000).div(v.totalVotes) < v.quorumPct) return 3;
        } else {
            _total = v.totalVotes;
        }
        if (v.counts[1].mul(10000).div(_total) < v.requiredPct) return 4;
        return 5;
    }

    /** @notice Internal - check approval for a permissioned call */
    function _checkApproval() internal {
        if (!approval[msg.sender][msg.data]) revert();
        approval[msg.sender][msg.data] = false;
    }

    /** @notice Fallback function, can be used to provide module permissioning */
    function () external {
        _checkApproval();
    }

    /**
        @notice Approval to modify authorized supply
        @dev Called by OrgCode.modifyAuthorizedSupply
        @return permission boolean
     */
    function modifyAuthorizedSupply(address, uint256) external returns (bool) {
        _checkApproval();
        return true;
    }

    /**
        @notice Approval to attach a new share contract
        @dev Called by OrgCode.addOrgShare
        @return permission boolean
     */
    function addOrgShare(address) external returns (bool) {
        _checkApproval();
        return true;
    }

}
