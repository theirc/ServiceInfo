Import/Export
=============

There is be an "Import/Export" item on the menu that goes to an import/export page.

Downloaded and uploaded Excel files will have the same format, as follows:

* The spreadsheet file will have three sheets or tabs.
* The first will contain the provider’s information, as a header row of field names followed by a row with one field’s data in each column.
* The second sheet will have the data for the provider’s currently approved/public services, again with a header row of field names, followed by one row per service with a field in each column.
* The third sheet will have the selection criteria for the services.

Pending new services or changes will not be included in the exported data.

Each sheet will have a first column called “id” which is a number that identifies that provider or service internally and is used when importing to match up the data to an existing record.

If an imported file contains services with blank ‘id’ fields, those rows will be considered as requests to create new services.

Rows with valid ID fields will be considered requests to change the data for existing services. If changes are already pending to the existing service, the pending changes will be canceled and replaced by the new requested changes.

Any rows with ID fields that are non-existent services or not currently public services belonging to the provider will cause the entire import to be rejected and the errors reported to the user.

Any row with a valid ID field but with all the other values cleared out will signal a request to delete/cancel that record.

The Services sheet will have a second column “provider__id” with the ID of the provider who owns the service. Providers should just leave this column alone when importing, and copy its value to any new service they are requesting to create.

The selection criteria sheet will have these columns: 'id', 'service__id', 'text_en', 'text_ar', and 'text_fr'.  'id' is a unique identifier for that criterion.  'service__id' is the ID of the service it applies to. The other fields should be self-explanatory.

Times of day will be represented as a string in 24-hour "HH:MM" format.

If the data for the provider is edited in the first sheet and is valid, then the provider’s data will be updated with the new data upon successful import.

The provider sheet will have a column “password” that never contains any values on export. The provider password can be changed by putting a value in that column for import.

Some fields in the provider and service records in the database do not contain values directly, but are links to other tables. The export/import format will not try to represent those fields that way. Any field that in the database is a link to a record in another table will be represented in the spreadsheet by one or more fields containing the data in the record that was linked to. For example, the provider type field links to a provider type record, but when the provider data is exported, instead of a single type column there will be four columns: type__number, type__name_en, type__name_ar, and type__name_fr (these are the four columns in the provider type table).

When adding selection criteria to a new service, there’s no way to know what ID the new service will be assigned. So in the selection criterion’s ‘service__id’ field, instead put the english name of the new service, for lack of a better solution.

When editing the spreadsheet to change the data, the user must either not change the values in these columns or must copy exactly the data from another record in the other table.  On import, if e.g. type__number, type__name_en, type__name_ar, and type__name_fr do not match exactly the four values in one record in the type table, then the import will be considered invalid and not accepted.  Errors will be reported to the user.

When importing a spreadsheet, all data will be carefully checked and if anything does not appear valid, the entire import will be rejected.

Staff export/import
-------------------

If a user is flagged as a staff user in Django (e.g. IRC staff), then the export button on the services list page will download a spreadsheet containing the data for all providers. (As if all providers downloaded their data and the results were merged into a single file). The format is exactly the same.

Import will work similarly to provider import, with these changes:

* New providers can be created by including their data on the providers sheet with a blank ID, including a new password in the password column.  New providers will be sent the usual confirmation email with a link they have to follow before they can login.
* New services can be created by including their data on the services sheet with a blank ID. If the provider who owns the service already exists, put their ID in the Provider_ID column. If the provider is being created by this import, put the new provider’s “name_en” value in the Provider_ID column (for lack of a better way to identify the new provider who should own the service).
* Staff imports can modify any record, not just those owned by the importing user.
