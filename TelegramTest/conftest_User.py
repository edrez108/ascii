import pytest


from user.Models import User


@pytest.fixture(autouse=True)
def create_dummy_user(tmpdir):


    """fixture to execute assert before and a test is run"""

    from conf_test_db import override_get_postgres_db
    database = next(override_get_postgres_db())
    new_user = User(phone_number="09101010101", password="852741")
    database.add(new_user)
    database.commit()

    yield  # this is where the testing happens


    # teardown

    database.query(User).filter(User.phone_number == "09101010101").delete()
    database.commit()
