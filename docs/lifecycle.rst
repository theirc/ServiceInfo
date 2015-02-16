Lifecycle of the Service records


Service record statuses:

* current - visible to the public, provider, and staff after approval
  by IRC staff
* draft - pending review by IRC staff. visible to provider and staff.
* canceled - provider canceled review before IRC staff acted on it.
  visible to provider and staff. OR provider withdrew the service after
  it was approved.
* rejected - IRC staff rejected it
  visible to provider and staff.
* archived - no longer visible in most interfaces, just keeping
  around because there might be links back to it from JIRA etc.


Provider creates a new service. It needs approval:

  pk: 1
  status: draft

Three possible new states:

    Provider cancels it:

      pk: 1
      status: canceled

    Or, IRC rejects it:

      pk: 1
      status: reject

    Or, IRC approves it:

      pk: 1
      status: current

From state current, provider submits some proposed changes.
Now we have:

  pk: 1
  status: current

  pk: 2
  status: draft
  update_of: 1

Both of these records are visible to the provider, so they
can see that they have a pending update.

From draft, pk 2 can go to canceled or rejected as before,
which would leave pk 1 unchanged, but if it is approved
then we don't need pk 1 anymore, so we archive it and nobody
sees it anymore.  We get:

  pk: 1
  status: archived

  pk: 2
  status: current
  update_of: 1

So now the only records anyone sees are:

  pk: 2
  status: current

Suppose provider had submitted a change but it's been rejected,
so we have these two records lying around:

  pk: 1
  status: current

  pk: 2
  status: rejected
  update_of: 1

Now they submit a new proposed change.  We only want 2 non-archived
records around at any one time, so change the rejected record to archived
before adding the new draft record:

  pk: 1
  status: current

  pk: 2
  status: archive
  update_of: 1

  pk: 3
  status: draft
  update_of: 1

The archive records don't show up anywhere for now, unless you
have a link to them.

If we had a canceled record lying around, we'd do the same thing with it
(change status to archived before proceeding).

Suppose the provider doesn't want their service published anymore.
If we have

   pk: 1
   status: current

they can withdraw or cancel it, giving

   pk: 1
   status: canceled

leaving the service not visible to the public.

If the provider has a rejected or canceled record, they might
reasonably want to edit it a little and "re-open" it, putting it
back in draft status and requesting a new review.

But for phase I, let's not implement that to save time. We can
always add it later.

The working spec says that even while a change is pending, the
provider can edit the draft service record and an update will
be sent to the JIRA ticket to let the staff know that the data
has been updated again.

Here's that scenario with a new service pending.  We start with:

  pk: 1
  status: draft
  update_of: none

Now the provider "edits" that draft, and we end up with:

  pk: 1
  status: archived

  pk: 2
  status: draft
  update_of: none

And we send a new comment to the JIRA ticket that was created when
the first service record was submitted. The comment includes a link
to the new record.

Now suppose we have one current record, and another record with a
draft change to it:

  pk: 1
  status: current

  pk: 2
  status: draft
  update_of: 1

Now someone submits an edit to pk 2. We archive 2 and create 3:

  pk: 1
  status: current

  pk: 2
  status: archived
  update_of: don't care

  pk: 3
  status: draft
  update_of: 1

and we submit a comment to the JIRA issue from pk: 2 and include
a link to pk: 3.
