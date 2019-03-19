# nattracker
A therapy tool allowing users to track their negative automatic thoughts and emotional responses.

Clients enter situations with a "helpful response" and/or an "unhelpful response".
Each "response" includes one or more thoughts, which may or may not be NATs
(negative automatic thoughts), as well as emotions that were felt, and behavioral
responses that occurred. Multiple situation entries may use the same response.

As data are entered into the database, the user can see which thoughts of his or
her "helpful" responses most effectively challenged his or her NATs, as well as
which NATs occurred more frequently. This information appears on the "Statistics" page.

Currently, a client is allowed to log in and see a "dashboard" overview of his
most recent situations and responses. However, a function for admins to grant
"observers" access to the data of specific clients will be implemented.

This repository contains the directory for a single Django app which is intended
to be installed and used within a larger Django project environment. The code
runs on Python 3 and is tested on Django 2.0.2.
