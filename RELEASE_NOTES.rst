Service Info

Release Notes

0.1.0 - Mar. 12, 2015
---------------------

* Add JIRA comment when a service is approved or rejected
* Updates to translations
* Speed up page load by compiling javascript with Closure
* Add three new provider fields: address, focal point name,
  focal point phone number
* Fix layout switching to landscape-style when keyboard invoked
  in Chrome Android
* Use google maps in admin, allowing staff to set service location
  with display of street-level data and providing search by address,
  place, and latitude-longitude
* Enable "Service Maps" page in public interface and provide
  initial implementation. Still a work in progress.


0.1.0 - Mar. 5, 2015
--------------------

* Use preferred fonts
* Updates to translations
* Remove text in service approval email to provider about the URL of
  the published service until we have a page to link to
* Translate days of the week
* Translate service statuses
* Require a location before approving a service
* Add API for anonymous searching of services
* Fixes for showing errors from the API
* Change the service list page when the list is empty
* Put "URL" in label and example in placeholder of website field
* Add +/- before Add/Remove Criterion button labels
* Change label on provider name
* Label hours as "working hours"
* Sort dropdown values before populating them
* Require one letter in provider name
* Minimum 6 character password
* Re-render the services list if the language is changed
* Phone number validation
* Fix service area, type not appearing in service list
* Right-to-left when in Arabic
* Fixed language toggle layout and positioning and added black background.
* Create JIRA record even if service already approved (or rejected, whatever)
* Service records can change between creating and running JiraUpdate
* Display link to Django admin in menu for staff users
* Add approve and reject buttons to the service admin change page
* Include an ES6 Promise polyfill for browsers that do not support it.

0.0.9 - Feb. 18, 2015
---------------------

* Fix map widget in admin
* Display which service records are pending edits of which other ones
* Better messages when unexpected errors happen from the backend

0.0.8 - Feb. 17, 2015
---------------------

* Remove 'delete' option for services in a state where
  we don't allow deleting anyway.

0.0.7 - Feb. 17, 2015
---------------------

* Fix regression on selection criteria controls

0.0.6 - Feb. 17, 2015
---------------------

* Fix double-submission of services

0.0.5 - Feb. 17, 2015
---------------------

* Finish applying translation to the UI
* Add selection criteria editing to service form
* Improvements to form validation
* Create or update JIRA issues on new service, change
  to service, canceling service or service change, and
  provider changes
* Remember user's language in backend so we use their
  language when they login on a new browser

0.0.4 - Feb. 11, 2015
---------------------

* Submit edits to existing services
* Display data fields in user's preferred language where available
* Many and various smaller design and behavioral fixes

0.0.3 - Feb. 9, 2015
--------------------

* Provider self-registration
* Menus update depending on whether user logged in
* List services
* Submit a new service
* Create new JIRA ticket when new service is submitted
* Send email when service is approved
* Updates to translations

0.0.2 - Jan. 30, 2015
---------------------

* Get login and logout working
* Style updates
* Initial service and provider types
* Hide/show language selection control
* Change project name to "Service Info"
* Load some initial message translations
* Start setting up support for geo data in the database
