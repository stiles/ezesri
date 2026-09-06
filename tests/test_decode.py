import json

import pandas as pd
import pytest

from ezesri.utils import (
    build_codebook,
    coded_value_map,
    decode_dataframe,
    write_ndjson,
)


def coded_domain(*pairs):
    return {
        "type": "codedValue",
        "name": "TestDomain",
        "codedValues": [{"code": code, "name": name} for code, name in pairs],
    }


STATUS_METADATA = {
    "name": "Permits",
    "fields": [
        {"name": "OBJECTID", "type": "esriFieldTypeOID"},
        {
            "name": "STATUS",
            "type": "esriFieldTypeSmallInteger",
            "domain": coded_domain((1, "Issued"), (2, "Pending"), (3, "Under construction")),
        },
        {"name": "FILED", "type": "esriFieldTypeDate"},
    ],
}


def test_coded_value_map_builds_lookup():
    mapping = coded_value_map(coded_domain((1, "Issued")))
    assert mapping[1] == "Issued"
    # String form registered too, since value and code types can differ
    assert mapping["1"] == "Issued"


def test_coded_value_map_ignores_range_domains():
    assert coded_value_map({"type": "range", "range": [0, 10]}) is None


def test_coded_value_map_handles_no_domain():
    assert coded_value_map(None) is None


def test_domains_are_decoded():
    df = pd.DataFrame({"OBJECTID": [1, 2, 3], "STATUS": [1, 3, 2]})
    decoded, report = decode_dataframe(df, STATUS_METADATA, parse_dates=False)

    assert list(decoded["STATUS"]) == ["Issued", "Under construction", "Pending"]
    assert "STATUS" in report["decoded_fields"]


def test_string_codes_match_integer_domain():
    """A field whose values arrive as strings still matches integer codes."""
    df = pd.DataFrame({"STATUS": ["1", "2"]})
    decoded, _ = decode_dataframe(df, STATUS_METADATA, parse_dates=False)
    assert list(decoded["STATUS"]) == ["Issued", "Pending"]


def test_unmapped_codes_are_kept_and_reported():
    """A code with no label is left alone rather than blanked out."""
    df = pd.DataFrame({"STATUS": [1, 99]})
    decoded, report = decode_dataframe(df, STATUS_METADATA, parse_dates=False)

    assert list(decoded["STATUS"]) == ["Issued", 99]
    assert report["unmapped_codes"]["STATUS"] == [99]


def test_nulls_survive_decoding():
    df = pd.DataFrame({"STATUS": [1, None]})
    decoded, report = decode_dataframe(df, STATUS_METADATA, parse_dates=False)

    assert decoded["STATUS"].iloc[0] == "Issued"
    assert pd.isna(decoded["STATUS"].iloc[1])
    assert "STATUS" not in report["unmapped_codes"]


def test_epoch_milliseconds_become_timestamps():
    """Esri hands back dates as epoch milliseconds."""
    df = pd.DataFrame({"FILED": [1735689600000, 1735776000000]})
    decoded, report = decode_dataframe(df, STATUS_METADATA, decode_domains=False)

    assert str(decoded["FILED"].iloc[0]) == "2025-01-01 00:00:00+00:00"
    assert report["date_fields"] == ["FILED"]


def test_iso_date_strings_are_parsed():
    """Some servers return ISO strings instead of epoch milliseconds."""
    df = pd.DataFrame({"FILED": ["2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z"]})
    decoded, _ = decode_dataframe(df, STATUS_METADATA, decode_domains=False)

    assert str(decoded["FILED"].iloc[0]) == "2025-01-01 00:00:00+00:00"


def test_null_dates_become_nat():
    df = pd.DataFrame({"FILED": [1735689600000, None]})
    decoded, _ = decode_dataframe(df, STATUS_METADATA, decode_domains=False)
    assert pd.isna(decoded["FILED"].iloc[1])


def test_raw_codes_opt_out():
    df = pd.DataFrame({"STATUS": [1, 2]})
    decoded, report = decode_dataframe(df, STATUS_METADATA, decode_domains=False, parse_dates=False)

    assert list(decoded["STATUS"]) == [1, 2]
    assert report["decoded_fields"] == []


def test_original_dataframe_is_not_mutated():
    df = pd.DataFrame({"STATUS": [1, 2]})
    decode_dataframe(df, STATUS_METADATA, parse_dates=False)
    assert list(df["STATUS"]) == [1, 2]


def test_missing_columns_are_skipped():
    """Metadata describing fields the query did not return is harmless."""
    df = pd.DataFrame({"OBJECTID": [1]})
    decoded, report = decode_dataframe(df, STATUS_METADATA)
    assert report["decoded_fields"] == []
    assert len(decoded) == 1


def test_empty_dataframe_is_returned_unchanged():
    df = pd.DataFrame()
    decoded, report = decode_dataframe(df, STATUS_METADATA)
    assert decoded.empty
    assert report["decoded_fields"] == []


