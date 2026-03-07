"""Tests for feedback system."""

import yaml

from wt_project_base.feedback import (
    FeedbackLesson,
    FeedbackStore,
    SuggestedFix,
    check_identifying_content,
    validate_lesson,
)


def _make_lesson(**kwargs):
    defaults = {
        "rule_id": "file-size-limit",
        "issue": "false_positive",
        "context": "Generated migration files often exceed the limit",
    }
    defaults.update(kwargs)
    return FeedbackLesson(**defaults)


def test_valid_lesson_no_errors():
    lesson = _make_lesson()
    assert validate_lesson(lesson) == []


def test_invalid_issue_type():
    lesson = _make_lesson(issue="bad_type")
    errors = validate_lesson(lesson)
    assert len(errors) == 1
    assert "Invalid issue type" in errors[0]


def test_missing_rule_id():
    lesson = _make_lesson(rule_id="")
    errors = validate_lesson(lesson)
    assert any("rule_id" in e for e in errors)


def test_missing_context():
    lesson = _make_lesson(context="")
    errors = validate_lesson(lesson)
    assert any("context" in e for e in errors)


def test_timestamp_auto_set():
    lesson = _make_lesson()
    assert lesson.timestamp  # should be auto-set


def test_store_append_and_load(tmp_path):
    store_path = tmp_path / "feedback.yaml"
    store = FeedbackStore(store_path)
    lesson = _make_lesson()
    errors = store.append(lesson)
    assert errors == []

    # Reload from file
    store2 = FeedbackStore(store_path)
    lessons = store2.get_lessons()
    assert len(lessons) == 1
    assert lessons[0].rule_id == "file-size-limit"


def test_store_rejects_invalid(tmp_path):
    store_path = tmp_path / "feedback.yaml"
    store = FeedbackStore(store_path)
    lesson = _make_lesson(issue="bad_type")
    errors = store.append(lesson)
    assert len(errors) > 0
    assert store.get_lessons() == []


def test_store_with_suggested_fix(tmp_path):
    store_path = tmp_path / "feedback.yaml"
    store = FeedbackStore(store_path)
    fix = SuggestedFix(type="add_exclude", value="*.migration.*")
    lesson = _make_lesson(suggested_fix=fix)
    store.append(lesson)

    store2 = FeedbackStore(store_path)
    loaded = store2.get_lessons()[0]
    assert loaded.suggested_fix is not None
    assert loaded.suggested_fix.type == "add_exclude"


def test_export_produces_yaml(tmp_path):
    store_path = tmp_path / "feedback.yaml"
    store = FeedbackStore(store_path)
    store.append(_make_lesson())
    export = store.export()
    assert "feedback:" in export
    assert "file-size-limit" in export
    # Should not contain timestamp in exported entries
    parsed = yaml.safe_load(export.split("\n\n", 1)[-1])
    assert "feedback" in parsed


def test_export_empty(tmp_path):
    store_path = tmp_path / "feedback.yaml"
    store = FeedbackStore(store_path)
    export = store.export()
    assert "Lessons: 0" in export


def test_identifying_content_detects_paths():
    lesson = _make_lesson(context="Found in /home/user/project/src/main.py")
    warns = check_identifying_content(lesson)
    assert len(warns) > 0
    assert "path" in warns[0].lower()


def test_identifying_content_clean():
    lesson = _make_lesson(context="Generated files often exceed the limit")
    warns = check_identifying_content(lesson)
    assert warns == []
