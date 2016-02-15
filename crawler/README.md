Meetup crawler
==============

Author: Antonio Lima
License: MIT

This is a minimal implementation of a Meetup API crawler, complete with rate limiting.

Usage
-----

In order to use the API you simply need to instantiate a MeetupApi object:

```Python
api = meetup.MeetupApi(api_key)
```

and then call endpoints as advertised in the online Meetup API documentation, for example:

```Python
gb_cities = api.cities(country='gb')
```

More complex endpoints (e.g., with slashes) can be reached using the method `_get`:

```Python
group_events = api.cities('/2/events', group_id=123456)
```
