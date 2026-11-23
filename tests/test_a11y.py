import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from a11y.checks import (
    check_html_lang,
    check_img_alt,
    check_contrast,
    check_form_labels,
    contrast_ratio,
    run_all,
)
from a11y.report import generate_report, report_to_json


def test_html_lang_present():
    html = '<html lang="en"><body></body></html>'
    r = check_html_lang(html)
    assert r.passed is True


def test_html_lang_missing():
    html = "<html><body></body></html>"
    r = check_html_lang(html)
    assert r.passed is False


def test_img_alt_present():
    html = '<img src="x.png" alt="desc">'
    results = check_img_alt(html)
    assert all(r.passed for r in results)


def test_img_alt_missing():
    html = '<img src="x.png">'
    results = check_img_alt(html)
    assert any(not r.passed for r in results)


def test_contrast_ratio():
    ratio = contrast_ratio("#000000", "#ffffff")
    assert ratio > 20


def test_contrast_ratio_same():
    ratio = contrast_ratio("#ffffff", "#ffffff")
    assert ratio == 1.0


def test_form_labels_missing():
    html = '<input type="text" id="name">'
    results = check_form_labels(html)
    assert any(not r.passed for r in results)


def test_form_labels_present():
    html = '<label for="name">Name</label><input type="text" id="name">'
    results = check_form_labels(html)
    assert all(r.passed for r in results)


def test_run_all():
    html = '<html lang="en"><body><img src="x.png" alt="d"></body></html>'
    results = run_all(html)
    assert len(results) >= 3
    assert all(isinstance(r.passed, bool) for r in results)


def test_generate_report():
    html = '<html lang="en"><body></body></html>'
    report = generate_report(html)
    assert "total" in report
    assert "passed" in report
    assert "failed" in report
    assert "checks" in report


def test_report_to_json():
    html = '<html lang="en"><body></body></html>'
    j = report_to_json(html)
    data = json.loads(j)
    assert data["failed"] == 0
