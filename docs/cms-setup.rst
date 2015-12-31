CMS Setup
=========

This document describes necessary page setup for the site to function
properly.

When adding a language
----------------------

- Create variation of search-results page for that language and publish.

Search bar support
------------------

- Create a page to display search results.  On Advanced Settings page:

  a. Id must be set to "search-results"
  b. Application must be set to "aldryn search"
  c. In the Pages menu, un-check the Menu column.
  d. For each language:

    - Set title to "Search Results" (or equivalent) in the appropriate language
    - Publish.

  The ``create_minimal_cms`` management command can create the page and
  initial language variations.  After running the command, edit the page titles
  and other data as appropriate.
