from unittest import TestCase, main
from ethereum import tester as t

from pyethereum import utils
from rlp.utils import decode_hex

import json


class TestResolution(TestCase):

    def setUp(self):

        s = t.state()

        code = open('sponsor.sol').read()
        self.c = t.state().abi_contract(code, language='solidity')

        self.alice_priv = t.k0
        self.alice_addr = utils.privtoaddr(self.alice_priv)
        self.bob_priv = t.k1
        self.bob_addr = utils.privtoaddr(self.bob_priv)

        # wget -qO- https://www.realitykeys.com/api/v1/runkeeper/new --post-data="user_id=29908850&activity=running&measurement=total_distance&comparison=ge&goal=4000&settlement_date=2015-12-23&objection_period_secs=604800&accept_terms_of_service=current&use_existing=1"

        before_event = json.loads('{"no_pubkey": "", "comparison": null, "measurement": "total_distance", "activity_open_datetime": "2015-12-02 06:35:05", "settlement_date": "2015-12-03", "objection_period_secs": 0, "human_resolution_scheduled_datetime": null, "value": null, "machine_resolution_winner": "No", "id": 6206, "evaluation_method": null, "machine_resolution_value": "246.210454708", "is_user_authenticated": true, "objection_fee_satoshis_paid": 0, "objection_fee_satoshis_due": 1000000, "machine_resolution_scheduled_datetime": "2015-12-03 00:00:00", "user_id": "29908850", "goal": null, "created_datetime": "2015-12-02 06:35:05", "winner": null, "user_profile": "edochan", "winner_value": null, "source": "runkeeper", "yes_pubkey": "", "signature_v2": {"signed_hash": null, "base_unit": 1000000000000000000, "signed_value": null, "sig_der": null, "ethereum_address": "6fde387af081c37d9ffa762b49d340e6ae213395", "fact_hash": "634ab403c50fec82f39e8c4057ea29105708967d386c7f58325a28db333bc418", "sig_r": null, "sig_s": null, "pubkey": "02e577bc17badf301e14d86c33d76be5c3b82a0c416fc93cd124d612761191ec21", "sig_v": null}, "activity_closed_datetime": null, "activity": "walking", "human_resolution_value": null, "user_name": ["edochan"], "winner_privkey": null}')

        sig_data = before_event['signature_v2']
        rk_addr = sig_data['ethereum_address']
        event_hash = sig_data['fact_hash']
        base_unit = sig_data['base_unit']

        # This happens to be the same as the base unit, but there is no deep meaning behind this.
        ETH_TO_WEI = 1000000000000000000000

        self.pledge_id = self.c.add_pledge(
            self.alice_addr, 
            decode_hex(event_hash), 
            base_unit,
            100, # You have to walk at least 100 meters before we pay
            int(0.01 * ETH_TO_WEI / 100), # We'll give you 0.01 eth per 100 meters (0.0001 eth per meter) after that
            rk_addr,
            sender=self.alice_priv,
            value=int(0.04 * ETH_TO_WEI), # We'll fund you 0.04 eth
        );

    def test_claim(self):

        # https://www.realitykeys.com/runkeeper/6206
        # https://www.realitykeys.com/api/v1/runkeeper/6206?accept_terms_of_service=current

        after_event = json.loads('{"no_pubkey": "", "comparison": null, "measurement": "total_distance", "activity_open_datetime": "2015-12-02 06:35:05", "settlement_date": "2015-12-03", "objection_period_secs": 0, "human_resolution_scheduled_datetime": null, "value": null, "machine_resolution_winner": "No", "id": 6206, "evaluation_method": null, "machine_resolution_value": "246.210454708", "is_user_authenticated": true, "objection_fee_satoshis_paid": 0, "objection_fee_satoshis_due": 1000000, "machine_resolution_scheduled_datetime": "2015-12-03 00:00:00", "user_id": "29908850", "goal": null, "created_datetime": "2015-12-02 06:35:05", "winner": "No", "user_profile": "edochan", "winner_value": "246.210454708", "source": "runkeeper", "yes_pubkey": "", "signature_v2": {"signed_hash": "6ce5105e4239c5ff401e46a4e660b0980298a15bd91ede79beac4ceb1b03939a", "base_unit": 1000000000000000000, "signed_value": "00000000000000000000000000000000000000000000000d58db4013f9be0800", "sig_der": "304502210083463358f3df9507b04d3db8ebaddf4cc36e50c97268a141282708f987d38d93022036a38b9fa72a16e8701478a1c39f766561bc9bce8fa4b5e9ab7b99ce685744d8", "ethereum_address": "6fde387af081c37d9ffa762b49d340e6ae213395", "fact_hash": "634ab403c50fec82f39e8c4057ea29105708967d386c7f58325a28db333bc418", "sig_r": "83463358f3df9507b04d3db8ebaddf4cc36e50c97268a141282708f987d38d93", "sig_s": "36a38b9fa72a16e8701478a1c39f766561bc9bce8fa4b5e9ab7b99ce685744d8", "pubkey": "02e577bc17badf301e14d86c33d76be5c3b82a0c416fc93cd124d612761191ec21", "sig_v": 28}, "activity_closed_datetime": null, "activity": "walking", "human_resolution_value": null, "user_name": ["edochan"], "winner_privkey": null}')

        sig_data = after_event['signature_v2']
        signed_hash = sig_data['signed_hash']
        rk_addr = sig_data['ethereum_address']
        event_hash = sig_data['fact_hash']
        result_value_hex = sig_data['signed_value']
        v = sig_data['sig_v']
        r = sig_data['sig_r']
        s = sig_data['sig_s']

        base_unit = sig_data['base_unit']

        self.c.settle(
            self.pledge_id,
            decode_hex(result_value_hex),
            v,
            decode_hex(r),
            decode_hex(s)
        )

        return


if __name__ == '__main__':
    main()
