"""Reject apparent Continue success without real reset and release-first cues."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from th04_ordinary_continue import validate_transition, validate_wait_cues


class ContinueTransitionTests(unittest.TestCase):
    def setUp(self):
        before = bytearray(80)
        before[:11] = b'HUMAConfig\0'
        before[11:15] = bytes((1, 6, 0, 0))
        after = before.copy()
        after[11] = 6
        self.capture = dict(receipt=dict(continue_at_frame=1),
                            resident=[before.hex(), before.hex(), after.hex()],
                            rows=[{}, dict(score_digits='0001020304050607', stage='00'),
                                  dict(score_digits='0100000000000000', power='01', frame='0200', stage='00')])

    def test_natural_last_life_restores_credit_and_updates_score_counter(self):
        self.assertEqual(validate_transition(self.capture)['counter_after'], 1)

    def test_separate_counter_with_unchanged_score_digit_rejects(self):
        self.capture['rows'][2]['score_digits'] = '0000000000000000'
        with self.assertRaisesRegex(ValueError, 'score/counter'):
            validate_transition(self.capture)

    def test_stale_score_digits_reject(self):
        self.capture['rows'][2]['score_digits'] = '0100000000000001'
        with self.assertRaisesRegex(ValueError, 'score/counter'):
            validate_transition(self.capture)

    def test_lives_must_restore_from_the_actual_credit(self):
        after = bytearray.fromhex(self.capture['resident'][2])
        after[11] = 5
        self.capture['resident'][2] = after.hex()
        with self.assertRaisesRegex(ValueError, 'credit restoration'):
            validate_transition(self.capture)

    def test_a_non_last_life_fixture_cannot_claim_natural_game_over(self):
        before = bytearray.fromhex(self.capture['resident'][1])
        before[11] = 2
        self.capture['resident'][1] = before.hex()
        with self.assertRaisesRegex(ValueError, 'last-life'):
            validate_transition(self.capture)

    def test_wrong_power_stage_or_frame_rejects(self):
        for name, value in (('power', '02'), ('stage', '01'), ('frame', '0300')):
            capture = copy.deepcopy(self.capture)
            capture['rows'][2][name] = value
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'resumed boundary'):
                validate_transition(capture)


class ContinueCueTests(unittest.TestCase):
    def setUp(self):
        self.receipt = dict(dialog_at_frame=1, continue_at_frame=3, end_after=6)
        self.clock = dict(actions=[], waits=[])
        for kind, frame in (('dialogue', 1), ('continue', 3)):
            start = len(self.clock['actions'])
            self.clock['actions'].extend([
                dict(key='KBD_z', pressed=False, frame=frame, tick=1000),
                dict(key='KBD_enter', pressed=True, frame=frame, tick=1500),
                dict(key='KBD_enter', pressed=False, frame=frame, tick=1620),
                dict(key='KBD_z', pressed=True, frame=frame+1, tick=2000, resident='resident')])
            self.clock['waits'].append(dict(kind=kind, frame=frame, tick=900, action_start=start,
                                            action_end=start+4, resumed_frame=frame+1,
                                            resumed_tick=2000, resident_after='resident'))

    def test_two_distinct_waits_with_real_release_confirmation_and_resume_pass(self):
        validate_wait_cues(self.clock, self.receipt)

    def test_missing_or_reordered_waits_reject(self):
        for waits in (self.clock['waits'][:1], list(reversed(self.clock['waits']))):
            clock = dict(self.clock, waits=waits)
            with self.assertRaisesRegex(ValueError, 'wait count|wait boundary'):
                validate_wait_cues(clock, self.receipt)

    def test_confirming_a_held_key_without_release_rejects(self):
        self.clock['actions'][4]['pressed'] = True
        with self.assertRaisesRegex(ValueError, 'release-first'):
            validate_wait_cues(self.clock, self.receipt)

    def test_no_confirmation_or_no_resumed_shot_rejects(self):
        for index in (5, 7):
            clock = copy.deepcopy(self.clock)
            clock['actions'][index]['pressed'] = False
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, 'confirmation|resumed gameplay'):
                validate_wait_cues(clock, self.receipt)

    def test_a_terminal_before_observed_resume_rejects(self):
        self.receipt['end_after'] = 4
        with self.assertRaisesRegex(ValueError, 'cue extent'):
            validate_wait_cues(self.clock, self.receipt)


if __name__ == '__main__':
    unittest.main()
