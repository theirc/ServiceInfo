Lifecycle of the Service records


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

From draft, pk 2 can go to canceled or rejected as before,
but if it is approved then we get:

  pk: 1
  status: archived

  pk: 2
  status: current

  We don't need pk 1 anymore, so we archive it and nobody
  sees it anymore.

  QUESTION: OR SHOULD WE COPY THE DATA INTO PK 1 and archive PK 2,
  in case there are foreign keys to it anywhere?   Do we have any
  such FK's?

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

The archive records don't show up anywhere for now.

If we had a canceled record lying around, we'd do the same thing with it
(change status to archived before proceeding).
