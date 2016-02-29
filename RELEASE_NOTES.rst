ServiceInfo

Release Notes

0.5.3 - Feb. 29, 2016
---------------------

* SC-152 - Fix issue in reCAPTCHA validation
* SC-151 - Use official aldryn-common package instead of Caktus fork
* SC-119 (partial) - Add management command to update site association of
  CMS pages, for using a database on one site on a different site
* Add infrastructure for generating documentation for RTD
* Add placeholders to "wide (two column)" template
* Fix styling issue
* Update translations from Transifex

0.5.2 - Feb. 1, 2016
--------------------

* Resolve misalignment of menu icons
* SC-148 - Allow large tables to be scrolled on mobile
* Add Facebook share feature
* SC-86 - Allow searching of services
* Fullcalendar widget added to improve calendar display and responsiveness
* Improve ratings submission: ratings submission mechanism tweaked to eliminate page reloads and save page ratings between visits
* SC-149 - Resolve problem with language buttons in IE
* Use ServiceInfo logo as favicon
* Disqus localization: Disqus plugin now correctly detects page's language

0.5.1 - Jan. 28, 2016
---------------------

* SC-107 Social sharing via Facebook and Twitter can now be easily enabled for a particular page (only "Like" for Facebook at this time)
* SC-142 Links from front-end app to CMS
* SC-42 Minimal page theme
* SC-65 Upgrade to Django CMS 3.2.0
* SC-34 Addition of aldryn-forms plugin
* SC-144 Show menu icons for child menu entries
* SC-114 Page rating feature

0.5.0 - Jan. 20, 2016
---------------------

* integrate translation changes made on Transifex
* Upgrade aldryn-newsblog and aldryn-faq (stop using Caktus forks of these)
* Various menu improvements
* Support for integrating Google maps and Google calendar
* Add search of CMS content

0.4.4 - Dec. 30, 2015
---------------------

* Present language dialog to new user loading CMS page
* Language selection integrated between front-end app and CMS
* Fix an issue with table width on mobile devices
* Allow specifying a Materialize icon for a page's menu entry
* / now reaches the CMS, not the ServiceInfo app
* Add logout button for logged-in users

0.4.3 - Dec. 18, 2015
---------------------

* Support four tiers of menus
* Use ServiceInfo twitter timeline
* Add Aldryn Video plug-in
* Introduce sidebar for navigation and search (search is just a placeholder for now)
* RTL for Arabic on page with both Arabic and English
* Make sure language chooser is available when top-level navigation has more elements than can be displayed
* IE 11 navigation layout fix
* Fix image template to be able to handle different image sizes

0.4.2 - Dec. 10, 2015
---------------------

* Fix aldryn-newsblog issue

0.4.1 - Dec. 10, 2015
---------------------

* Remove author from News/Blog detail page
* Various style improvements
* Upgrade aldryn-faq to 1.0.8 to fix a 500 error
* Add column plug-in and make appropriate styling changes
* Add Google Map plugin (djangocms-googlemap)
* A language picker is now provided on CMS pages.
* Front-end application fix: When adding a service failed, error messages which
  weren't specific to a particular field were not displayed previously.
* The CMS menu now shows pages under the top-level page.
* SC-33 - the footer for CMS pages is now a static placeholder
* SC-60 - the active menu item is now highlighted
* SC-61 - the menu can now show up to three levels of pages
* Horizontal layout for menu
* Improved page templates, especially for FAQ and News/Blog
* SC-53: update djangocms-admin-style package to resolve 500 error when trying
  to delete FAQ question from list view

0.4.0 - Nov. 19, 2015
---------------------

