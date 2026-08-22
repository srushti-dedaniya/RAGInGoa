from app.config.settings import Settings


def test_language_specific_dataset_and_index_paths():
    settings = Settings(
        DATASET_PATH_EN="data/en.jsonl",
        DATASET_PATH_HI="data/hi.jsonl",
        DATASET_PATH_MR="data/mr.jsonl",
        VECTOR_DB_PATH_EN="index/en",
        VECTOR_DB_PATH_HI="index/hi",
        VECTOR_DB_PATH_MR="index/mr",
    )

    assert settings.DATASET_LANGUAGE == "en"
    assert settings.dataset_path_for("en-IN").parts[-2:] == ("data", "en.jsonl")
    assert settings.dataset_path_for("hi-IN").parts[-2:] == ("data", "hi.jsonl")
    assert settings.dataset_path_for("mr-IN").parts[-2:] == ("data", "mr.jsonl")
    assert settings.index_path_for("en-IN").parts[-2:] == ("index", "en")
    assert settings.index_path_for("hi-IN").parts[-2:] == ("index", "hi")
    assert settings.index_path_for("mr-IN").parts[-2:] == ("index", "mr")
