"""
Tests for ErrorBlock and NonStaffErrorBlock
"""


import unittest

import pytest
from opaque_keys.edx.locator import CourseLocator
from xblock.test.tools import unabc

from xmodule.error_module import ErrorBlock, NonStaffErrorBlock
from xmodule.modulestore.xml import CourseLocationManager
from xmodule.tests import get_test_system
from xmodule.x_module import STUDENT_VIEW


class SetupTestErrorBlock(unittest.TestCase):
    """Common setUp for use in ErrorBlock tests."""

    def setUp(self):
        super().setUp()
        self.system = get_test_system()
        self.course_id = CourseLocator('org', 'course', 'run')
        self.location = self.course_id.make_usage_key('foo', 'bar')
        self.valid_xml = "<problem>ABC \N{SNOWMAN}</problem>"
        self.error_msg = "Error"


class TestErrorBlock(SetupTestErrorBlock):
    """
    Tests for ErrorBlock
    """

    def test_error_block_xml_rendering(self):
        descriptor = ErrorBlock.from_xml(
            self.valid_xml,
            self.system,
            CourseLocationManager(self.course_id),
            self.error_msg
        )
        assert isinstance(descriptor, ErrorBlock)
        descriptor.xmodule_runtime = self.system
        context_repr = self.system.render(descriptor, STUDENT_VIEW).content
        assert self.error_msg in context_repr
        assert repr(self.valid_xml) in context_repr


class TestNonStaffErrorBlock(SetupTestErrorBlock):
    """
    Tests for NonStaffErrorBlock.
    """

    def test_non_staff_error_block_create(self):
        descriptor = NonStaffErrorBlock.from_xml(
            self.valid_xml,
            self.system,
            CourseLocationManager(self.course_id)
        )
        assert isinstance(descriptor, NonStaffErrorBlock)

    def test_from_xml_render(self):
        descriptor = NonStaffErrorBlock.from_xml(
            self.valid_xml,
            self.system,
            CourseLocationManager(self.course_id)
        )
        descriptor.xmodule_runtime = self.system
        context_repr = self.system.render(descriptor, STUDENT_VIEW).content
        assert self.error_msg not in context_repr
        assert repr(self.valid_xml) not in context_repr