# --- Subtypes -------------------------------------------------------------

SUBTYPE_METADATA = {
    "name": "Utilities",
    "subtypeField": "KIND",
    "subtypes": [
        {
            "code": 1,
            "name": "Water",
            "domains": {"MATERIAL": coded_domain(("A", "Ductile iron"), ("B", "PVC"))},
        },
        {
            "code": 2,
            "name": "Sewer",
            "domains": {"MATERIAL": coded_domain(("A", "Clay"), ("B", "Concrete"))},
        },
    ],
    "fields": [
        {"name": "KIND", "type": "esriFieldTypeSmallInteger"},
        {"name": "MATERIAL", "type": "esriFieldTypeString"},
    ],
}


def test_subtype_field_is_decoded():
    df = pd.DataFrame({"KIND": [1, 2], "MATERIAL": ["A", "A"]})
    decoded, _ = decode_dataframe(df, SUBTYPE_METADATA, parse_dates=False)
    assert list(decoded["KIND"]) == ["Water", "Sewer"]


def test_subtype_domains_override_per_row():
    """The same code means different things depending on the subtype."""
    df = pd.DataFrame({"KIND": [1, 2], "MATERIAL": ["A", "A"]})
    decoded, _ = decode_dataframe(df, SUBTYPE_METADATA, parse_dates=False)
    assert list(decoded["MATERIAL"]) == ["Ductile iron", "Clay"]


NUMERIC_SUBTYPE_METADATA = {
    "name": "Structures",
    "subtypeField": "FEATURE_CODE",
    "subtypes": [
        {
            "code": 10,
            "name": "Rail Bridge",
            "domains": {"STATUS": coded_domain((1, "In use"), (2, "Disused"))},
        },
        {
            "code": 20,
            "name": "Road Bridge",
            "domains": {"STATUS": coded_domain((1, "Open"), (2, "Closed"))},
        },
    ],
    "fields": [
        {"name": "FEATURE_CODE", "type": "esriFieldTypeInteger"},
        {"name": "STATUS", "type": "esriFieldTypeInteger"},
    ],
}


def test_subtype_decoding_of_numeric_column():
    """Labels must be writable into a numeric column without a dtype error."""
    df = pd.DataFrame({"FEATURE_CODE": [10, 20, 10], "STATUS": [1, 1, 2]})
    decoded, report = decode_dataframe(df, NUMERIC_SUBTYPE_METADATA, parse_dates=False)

    assert list(decoded["STATUS"]) == ["In use", "Open", "Disused"]
    assert list(decoded["FEATURE_CODE"]) == ["Rail Bridge", "Road Bridge", "Rail Bridge"]
    assert "STATUS" in report["decoded_fields"]


def test_subtype_rows_without_override_keep_their_codes():
    """A subtype code with no matching definition is left alone."""
    df = pd.DataFrame({"FEATURE_CODE": [10, 99], "STATUS": [1, 1]})
    decoded, _ = decode_dataframe(df, NUMERIC_SUBTYPE_METADATA, parse_dates=False)

    assert decoded["STATUS"].iloc[0] == "In use"
    assert decoded["STATUS"].iloc[1] == 1


def test_codebook_records_domains():
    book = build_codebook(STATUS_METADATA)
    assert book["layer"] == "Permits"
    assert book["fields"]["STATUS"]["domain"]["codedValues"][3] == "Under construction"
    assert book["fields"]["FILED"]["decodedAs"].startswith("ISO-8601")


def test_codebook_records_subtypes():
    book = build_codebook(SUBTYPE_METADATA)
    assert book["subtypeField"] == "KIND"
    assert book["subtypes"][1]["name"] == "Water"
    assert book["subtypes"][2]["domains"]["MATERIAL"]["A"] == "Clay"


def test_codebook_is_json_serializable():
    json.dumps(build_codebook(SUBTYPE_METADATA), default=str)


# --- NDJSON serialization -------------------------------------------------


def test_ndjson_writes_timestamps(tmp_path):
    """Decoded timestamps must not break the NDJSON writer."""
    df = pd.DataFrame({"FILED": pd.to_datetime([1735689600000], unit="ms", utc=True)})
    out = tmp_path / "out.ndjson"

    write_ndjson(df, str(out))

    record = json.loads(out.read_text().strip())
    assert record["FILED"].startswith("2025-01-01T00:00:00")


def test_ndjson_writes_null_for_nat(tmp_path):
    df = pd.DataFrame({"FILED": pd.to_datetime([None], unit="ms", utc=True)})
    out = tmp_path / "out.ndjson"

    write_ndjson(df, str(out))

    assert json.loads(out.read_text().strip())["FILED"] is None


def test_ndjson_writes_null_for_nan(tmp_path):
    """NaN is not valid JSON, so it is written as null."""
    df = pd.DataFrame({"VALUE": [float("nan")]})
    out = tmp_path / "out.ndjson"

    write_ndjson(df, str(out))

    assert json.loads(out.read_text().strip())["VALUE"] is None
