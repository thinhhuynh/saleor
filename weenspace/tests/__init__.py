import pytest

# We want to have PyTest assert introspection in the API tests
pytest.register_assert_rewrite("weenspace.tests.e2e")
