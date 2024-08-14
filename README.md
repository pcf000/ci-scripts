These scripts connect to the Jenkins servers at ml-ci.amd.com:21096 and
ml-ci-internal.amd.com:8080, and as such require a username and password
to authenticate.

They look for the files .jenkins.ml-ci and .jenkins.ml-ci-internal in
the home directory.  (Those can be changed -- see the 'servers' variable
and 'init_servers' function in the files.)  The file is expected to
contain "username:password".

To avoid putting one's main password in a file, it's best to make an API
token on the Jenkins server and use that.  To create an API token,
connect to the Jenkins server at, eg,
http://ml-ci.amd.com:21096/me/configure (or take the long route of
clicking on your name at the upper right and then Configure in the
left-side menu).

Do "python3 -m pip install -r requirements.txt" for the essential
prerequisites -- python\_jenkins is the jenkins module, tabulate is used
for text output, and dominate is used for html output.  Python\_jenkins
does drag in a bunch of other modules.
