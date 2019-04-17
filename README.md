# 'base' project

#### INPUT:
Service listens on the same host, public IP. Accepts params by GET/POST.
API token expires in 5mins.
If task is not started, returns 404 code with "Not found" message.
When task completed successfully - returns 200 code with some log output containing "RESULT: INTEGER" line.
Otherwise - 500 code with log output and "ERROR: STRING" line.
We need to start task, control its result and restart if failed or every 60 seconds.
The process must work on permanent basis in background.

#### TODO:
Improve the base solution.

Objectives:
1) Universalize;
2) Optimize;
3) Secure.

Please make sent a pull request or link to your repository with the solution.

Thanks
