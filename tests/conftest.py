import pytest
import json
from tests import app

from core import db
from core.apis.decorators import Principal
from core.models.assignments import Assignment

@pytest.fixture(scope="session", autouse=True)
def temporaryTestAssignmentData():
    assignment_1 = Assignment(student_id=1, content='ESSAY T1')
    assignment_2 = Assignment(student_id=1, content='THESIS T1')
    assignment_3 = Assignment(student_id=2, content='ESSAY T2')
    assignment_4 = Assignment(student_id=2, content='THESIS T2')
    assignment_5 = Assignment(student_id=1, content='SOLUTION T1')

    db.session.add(assignment_1)
    db.session.add(assignment_2)
    db.session.add(assignment_3)
    db.session.add(assignment_4)
    db.session.add(assignment_5)

    db.session.flush()

    Assignment.submit(
        _id=assignment_1.id,
        teacher_id=1,
        principal=Principal(user_id=1, student_id=1)
    )

    Assignment.submit(
        _id=assignment_3.id,
        teacher_id=2,
        principal=Principal(user_id=2, student_id=2)
    )

    Assignment.submit(
        _id=assignment_4.id,
        teacher_id=2,
        principal=Principal(user_id=2, student_id=2)
    )

    db.session.commit()

    yield

    # delete all rows of assignment table (including those added by tests via API)
    db.session.query(Assignment).delete()
    db.session.commit()


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def h_student_1():
    headers = {
        'X-Principal': json.dumps({
            'student_id': 1,
            'user_id': 1
        })
    }

    return headers


@pytest.fixture
def h_student_2():
    headers = {
        'X-Principal': json.dumps({
            'student_id': 2,
            'user_id': 2
        })
    }

    return headers


@pytest.fixture
def h_teacher_1():
    headers = {
        'X-Principal': json.dumps({
            'teacher_id': 1,
            'user_id': 3
        })
    }

    return headers


@pytest.fixture
def h_teacher_2():
    headers = {
        'X-Principal': json.dumps({
            'teacher_id': 2,
            'user_id': 4
        })
    }

    return headers
