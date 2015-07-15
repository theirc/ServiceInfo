import datetime
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings
from email_user.tests.factories import EmailUserFactory

from ..models import JiraUpdateRecord, Service
from ..tasks import process_jira_work
from ..utils import absolute_url
from .factories import ServiceFactory, ProviderFactory, SelectionCriterionFactory, FeedbackFactory, \
    RequestForServiceFactory


class JiraUpdateRecordModelTest(TestCase):
    def test_blank_type_not_allowed(self):
        with self.assertRaises(Exception) as cm:
            JiraUpdateRecord.objects.create(update_type='')
        self.assertTrue('non-blank update_type' in str(cm.exception))

    def test_unrecognized_type_not_allowed(self):
        with self.assertRaises(Exception) as cm:
            JiraUpdateRecord.objects.create(update_type='alsdkfjasldkfj')
        self.assertTrue('unrecognized update_type' in str(cm.exception))

    def test_types_require_service(self):
        require_service_types = JiraUpdateRecord.SERVICE_CHANGE_UPDATE_TYPES
        for update_type in require_service_types:
            with self.assertRaises(Exception) as cm:
                JiraUpdateRecord.objects.create(update_type=update_type)
            self.assertTrue(
                'must specify service' in str(cm.exception),
                msg='Unexpected exception message (%s) for %s' % (str(cm.exception), update_type))

    def test_types_require_no_provider(self):
        provider = ProviderFactory()
        disallow_provider_types = JiraUpdateRecord.SERVICE_CHANGE_UPDATE_TYPES
        for update_type in disallow_provider_types:
            with self.assertRaises(Exception) as cm:
                JiraUpdateRecord.objects.create(update_type=update_type, provider=provider)
            self.assertTrue(
                'must not specify provider' in str(cm.exception),
                msg='Unexpected exception message (%s) for %s' % (str(cm.exception), update_type))

    def test_types_require_provider(self):
        require_provider_types = JiraUpdateRecord.PROVIDER_CHANGE_UPDATE_TYPES
        for update_type in require_provider_types:
            with self.assertRaises(Exception) as cm:
                JiraUpdateRecord.objects.create(update_type=update_type)
            self.assertTrue(
                'must specify provider' in str(cm.exception),
                msg='Unexpected exception message (%s) for %s' % (str(cm.exception), update_type))

    def test_types_require_no_service(self):
        service = ServiceFactory()
        disallow_service_types = JiraUpdateRecord.PROVIDER_CHANGE_UPDATE_TYPES
        for update_type in disallow_service_types:
            with self.assertRaises(Exception) as cm:
                JiraUpdateRecord.objects.create(update_type=update_type, service=service)
            self.assertTrue(
                'must not specify service' in str(cm.exception),
                msg='Unexpected exception message (%s) for %s' % (str(cm.exception), update_type))

    def test_feedback_requires_feedback(self):
        with self.assertRaises(Exception) as cm:
            JiraUpdateRecord.objects.create(update_type=JiraUpdateRecord.FEEDBACK,
                                            feedback=None)
        self.assertIn('must specify feedback', str(cm.exception))

    def test_request_for_service_requires_request(self):
        with self.assertRaises(Exception) as cm:
            JiraUpdateRecord.objects.create(update_type=JiraUpdateRecord.REQUEST_FOR_SERVICE,
                                            request_for_service=None)
        self.assertIn('must specify request', str(cm.exception))


class MockJiraTestMixin(object):
    def setup_issue_key(self, mock_JIRA):
        issue_key = 'ABC-123'
        attrs = {'return_value.create_issue.return_value.key': issue_key}
        mock_JIRA.configure_mock(**attrs)
        return issue_key


