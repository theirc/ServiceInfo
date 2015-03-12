from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.test import TestCase
from email_user.tests.factories import EmailUserFactory
from services.models import Service
from services.tests.factories import ServiceFactory


class ServiceAdminTest(TestCase):
    def setUp(self):
        self.service = ServiceFactory(status=Service.STATUS_DRAFT,
                                      location="POINT (33.0000 35.0000)")
        self.password = 'foofroo'
        self.user = EmailUserFactory(is_staff=True, password=self.password)
        assert self.user.is_staff
        group = Group.objects.get(name='Staff')
        self.user.groups.add(group)
        assert self.user.has_perm('services.change_service')
        assert self.client.login(email=self.user.email, password=self.password)

    def test_permissions(self):
        # Must have Staff group to access services in the admin
        self.user.groups.remove(Group.objects.get(name='Staff'))
        rsp = self.client.get(reverse('admin:services_service_change', args=[self.service.pk]))
        self.assertEqual(403, rsp.status_code)
        rsp = self.save_service_in_form()
        self.assertEqual(403, rsp.status_code)

    def save_service_in_form(self, **kwargs):
        """
        Simulate loading the service in a change form in the admin, updating
        some data from **kwargs, and submitting.
        Returns the response returned by the post.
        """
        data = model_to_dict(self.service)
        data['location'] = str(data['location'])
        # inline data
        data["selection_criteria-TOTAL_FORMS"] = 0
        data["selection_criteria-INITIAL_FORMS"] = 0
        data["selection_criteria-MIN_NUM_FORMS"] = 0
        data["selection_criteria-MAX_NUM_FORMS"] = 0
        # Drop any None values
        data = {k: v for k, v in data.items() if v is not None}
        # Update with caller data
        data.update(**kwargs)
        rsp = self.client.post(reverse('admin:services_service_change', args=[self.service.pk]),
                               data=data)
        return rsp

    def test_edit_service(self):
        # Make a change to the data
        rsp = self.save_service_in_form(name_en="New service name")
        self.assertEqual(302, rsp.status_code, msg=rsp.content.decode('utf-8'))
        service = Service.objects.get(pk=self.service.pk)
        self.assertEqual("New service name", service.name_en)

    def test_approve_button(self):
        rsp = self.save_service_in_form(name_en="New service name",
                                        _approve=True,  # the button we "clicked"
                                        )
        self.assertEqual(302, rsp.status_code, msg=rsp.content.decode('utf-8'))
        service = Service.objects.get(pk=self.service.pk)
        self.assertEqual("New service name", service.name_en)
        self.assertEqual(Service.STATUS_CURRENT, service.status)

    def test_approve_button_with_bad_data(self):
        rsp = self.save_service_in_form(name_en="New service name",
                                        location="not a valid location",
                                        _approve=True,  # the button we "clicked"
                                        )
        self.assertEqual(200, rsp.status_code, msg=rsp.content.decode('utf-8'))
        self.assertIn('<ul class="errorlist"><li>Invalid geometry value.</li></ul>',
                      rsp.context['errors'])
        service = Service.objects.get(pk=self.service.pk)
        self.assertEqual(Service.STATUS_DRAFT, service.status)

    def test_approve_button_with_missing_data(self):
        rsp = self.save_service_in_form(name_en="New service name",
                                        location='',
                                        _approve=True,  # the button we "clicked"
                                        )
        self.assertEqual(200, rsp.status_code, msg=rsp.content.decode('utf-8'))
        self.assertIn('<ul class="errorlist"><li>No geometry value provided.</li></ul>',
                      rsp.context['errors'])
        service = Service.objects.get(pk=self.service.pk)
        self.assertEqual(Service.STATUS_DRAFT, service.status)

    def test_reject_button(self):
        rsp = self.save_service_in_form(name_en="New service name",
                                        _reject=True,  # the button we "clicked"
                                        )
        self.assertEqual(302, rsp.status_code, msg=rsp.content.decode('utf-8'))
        service = Service.objects.get(pk=self.service.pk)
        self.assertEqual("New service name", service.name_en)
        self.assertEqual(Service.STATUS_REJECTED, service.status)

    def test_actions_appear(self):
        rsp = self.client.get(reverse('admin:services_service_changelist'))
        self.assertContains(rsp, "Approve new or changed service")
        self.assertContains(rsp, "Reject new or changed service")

    def test_buttons_appear(self):
        rsp = self.client.get(reverse('admin:services_service_change', args=[self.service.pk]))
        self.assertContains(rsp, "Save and approve")
        self.assertContains(rsp, "Save and reject")

    def test_approve_action(self):
        self.service.validate_for_approval()
        data = {
            'index': '0',  # "Go" button
            'action': 'approve',  # selected action
            '_selected_action': [
                str(self.service.pk),  # selected checkbox
            ]
        }
        rsp = self.client.post(reverse('admin:services_service_changelist'), data)
        self.assertEqual(302, rsp.status_code, msg=rsp.content.decode('utf-8'))
        new_url = rsp['Location']
        rsp = self.client.get(new_url)
        self.assertEqual(200, rsp.status_code, msg=rsp.content.decode('utf-8'))
        service = Service.objects.get(pk=self.service.pk)
        self.assertEqual(Service.STATUS_CURRENT, service.status)

    def test_reject_action(self):
        data = {
            'index': '0',  # "Go" button
            'action': 'reject',  # selected action
            '_selected_action': [
                str(self.service.pk),  # selected checkbox
            ]
        }
        rsp = self.client.post(reverse('admin:services_service_changelist'), data)
        self.assertEqual(302, rsp.status_code, msg=rsp.content.decode('utf-8'))
        new_url = rsp['Location']
        rsp = self.client.get(new_url)
        self.assertEqual(200, rsp.status_code, msg=rsp.content.decode('utf-8'))
        service = Service.objects.get(pk=self.service.pk)
        self.assertEqual(Service.STATUS_REJECTED, service.status)

    def test_approve_action_wrong_status(self):
        self.service.status = Service.STATUS_CURRENT
        self.service.save()
        data = {
            'index': '0',  # "Go" button
            'action': 'approve',  # selected action
            '_selected_action': [
                str(self.service.pk),  # selected checkbox
            ]
        }
        rsp = self.client.post(reverse('admin:services_service_changelist'), data, follow=True)
        self.assertEqual(200, rsp.status_code)
        self.assertIn('Only services in draft status may be approved',
                      [str(msg) for msg in rsp.context['messages']])

    def test_reject_action_wrong_status(self):
        self.service.status = Service.STATUS_CURRENT
        self.service.save()
        data = {
            'index': '0',  # "Go" button
            'action': 'reject',  # selected action
            '_selected_action': [
                str(self.service.pk),  # selected checkbox
            ]
        }
        rsp = self.client.post(reverse('admin:services_service_changelist'), data, follow=True)
        self.assertEqual(200, rsp.status_code)
        self.assertIn('Only services in draft status may be rejected',
                      [str(msg) for msg in rsp.context['messages']])
