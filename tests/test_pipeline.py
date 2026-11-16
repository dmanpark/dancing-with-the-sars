import numpy as np
import pytest
from scipy.optimize import brentq
from scipy.stats import norm

from dwts import config as C
from dwts.calib import calibrate_channel, offset_map
from dwts.detect import classify, flooded_veg, nanmedian3, open_water, twosided_open
from dwts.grid import block_mean_power, power_to_db
from dwts.stats import Bootstrap, block_index, score_methods
from dwts.thresholds import ashman_d, fit_tile, kittler_illingworth


def test_ki_recovers_known_threshold():
    rng = np.random.default_rng(1)
    w1, m1, s1, w2, m2, s2 = 0.3, -20.0, 1.5, 0.7, -8.0, 2.0
    n = 200_000
    v = np.concatenate([rng.normal(m1, s1, int(n * w1)), rng.normal(m2, s2, int(n * w2))])
    truth = brentq(lambda t: w1 * norm.pdf(t, m1, s1) - w2 * norm.pdf(t, m2, s2), m1, m2)
    t = kittler_illingworth(v, m1, m2)
    assert abs(t - truth) < 0.5


def test_ashman_d_hand_calculation():
    # sqrt(2) * |(-20) - (-8)| / sqrt(1.5^2 + 2^2) = sqrt(2) * 12 / 2.5 = 6.7882...
    assert ashman_d(-20, -8, 1.5, 2.0) == pytest.approx(np.sqrt(2) * 12 / 2.5, rel=1e-9)
    assert ashman_d(0, 1, 1, 1) == pytest.approx(1.0)


def test_fit_tile_bimodal_and_unimodal():
    rng = np.random.default_rng(2)
    bi = np.concatenate([rng.normal(-20, 1.5, 20_000), rng.normal(-8, 2, 40_000)])
    uni = rng.normal(-8, 2, 60_000)
    fb, fu = fit_tile(bi), fit_tile(uni)
    assert fb["passes"] and -17 < fb["threshold_db"] < -12
    assert not fu["passes"]


def _stable(shape):
    return np.ones(shape, bool)


def test_calibration_branch_none():
    lr = np.full((500, 500), 0.2, np.float32)
    rec = calibrate_channel(lr, _stable(lr.shape), None)
    assert rec["branch"] == "none"
    assert np.all(offset_map(rec, None, lr.shape) == 0)


def test_calibration_branch_scene():
    lr = np.full((500, 500), 0.8, np.float32)
    rec = calibrate_channel(lr, _stable(lr.shape), None)
    assert rec["branch"] == "scene"
    assert np.allclose(offset_map(rec, None, lr.shape), 0.8)


def test_calibration_branch_per_part():
    lr = np.zeros((500, 500), np.float32)
    lr[:250, :250], lr[:250, 250:], lr[250:, :250], lr[250:, 250:] = 0.0, 0.3, 0.6, 0.9
    part = np.ones(lr.shape, np.uint8)
    part[250:] = 2
    rec = calibrate_channel(lr, _stable(lr.shape), part)
    assert rec["branch"] == "per_part"
    off = offset_map(rec, part, lr.shape)
    assert off[0, 0] == pytest.approx(np.median(lr[:250]))
    assert off[-1, -1] == pytest.approx(np.median(lr[250:]))


def test_averaging_in_linear_power():
    p = np.array([[1.0, 100.0], [1.0, 100.0]], np.float32)   # 0 dB and 20 dB
    m, n = block_mean_power(p, 2)
    assert n[0, 0] == 4
    assert power_to_db(m)[0, 0] == pytest.approx(10 * np.log10(50.5), abs=1e-4)   # not 10 dB (mean of dB)


def test_averaging_ignores_nan():
    p = np.array([[1.0, np.nan], [1.0, 1.0]], np.float32)
    m, n = block_mean_power(p, 2)
    assert n[0, 0] == 3 and m[0, 0] == pytest.approx(1.0)


def test_bootstrap_identical_with_seed():
    rng = np.random.default_rng(3)
    blocks = block_index((500, 500)).ravel()
    truth = rng.random(blocks.size) < 0.1
    pa = truth ^ (rng.random(blocks.size) < 0.05)
    pb = truth ^ (rng.random(blocks.size) < 0.08)
    r1 = score_methods(truth, {"a": pa, "b": pb}, blocks)
    r2 = score_methods(truth, {"a": pa, "b": pb}, blocks)
    assert r1[0] == r2[0]
    assert np.array_equal(r1[1]["a"], r2[1]["a"])
    assert np.array_equal(Bootstrap(blocks).w, Bootstrap(blocks).w)


def test_block_index_5km():
    b = block_index((250, 250))
    assert len(np.unique(b)) == 4 and b[0, 0] != b[0, 125] and b[0, 0] == b[124, 124]


def test_detector_rules():
    lr_hh = np.array([-4.0, -4.0, 3.5, 3.5, 0.0], np.float32)
    lr_hv = np.array([-4.0, -4.0, 1.0, 2.0, 0.0], np.float32)
    post_hh = np.array([-20.0, -5.0, -5.0, -5.0, -5.0], np.float32)
    post_hv = np.array([-25.0, -25.0, -10.0, -10.0, -10.0], np.float32)
    t_hh = np.full(5, -12.0, np.float32)
    t_hv = np.full(5, -18.0, np.float32)
    assert open_water(lr_hh, post_hh, t_hh).tolist() == [True, False, False, False, False]
    assert twosided_open(lr_hh, post_hh, post_hv, t_hh, t_hv).tolist() == [True, False, False, False, False]
    assert flooded_veg(lr_hh, lr_hv).tolist() == [False, False, True, False, False]
    # no threshold for a part -> the log-ratio cut alone
    nan = np.full(5, np.nan, np.float32)
    assert open_water(lr_hh, post_hh, nan).tolist() == [True, True, False, False, False]
    valid = np.array([True, True, True, True, False])
    perm = np.array([False, False, False, False, True])
    cls = classify(valid, perm, twosided_open(lr_hh, post_hh, post_hv, t_hh, t_hv), flooded_veg(lr_hh, lr_hv))
    assert cls.tolist() == [C.OPEN_WATER, C.DRY, C.FLOODED_VEG, C.DRY, C.PERMANENT]


def test_nanmedian3_uses_valid_neighbours_only():
    a = np.zeros((5, 5), np.float32)
    a[2, 2] = 10.0
    a[0, :] = 100.0
    valid = np.ones((5, 5), bool)
    valid[0, :] = False
    m = nanmedian3(a, valid)
    assert np.isnan(m[0, 0]) and m[2, 2] == 0.0 and m[1, 1] == 0.0