@mock.patch('services.jira_support.JIRA', autospec=True)
class JiraProviderChangeTest(MockJiraTestMixin, TestCase):
    def setUp(self):
        self.test_provider = ProviderFactory()

    def test_creating_provider_doesnt_create_jira_record(self, mock_JIRA):
        with self.assertRaises(JiraUpdateRecord.DoesNotExist):
            self.jira_record = self.test_provider.jira_records.get(
                update_type=JiraUpdateRecord.PROVIDER_CHANGE)

    def test_provider_notify_jira_of_change_creates_record(self, mock_JIRA):
        self.test_provider.notify_jira_of_change()
        jira_record = self.test_provider.jira_records.get(
            update_type=JiraUpdateRecord.PROVIDER_CHANGE)
        self.assertEqual(self.test_provider, jira_record.provider)

    def test_provider_change_jira_work(self, mock_JIRA):
        self.test_provider.notify_jira_of_change()
        jira_record = self.test_provider.jira_records.get(
            update_type=JiraUpdateRecord.PROVIDER_CHANGE)
        self.assertEqual('', jira_record.jira_issue_key)
        issue_key = self.setup_issue_key(mock_JIRA)
        jira_record.do_jira_work()
        expected_duedate = datetime.date.today() + datetime.timedelta(days=settings.JIRA_DUEIN_DAYS)
        mock_JIRA.return_value.create_issue.assert_called_with(
            description=mock.ANY,
            project={'key': settings.JIRA_SERVICES_PROJECT_KEY},
            issuetype={'name': 'Task'},
            duedate=str(expected_duedate),
            summary="Changed provider from %s" % str(self.test_provider),
        )
        description = mock_JIRA.return_value.create_issue.call_args[1]['description']
        self.assertIn(absolute_url(self.test_provider.get_admin_edit_url()), description)
        self.assertIn(self.test_provider.name_en, description)
        jira_record = JiraUpdateRecord.objects.get(pk=jira_record.pk)
        self.assertEqual(issue_key, jira_record.jira_issue_key)


@mock.patch('services.jira_support.JIRA', autospec=True)
class JiraApproveServiceTest(MockJiraTestMixin, TestCase):
    def setUp(self):
        self.test_service = ServiceFactory(location='POINT(5 23)')
        self.jira_record = self.test_service.jira_records.get(
            update_type=JiraUpdateRecord.NEW_SERVICE)
        self.staff_user = EmailUserFactory(is_staff=True)

    def test_approving_service_creates_record(self, mock_JIRA):
        self.test_service.staff_approve(self.staff_user)
        self.assertTrue(self.test_service.jira_records.filter(
            update_type=JiraUpdateRecord.APPROVE_SERVICE).exists())

    def test_rejecting_service_creates_record(self, mock_JIRA):
        self.test_service.staff_reject(self.staff_user)
        self.assertTrue(self.test_service.jira_records.filter(
            update_type=JiraUpdateRecord.REJECT_SERVICE).exists())

    def test_approval_comments_on_issue(self, mock_JIRA):
        self.test_service.staff_approve(self.staff_user)
        issue_key = self.setup_issue_key(mock_JIRA)
        self.jira_record.do_jira_work()
        record2 = self.test_service.jira_records.get(
            update_type=JiraUpdateRecord.APPROVE_SERVICE)
        record2.do_jira_work()
        self.assertEqual(self.jira_record.jira_issue_key, record2.jira_issue_key)
        call_args, call_kwargs = mock_JIRA.return_value.add_comment.call_args
        self.assertEqual(
            (issue_key, "The new service was approved by %s." % self.staff_user.email),
            call_args)
        self.assertEqual({}, call_kwargs)

    def test_rejecting_comments_on_issue(self, mock_JIRA):
        self.test_service.staff_reject(self.staff_user)
        issue_key = self.setup_issue_key(mock_JIRA)
        self.jira_record.do_jira_work()
        record2 = self.test_service.jira_records.get(
            update_type=JiraUpdateRecord.REJECT_SERVICE)
        record2.do_jira_work()
        self.assertEqual(self.jira_record.jira_issue_key, record2.jira_issue_key)
        call_args, call_kwargs = mock_JIRA.return_value.add_comment.call_args
        self.assertEqual(
            (issue_key, "The new service was rejected by %s." % self.staff_user.email),
            call_args)
        self.assertEqual({}, call_kwargs)


