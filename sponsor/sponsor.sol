contract Sponsorship {

    event LogSettlementAmount(uint);    
    event LogFunded(uint);    
    event LogPaid(uint);    
    event LogDue(uint);    
    event LogRefunded(uint);    
    event LogFail(address);    

    event LogClearedThreshold(uint);

    struct Pledge {
        address sponsorer;
        address sponsoree;

        address oracle_address;
        bytes32 event_hash;
        uint base_unit;

        uint success_threshold;
        uint amount_per_meter;
        uint amount_pledged;
    }

    uint numPledges;
    mapping (uint => Pledge) pledges;

    function Sponsorship() {
    }

    function add_pledge( address sponsoree, bytes32 event_hash, uint base_unit, uint success_threshold, uint amount_per_meter, address oracle_address) returns (uint) {
        
        address msg_sender = msg.sender;
        numPledges = numPledges + 1;
        uint pledgeID = numPledges;
        pledges[pledgeID] = Pledge( {
            sponsorer: msg_sender, 
            sponsoree: sponsoree,
            oracle_address: oracle_address,
            event_hash: event_hash,
            success_threshold: success_threshold,
            amount_per_meter: amount_per_meter,
            base_unit: base_unit,
            amount_pledged: msg.value
        });
        return pledgeID;

    }

    function settle(uint pledgeID, bytes32 result_value_hex, uint8 v, bytes32 r, bytes32 s) returns (bool) {

        Pledge p = pledges[pledgeID];

        bytes32 result_hash = sha3(p.event_hash, result_value_hex);
        address signer_address = ecrecover(result_hash, v, r, s);
        uint256 result_value = uint256(result_value_hex) / p.base_unit;

        LogSettlementAmount(result_value);
        if (signer_address != p.oracle_address) {
           LogFail(signer_address);
           LogFail(p.oracle_address);
           return false;
        }

        uint result_above_success_threshold = result_value - p.success_threshold;
        LogClearedThreshold(result_above_success_threshold);

        uint remainder = p.amount_pledged;
        LogFunded(remainder);

        if (result_above_success_threshold > 0) {
            uint due = result_above_success_threshold * p.amount_per_meter;
            LogDue(due);
            if (due > remainder) {
               due = remainder;
            }
            remainder = remainder - due;
            p.sponsoree.send(due);
            LogPaid(due);
        }

        if (remainder > 0) {
            p.sponsorer.send(remainder);
            LogRefunded(remainder);
        }

        return true;

    }

}