* Upgrade to Django 1.7.10 (#70)
* Update dev setup (#71, #72)
* Prepare frontend for DjangoCMS (#73, #74, #78, #85)
* Install Django CMS (#75)
* Setup Transifex for CMS (#76, #82)
* Google Analytics (#79)
* Disqus plugin (#80)
* FAQ plugin (#81)
* News/blog plugin (#83, #84)


0.3.3 - Aug. 20, 2015
---------------------

* Make chart sizes more flexible (#62, #64)
* Upgrade to Django 1.7.9 (#65)
* Fix for CSV downloads (#60)
* Add charts (#53)

0.3.2 - Aug. 17, 2015
---------------------

* Fixes for feedback form (#66)

0.3.1 - Aug. 11, 2015
---------------------

* Reference npm dependencies by version (#54, #55)
* Remove DRF session auth, fixing authenticated form submissions (#57, #58)

0.3.0 - Aug. 4, 2015
--------------------

* Remove leaflet references (#39)
* Add support for responsive Service photos (#40, #41, #44)
* Add Flot.js (#48)
* Don't i18n Django admin (#47, #49)
* Allow authentication for browsable API (#42)
* Fix service overlap in admin (#50)
* Initial chart implementation (#51)

0.2.9 - Jul. 21, 2015
---------------------

* Add Request for Service functionality (#20, #21, #27, #36, #37)
* Spiderfy to show multiple markers in close proximity (#29)
* Minor doc / TravisCI improvements (#24, #26, #28, #30)
* Add Google Analytics (#38)

0.2.8 - Jul. 14, 2015
---------------------

* Fix feedback form when service not delivered

0.2.7 - Jun. 29, 2015
---------------------

* Copyright in LICENSE updated
* On map view, show number of results that are displayed in the map
* Fix bug where some text wasn't appearing on the feedback form.

0.2.6 - Jun. 23, 2015
---------------------

* New repo for open source, serviceinfo
* Updated translations

0.2.5 - Jun. 22, 2015
---------------------

* Make "get directions" a button
* Change maps zoom levels
* Update messages
* Add link to Google directions
* Fix mobile keyboard popping up over map in some cases
* Fix some services not showing up on map by showing results
  closest to current map center

0.2.4 - Jun. 10, 2015
---------------------

* Changes for AWS load balancing
* Translation updates
* Display cost of service on detail page (#576)
* Allow non-staff to use reports (#574)
* Fix translation issues related to feedback (#573)

0.2.3 - Jun 1, 2015
-------------------

* Fix alignment of phone number and website sections on service detail page
* Add a checkbox for mobile services and some help text
* Allow selecting higher-level areas as a service's service area (e.g. choose a governate
  or a CAZA).
* Add geographic data to the service areas
* On mobile services, set location field to the center of their area of service
* Allow non-staff to use reports

0.2.2 - May 19, 2015
--------------------

* Fix some links on the home page.

0.2.1 - May 19, 2015
--------------------

* Fix search - was broken by a new release of backbone.

0.2.0 - May 18, 2015
--------------------

* Updated translations
* Clean out old migrations
* Move button for viewing reports from side menu to manage services page
* Remove "Add service" from menu and rename "Services list" to "Manage services"

0.1.9 - May 13, 2015
--------------------

* Fix search using map
* Add "Give feedback again" button on Feedback confirmation page

0.1.8 - May 13, 2015
--------------------

* Some IE fixes
* Fix: "Todays hours"
* Fix: sort search results by name
* First 5 reports of services by service type
* Fix: site name in password reset email subject
* Include all providers in exports
* Improve styling of import/export page
* Add more checks that only staff can see reports
* Add report with services by type and location
* Rename from "Service Info" to "ServiceInfo"
* Show provider name in search results and service detail page
* Translation updates
* Allow creating services in the Django admin
* Git repository name changed to ServiceInfo
* Make all provider names clickable in Django admin
* Update text on feedback form
* Import/export feature
* Fix for bad lat/long coming from old Firefox
* Make error messages more prominent.
* Added backups.
* Numerous styling updates
* Fixes to display logic on services list
* Improve services list styling to make status of services more obvious.

0.1.7 - Apr. 23, 2015
---------------------

* Get completed translations of changes in 0.1.5 & 0.1.6

0.1.6 - Apr. 22, 2015
---------------------

* Update footer text as requested by IRC
* Use different JIRA projects for staging

0.1.5 - Apr. 22, 2015
---------------------

* Add password reset/change (see login page)
* Make login email not case sensitive
* Fix losing focus while typing search text
* Add field help text provided by IRC
* Fix missing link from password reset emails
* Ensure user is provider when creating a service
* Multiple style improvements
* Limit view in initial map display

0.1.4 - Apr. 20, 2015
---------------------

* Fix for not everything changing language
* Update translations
* Fix Arabic font in select element
* Improve resend verification link UI visibility
* Feedback link goes to search page
* Add Home link to side menu

0.1.3 - Apr. 15, 2015
---------------------

* Add frontend tests
* Add links to footer
* Translation updates
* Django 1.7.7
* Fix admin link
* Fix menu items appearing in the right context
* Rearrange and reword menu items
* Fix new service button
* Give list/map buttons more contrast
* Some wording changes
* Fix add criterion button
* Send feedback to JIRA
* Add feedback pages
* Add landing page
* Better handling of geolocation "errors"
* Allow pagination in the API
* Limit input lengths
* Clarify view and change operations on services list
* Close menu when opening language picker
* Hide sort options on map
* Sort by name when not sorting by nearest

0.1.2 - Mar. 27, 2015
---------------------

* Continue updating translations
* Continue fixing and improving styling
* Unified list and map options on search page
* If no translation for a particular message, fall back to another
  language rather than leaving the text blank.
* When nothing matches in search, display a message to let the user
  know.
* Display cost and selection criteria on service detail page.
* Replace red markers on map with service icons
* Make ordering english-arabic-french consistent in admin
* Add new feedback page (styling TBD)
* Fix bug - preserve translations of fields in other languages
  when submitting an update to a service
* Improve performance by reducing redundant API calls
* Include all provider and service data in JIRA tickets
* In JIRA data about a service, display "Closed" on days when a
  service has no hours.
* Add service type icons to database
* Improved display of errors in frontend
* New logo

0.1.1 - Mar. 12, 2015
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