@mock.patch('services.jira_support.JIRA', autospec=True)
class JiraNewServiceTest(MockJiraTestMixin, TestCase):
    def setUp(self):
        self.test_service = ServiceFactory(location='POINT(5 23)')
        self.jira_record = self.test_service.jira_records.get(
            update_type=JiraUpdateRecord.NEW_SERVICE)
        self.staff_user = EmailUserFactory(is_staff=True)

    def test_create_issue_sets_keyval(self, mock_JIRA):
        self.assertEqual('', self.jira_record.jira_issue_key)
        issue_key = self.setup_issue_key(mock_JIRA)
        self.jira_record.do_jira_work()
        self.assertEqual(issue_key, self.jira_record.jira_issue_key)

    def test_create_issue_kwargs(self, mock_JIRA):
        self.test_service.sunday_open = datetime.time(11, 10)
        self.test_service.sunday_close = datetime.time(12, 10)
        self.test_service.saturday_open = datetime.time(17, 18)
        self.test_service.saturday_close = datetime.time(19, 18)
        self.test_service.save()
        self.test_service.provider.focal_point_phone_number = '12-345678'
        self.test_service.provider.number_of_monthly_beneficiaries = '31415'
        self.test_service.provider.save()
        SelectionCriterionFactory(
            service=self.test_service,
            text_en="Must be 18",
            text_ar="Must have passport",
            text_fr="Must have transportation"
        )
        SelectionCriterionFactory(
            service=self.test_service,
            text_en="Must be 21",
            text_ar="Must have shoes",
            text_fr="Must be citizen"
        )
        self.setup_issue_key(mock_JIRA)
        self.jira_record = JiraUpdateRecord.objects.get(pk=self.jira_record.pk)
        self.jira_record.do_jira_work()
        call_args, call_kwargs = mock_JIRA.return_value.create_issue.call_args
        # Expecting: summary, project, issuetype, description, duedate
        self.assertTrue('summary' in call_kwargs)
        self.assertTrue('new service' in call_kwargs['summary'].lower())
        self.assertTrue(self.test_service.provider.name_en in call_kwargs['summary'])
        self.assertTrue('project' in call_kwargs)
        self.assertEqual({'key': settings.JIRA_SERVICES_PROJECT_KEY}, call_kwargs['project'])
        self.assertTrue('issuetype' in call_kwargs)
        self.assertEqual({'name': 'Task'}, call_kwargs['issuetype'])
        self.assertTrue('description' in call_kwargs)
        admin_url = absolute_url(self.test_service.get_admin_edit_url())
        self.assertTrue(
            admin_url in call_kwargs['description'],
            msg='%s not found in %s' % (admin_url, call_kwargs['description']))
        self.assertIn('11:10', call_kwargs['description'])
        self.assertIn('17:18', call_kwargs['description'])
        self.assertIn('Must be 18', call_kwargs['description'])
        self.assertIn('Must have shoes', call_kwargs['description'])
        self.assertIn('12-345678', call_kwargs['description'])
        self.assertIn('31415', call_kwargs['description'])
        self.assertTrue('duedate' in call_kwargs)
        expected_duedate = datetime.date.today() + datetime.timedelta(days=settings.JIRA_DUEIN_DAYS)
        self.assertEqual(str(expected_duedate), call_kwargs['duedate'])
        # We've tested 5, ensure that is all that were passed
        self.assertEqual(5, len(call_kwargs))
        self.assertEqual((), call_args)

    def test_create_issue_kwargs_for_update(self, mock_JIRA):
        self.test_service.update_of = ServiceFactory()
        self.jira_record.update_type = JiraUpdateRecord.CHANGE_SERVICE
        self.jira_record.save()
        self.setup_issue_key(mock_JIRA)
        self.jira_record.do_jira_work()
        call_args, call_kwargs = mock_JIRA.return_value.create_issue.call_args
        # Only checking summary as that has the essentially different value
        # from what the "new service" case sets.
        self.assertTrue('summary' in call_kwargs)
        self.assertTrue('changed service' in call_kwargs['summary'].lower())
        self.assertTrue(self.test_service.provider.name_en in call_kwargs['summary'])

    def test_new_service_then_approve_before_task(self, mock_JIRA):
        # If a service is approved before we try to do the JIRA work,
        # the JIRA work gracefully works
        self.jira_record.update_type = JiraUpdateRecord.NEW_SERVICE
        self.jira_record.save()
        self.test_service.staff_approve(self.staff_user)
        self.setup_issue_key(mock_JIRA)
        self.jira_record.do_jira_work()

    def test_change_service_then_approve_before_task(self, mock_JIRA):
        # If a service is approved before we try to do the JIRA work,
        # the JIRA work gracefully works
        self.test_service.update_of = ServiceFactory()
        self.jira_record.update_type = JiraUpdateRecord.CHANGE_SERVICE
        self.jira_record.save()
        self.test_service.staff_approve(self.staff_user)
        self.setup_issue_key(mock_JIRA)
        self.jira_record.do_jira_work()

    def test_create_jira_issue_noop_if_already_created(self, mock_JIRA):
        test_key_val = 'ALREADY-SET'
        self.jira_record.jira_issue_key = test_key_val
        self.jira_record.save()
        self.jira_record.do_jira_work()
        self.assertFalse(mock_JIRA.called)
        self.assertEqual(test_key_val, self.jira_record.jira_issue_key)

    def test_create_jira_issue_uses_provided_jira(self, mock_JIRA):
        # This 2nd mock will take precendence by default, we test to
        # ensure that if the original mock is passed in it is called.
        with mock.patch('services.jira_support.JIRA') as JIRA:
            issue_key = self.setup_issue_key(mock_JIRA)
            self.jira_record.do_jira_work(mock_JIRA())
            self.assertFalse(JIRA.called)
            self.assertEqual(issue_key, self.jira_record.jira_issue_key)

    def test_cancel_current_service_creates_jira_issue(self, mock_JIRA):
        service = self.jira_record.service
        service.status = service.STATUS_CURRENT
        service.save()
        service.cancel()
        self.jira_record = \
            service.jira_records.get(update_type=JiraUpdateRecord.CANCEL_CURRENT_SERVICE)
        self.jira_record.save()
        self.setup_issue_key(mock_JIRA)
        self.jira_record.do_jira_work()
        call_args, call_kwargs = mock_JIRA.return_value.create_issue.call_args
        # Only checking summary as that has the essentially different value
        # from what the "new service" case sets.
        self.assertTrue('summary' in call_kwargs)
        self.assertTrue('canceled service' in call_kwargs['summary'].lower())
        self.assertTrue(self.test_service.provider.name_en in call_kwargs['summary'])

    def test_cancel_draft_new_service_comments_on_jira_issue(self, mock_JIRA):
        # If we cancel a pending new service, it adds a comment to the
        # existing JIRA issue.

        # First create a record from when the draft service was started
        issue_key = 'XXX-123'
        self.jira_record.jira_issue_key = issue_key
        self.jira_record.save()

        service = self.jira_record.service
        service.status = service.STATUS_DRAFT
        service.save()

        service.cancel()
        cancel_record = service.jira_records.get(update_type=JiraUpdateRecord.CANCEL_DRAFT_SERVICE)

        cancel_record.do_jira_work()
        call_args, call_kwargs = mock_JIRA.return_value.add_comment.call_args
        # Only checking summary as that has the essentially different value
        # from what the "new service" case sets.
        self.assertEqual(issue_key, call_args[0])
        self.assertIn('change was canceled', call_args[1])
        # We should NOT have created a new JIRA record
        self.assertFalse(mock_JIRA.return_value.create_issue.called)

    def test_cancel_draft_service_change_comments_on_jira_issue(self, mock_JIRA):
        # If we cancel a pending change to a current service, it adds a comment
        # to the existing jira issue.

        # make the service we're canceling look like a change to an existing service
        existing_service = ServiceFactory(status=Service.STATUS_CURRENT)
        draft_service = ServiceFactory(
            update_of=existing_service,
            status=Service.STATUS_DRAFT,
        )
        # Pretend we've created a JIRA issue when the draft was started.
        issue_key = 'XXX-123'
        draft_service.jira_records.update(jira_issue_key=issue_key)

        # Now cancel the draft
        draft_service.cancel()

        # We should get a new jira update record created
        cancel_record = \
            draft_service.jira_records.get(update_type=JiraUpdateRecord.CANCEL_DRAFT_SERVICE)
        # run it:
        cancel_record.do_jira_work()
        call_args, call_kwargs = mock_JIRA.return_value.add_comment.call_args
        # Only checking summary as that has the essentially different value
        # from what the "new service" case sets.
        self.assertEqual(issue_key, call_args[0])
        self.assertIn('change was canceled', call_args[1])
        record = JiraUpdateRecord.objects.get(pk=cancel_record.pk)
        self.assertEqual(issue_key, record.jira_issue_key)
        # We should NOT have created a new JIRA record
        self.assertFalse(mock_JIRA.return_value.create_issue.called)

    def test_replacing_a_draft_comments_on_jira_issue(self, mock_JIRA):
        draft_service = ServiceFactory(status=Service.STATUS_DRAFT)
        # Pretend we've created a JIRA issue when the draft was started.
        issue_key = 'XXX-123'
        draft_service.jira_records.update(jira_issue_key=issue_key)
        mock_JIRA.return_value.create_issue.reset_mock()  # Forget we "created a jira record"
        # Now edit the draft
        new_draft = ServiceFactory(update_of=draft_service, status=Service.STATUS_DRAFT)
        # We should have a new update record
        jira_record = new_draft.jira_records.get(update_type=JiraUpdateRecord.SUPERSEDED_DRAFT)
        jira_record.do_jira_work()
        # We should NOT have created another JIRA record
        self.assertFalse(mock_JIRA.return_value.create_issue.called)
        # We add a comment with links to the old and new data
        call_args, call_kwargs = mock_JIRA.return_value.add_comment.call_args
        self.assertEqual(issue_key, call_args[0])
        self.assertIn(new_draft.get_admin_edit_url(), call_args[1])


