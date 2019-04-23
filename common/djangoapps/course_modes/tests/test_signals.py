"""
Unit tests for the course_mode signals
"""
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta

import ddt
from mock import patch
from pytz import UTC

from course_modes.models import CourseMode
from course_modes.signals import _listen_for_course_publish
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory


@ddt.ddt
class CourseModeSignalTest(ModuleStoreTestCase):
    """
    Tests for the course_mode course_published signal.
    """

    def setUp(self):
        super(CourseModeSignalTest, self).setUp()
        self.end = datetime.now(tz=UTC).replace(microsecond=0) + timedelta(days=7)
        self.course = CourseFactory.create(end=self.end)
        CourseMode.objects.all().delete()

    def create_mode(
            self,
            mode_slug,
            mode_name,
            min_price=0,
            suggested_prices='',
            currency='usd',
            expiration_datetime=None,
    ):
        """
        Create a new course mode
        """
        return CourseMode.objects.get_or_create(
            course_id=self.course.id,
            mode_display_name=mode_name,
            mode_slug=mode_slug,
            min_price=min_price,
            suggested_prices=suggested_prices,
            currency=currency,
            _expiration_datetime=expiration_datetime,
        )

    def test_no_verified_mode(self):
        """ Verify expiration not updated by signal for non-verified mode. """
        course_mode, __ = self.create_mode('honor', 'honor')

        _listen_for_course_publish('store', self.course.id)
        course_mode.refresh_from_db()

        self.assertIsNone(course_mode.expiration_datetime)

    @ddt.data(1, 14, 30)
    def test_verified_mode(self, verification_window):
        """ Verify signal updates expiration to configured time period before course end for verified mode. """
        course_mode, __ = self.create_mode('verified', 'verified', 10)
        self.assertIsNone(course_mode.expiration_datetime)

        with patch('course_modes.models.CourseModeExpirationConfig.current') as config:
            instance = config.return_value
            instance.verification_window = timedelta(days=verification_window)

            _listen_for_course_publish('store', self.course.id)
            course_mode.refresh_from_db()

            self.assertEqual(course_mode.expiration_datetime, self.end - timedelta(days=verification_window))

    @ddt.data(1, 14, 30)
    def test_verified_mode_explicitly_set(self, verification_window):
        """ Verify signal does not update expiration for verified mode with explicitly set expiration. """
        course_mode, __ = self.create_mode('verified', 'verified', 10)
        course_mode.expiration_datetime_is_explicit = True
        self.assertIsNone(course_mode.expiration_datetime)

        with patch('course_modes.models.CourseModeExpirationConfig.current') as config:
            instance = config.return_value
            instance.verification_window = timedelta(days=verification_window)

            _listen_for_course_publish('store', self.course.id)
            course_mode.refresh_from_db()

            self.assertEqual(course_mode.expiration_datetime, self.end - timedelta(days=verification_window))

    def test_masters_mode(self):
        # create an xblock with verified group access
        verified_section = ItemFactory.create(
            category="sequential",
            metadata={'group_access': {50: [2]}}
        )
        # and a section with no restriction
        section2 = ItemFactory.create(
            category="sequential",
        )
        section3 = ItemFactory.create(
            category='sequential',
            metadata={'group_access': {50: [1]}}
        )
        with self.store.branch_setting(ModuleStoreEnum.Branch.draft_preferred):
            # create the master's mode. signal will add masters to the verified section
            self.create_mode('masters', 'masters')
            verified_section_ret = self.store.get_item(verified_section.location)
            section2_ret = self.store.get_item(section2.location)
            section3_ret = self.store.get_item(section3.location)
            # group 2 is verified. 7 is masters
            assert verified_section_ret.group_access[50] == [2, 7]
            assert section2_ret.group_access == {}
            assert section2_ret.group_access == {50: [1]}
