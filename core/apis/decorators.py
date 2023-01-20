import json
from flask import request
from core.libs import assertions
from functools import wraps
from core.models.students import Student
from core.models.teachers import Teacher
from json.decoder import JSONDecodeError

class Principal:
    def __init__(self, user_id, student_id=None, teacher_id=None):
        self.user_id = user_id
        self.student_id = student_id
        self.teacher_id = teacher_id


def accept_payload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        incoming_payload = request.json
        return func(incoming_payload, *args, **kwargs)
    return wrapper


def auth_principal(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        p_str = request.headers.get('X-Principal')
        assertions.assert_auth(p_str is not None, 'principal not found')
        try:
            p_dict = json.loads(p_str)
        except JSONDecodeError:
            assertions.assert_valid(False, 'Invalid X-Principal header value')
        p = Principal(
            user_id=p_dict.get('user_id'),
            student_id=p_dict.get('student_id'),
            teacher_id=p_dict.get('teacher_id')
        )
        assertions.assert_auth(p.user_id is not None, 'user_id not found in principal')
        assertions.assert_valid(type(p.user_id)==int, 'user_id in header X-Principal should be an integer')

        if request.path.startswith('/student'):
            assertions.assert_true(p.student_id is not None, 'requester should be a student')
            assertions.assert_valid(type(p.student_id)==int, 'student_id in header X-Principal should be an integer')
            student = Student.get_by_id(p.student_id)
            assertions.assert_found(student, 'No student with this id was found')
            assertions.assert_auth(student.user_id == p.user_id, 'Wrong user_id for given student_id')
        elif request.path.startswith('/teacher'):
            assertions.assert_true(p.teacher_id is not None, 'requester should be a teacher')
            assertions.assert_valid(type(p.teacher_id)==int, 'teacher_id in header X-Principal should be an integer')
            teacher = Teacher.get_by_id(p.teacher_id)
            assertions.assert_found(teacher, 'No teacher with this id was found')
            assertions.assert_auth(teacher.user_id == p.user_id, 'Wrong user_id for given teacher_id')
        else:
            assertions.assert_found(None, 'No such api')

        return func(p, *args, **kwargs)
    return wrapper