# These settings are not used for real since we don't talk to JIRA
# actually but they are needed for the task to try to do any work.
@override_settings(JIRA_USER='dummy', JIRA_PASSWORD='dummy', JIRA_SERVER='nonsense')
@mock.patch('services.jira_support.JIRA', autospec=True)
class JiraTaskTest(MockJiraTestMixin, TestCase):
    def setUp(self):
        self.test_service = ServiceFactory()

    def test_missing_config_does_nothing(self, mock_JIRA):
        settings.JIRA_USER = ''
        self.assertEqual(1, JiraUpdateRecord.objects.filter(jira_issue_key='').count())
        process_jira_work()
        self.assertEqual(1, JiraUpdateRecord.objects.filter(jira_issue_key='').count())

    def test_process_single_record(self, mock_JIRA):
        self.assertEqual(1, JiraUpdateRecord.objects.filter(jira_issue_key='').count())
        self.setup_issue_key(mock_JIRA)
        process_jira_work()
        self.assertEqual(0, JiraUpdateRecord.objects.filter(jira_issue_key='').count())

    def test_process_multiple_records(self, mock_JIRA):
        ServiceFactory()
        self.assertEqual(2, JiraUpdateRecord.objects.filter(jira_issue_key='').count())
        self.setup_issue_key(mock_JIRA)
        process_jira_work()
        self.assertEqual(0, JiraUpdateRecord.objects.filter(jira_issue_key='').count())


@mock.patch('services.jira_support.JIRA', autospec=True)
class JiraFeedbackTest(MockJiraTestMixin, TestCase):
    def setUp(self):
        self.test_service = ServiceFactory()

    def test_creating_feedback_sends_data_to_jira(self, mock_JIRA):
        for delivered in [False, True]:
            mock_JIRA.reset_mock()
            feedback = FeedbackFactory(
                service=self.test_service,
                delivered=delivered,
                difficulty_contacting='didntknow',
                extra_comments='I have a little dog',
            )
            jira_record = feedback.jira_records.get()
            self.assertEqual(jira_record.feedback, feedback)
            self.assertEqual('', jira_record.jira_issue_key)
            self.setup_issue_key(mock_JIRA)
            jira_project = 'XYZ'
            with override_settings(JIRA_FEEDBACK_PROJECT_KEY=jira_project):
                jira_record.do_jira_work()
            mock_JIRA.return_value.create_issue.assert_called_with(
                issuetype={'name': 'Task'},
                summary='Feedback about %s' % feedback.service.name_en,
                project={'key': jira_project},
                description=mock.ANY,
                duedate=mock.ANY,
            )
            description = mock_JIRA.return_value.create_issue.call_args[1]['description']
            self.assertIn(feedback.name, description)
            self.assertIn(feedback.nationality.name_en, description)
            self.assertIn(feedback.phone_number, description)
            self.assertIn(feedback.service.name_en, description)
            if delivered:
                self.assertIn('Quality', description)
                self.assertIn(feedback.get_wait_time_display(), description)
            else:
                self.assertNotIn('Quality', description)
                self.assertIn(feedback.get_non_delivery_explained_display(), description)
            self.assertIn('Did not know how to contact them', description)
            self.assertIn('I have a little dog', description)


@mock.patch('services.jira_support.JIRA', autospec=True)
class JiraRequestForServiceTest(MockJiraTestMixin, TestCase):
    def test_creating_request_for_service_sends_data_to_jira(self, mock_JIRA):
        mock_JIRA.reset_mock()
        rfs = RequestForServiceFactory()
        jira_record = rfs.jira_records.get()
        self.assertEqual(jira_record.request_for_service, rfs)
        self.assertEqual('', jira_record.jira_issue_key)
        self.setup_issue_key(mock_JIRA)
        jira_project = 'XYZ'
        with override_settings(JIRA_REQUEST_SERVICE_PROJECT_KEY=jira_project):
            jira_record.do_jira_work()
        mock_JIRA.return_value.create_issue.assert_called_with(
            issuetype={'name': 'Task'},
            summary='Request service to be added: %s' % rfs.service_name,
            project={'key': jira_project},
            description=mock.ANY,
            duedate=mock.ANY,
        )
        description = mock_JIRA.return_value.create_issue.call_args[1]['description']
        for attr in ['provider_name', 'service_name', 'address',
                     'contact', 'description', 'rating', ]:
            self.assertIn(str(getattr(rfs, attr)), description)
        self.assertIn(rfs.get_admin_edit_url(), description)
