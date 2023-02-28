# MICE Gathering

Repo for code and things to running real world tests to measure internet censorship.

## Overview

#TODO: fill this out more betterer, and get feedback from Paul

* We don't really care about _what_ sites are navigated, or _how_ they are navigated (e.g. user models don't much matter). We primarily want to see if the protocol (is this the correct term?) under test, e.g. shawdows, obfs, etc., flag some censorship in some adversarial environment.

## Issues

- Seeing a lot of this in the logs. Expected, or a problem?
    > :warning: NOT EXPECTED, THIS IS A PROBLEM!!!
    ```
    1663675843.621021,navigation_failed,http://wordpress.com,83/1000 b'VHJhY2ViYWNrIChtb3N0IHJlY2VudCBjYWxsIGxhc3QpOgogIEZpbGUgIi9ob21lL2Jyb3dzZXIvc2NyaXB0cy9ydW5fc3MucHkiLCBsaW5lIDQ5MywgaW4gbWFpbgogICAgZHJpdmVyLmdldCh1cmwpCiAgRmlsZSAiL3Vzci9sb2NhbC9saWIvcHl0aG9uMy45L2Rpc3QtcGFja2FnZXMvc2VsZW5pdW0vd2ViZHJpdmVyL3JlbW90ZS93ZWJkcml2ZXIucHkiLCBsaW5lIDQ0MCwgaW4gZ2V0CiAgICBzZWxmLmV4ZWN1dGUoQ29tbWFuZC5HRVQsIHsndXJsJzogdXJsfSkKICBGaWxlICIvdXNyL2xvY2FsL2xpYi9weXRob24zLjkvZGlzdC1wYWNrYWdlcy9zZWxlbml1bS93ZWJkcml2ZXIvcmVtb3RlL3dlYmRyaXZlci5weSIsIGxpbmUgNDI4LCBpbiBleGVjdXRlCiAgICBzZWxmLmVycm9yX2hhbmRsZXIuY2hlY2tfcmVzcG9uc2UocmVzcG9uc2UpCiAgRmlsZSAiL3Vzci9sb2NhbC9saWIvcHl0aG9uMy45L2Rpc3QtcGFja2FnZXMvc2VsZW5pdW0vd2ViZHJpdmVyL3JlbW90ZS9lcnJvcmhhbmRsZXIucHkiLCBsaW5lIDI0MywgaW4gY2hlY2tfcmVzcG9uc2UKICAgIHJhaXNlIGV4Y2VwdGlvbl9jbGFzcyhtZXNzYWdlLCBzY3JlZW4sIHN0YWNrdHJhY2UpCnNlbGVuaXVtLmNvbW1vbi5leGNlcHRpb25zLlRpbWVvdXRFeGNlcHRpb246IE1lc3NhZ2U6IHRpbWVvdXQ6IFRpbWVkIG91dCByZWNlaXZpbmcgbWVzc2FnZSBmcm9tIHJlbmRlcmVyOiAtMC4wMDIKICAoU2Vzc2lvbiBpbmZvOiBjaHJvbWU9MTA0LjAuNTExMi4xMDEpClN0YWNrdHJhY2U6CiMwIDB4NTYyNmQ5NzgyMmQzIDx1bmtub3duPgojMSAweDU2MjZkOTU4NzhlOCA8dW5rbm93bj4KIzIgMHg1NjI2ZDk1NzRlYzggPHVua25vd24+CiMzIDB4NTYyNmQ5NTczYTliIDx1bmtub3duPgojNCAweDU2MjZkOTU3NDA1YyA8dW5rbm93bj4KIzUgMHg1NjI2ZDk1N2ZkOWYgPHVua25vd24+CiM2IDB4NTYyNmQ5NTgwOTAyIDx1bmtub3duPgojNyAweDU2MjZkOTU4ZWVmZCA8dW5rbm93bj4KIzggMHg1NjI2ZDk1OTJkNmEgPHVua25vd24+CiM5IDB4NTYyNmQ5NTc0NDg2IDx1bmtub3duPgojMTAgMHg1NjI2ZDk1OGVjMDQgPHVua25vd24+CiMxMSAweDU2MjZkOTVlZmMyMyA8dW5rbm93bj4KIzEyIDB4NTYyNmQ5NWRjYTIzIDx1bmtub3duPgojMTMgMHg1NjI2ZDk1YjIxYjggPHVua25vd24+CiMxNCAweDU2MjZkOTViMzJlNSA8dW5rbm93bj4KIzE1IDB4NTYyNmQ5N2M5YmJkIDx1bmtub3duPgojMTYgMHg1NjI2ZDk3Y2NjOTggPHVua25vd24+CiMxNyAweDU2MjZkOTdiMmRjZSA8dW5rbm93bj4KIzE4IDB4NTYyNmQ5N2NkYjY1IDx1bmtub3duPgojMTkgMHg1NjI2ZDk3YTc3NTAgPHVua25vd24+CiMyMCAweDU2MjZkOTdlYWY4OCA8dW5rbm93bj4KIzIxIDB4NTYyNmQ5N2ViMTFmIDx1bmtub3duPgojMjIgMHg1NjI2ZDk4MDU5OWUgPHVua25vd24+CiMyMyAweDdmMmI3NzcwZGVhNyA8dW5rbm93bj4KCg=='
    ```
    base64 decoded error message:
    ```
    Traceback (most recent call last):
    File "/home/browser/scripts/run_ss.py", line 493, in main
        driver.get(url)
    File "/usr/local/lib/python3.9/dist-packages/selenium/webdriver/remote/webdriver.py", line 440, in get
        self.execute(Command.GET, {'url': url})
    File "/usr/local/lib/python3.9/dist-packages/selenium/webdriver/remote/webdriver.py", line 428, in execute
        self.error_handler.check_response(response)
    File "/usr/local/lib/python3.9/dist-packages/selenium/webdriver/remote/errorhandler.py", line 243, in check_response
        raise exception_class(message, screen, stacktrace)
    selenium.common.exceptions.TimeoutException: Message: timeout: Timed out receiving message from renderer: -0.002
    (Session info: chrome=104.0.5112.101)
    Stacktrace:
    #0 0x5626d97822d3 <unknown>
    #1 0x5626d95878e8 <unknown>
    #2 0x5626d9574ec8 <unknown>
    #3 0x5626d9573a9b <unknown>
    #4 0x5626d957405c <unknown>
    #5 0x5626d957fd9f <unknown>
    #6 0x5626d9580902 <unknown>
    #7 0x5626d958eefd <unknown>
    #8 0x5626d9592d6a <unknown>
    #9 0x5626d9574486 <unknown>
    #10 0x5626d958ec04 <unknown>
    #11 0x5626d95efc23 <unknown>
    #12 0x5626d95dca23 <unknown>
    #13 0x5626d95b21b8 <unknown>
    #14 0x5626d95b32e5 <unknown>
    #15 0x5626d97c9bbd <unknown>
    #16 0x5626d97ccc98 <unknown>
    #17 0x5626d97b2dce <unknown>
    #18 0x5626d97cdb65 <unknown>
    #19 0x5626d97a7750 <unknown>
    #20 0x5626d97eaf88 <unknown>
    #21 0x5626d97eb11f <unknown>
    #22 0x5626d980599e <unknown>
    #23 0x7f2b7770dea7 <unknown>
    ```
- Warning when starting up server
    ```
    [[0;32m  OK  [0m] Started [0;1;39mlibcontainer contaâ¦a17f1e284abc76f51eaf78dde9a0c[0m.
    [  103.248082] cloud-init[1180]: /home/browser/scripts/run_ss.py:438: DeprecationWarning: executable_path has been deprecated, please pass in a Service object
    [  103.262416] cloud-init[1180]:   driver = webdriver.Chrome(
    ```

## Ideas

- Run the test distributed? i.e. instead of running a single client/server pair that browses 1000 websites, spin up 10 client/server pairs that browse 100 websites each. Hosting cost should be similar assuming you are charged for time, like AWS.
    - could the clients share the same server? load balance multiple servers?
    - instances (at least on AWS) can be pre-empted, so distributing the test reduces the likelihood of losing test results.

## TODO

- :warning: FIX NAVIGATION BUG!!!
    - Fail early if shadowsocks (or whatever we happen to be using for an experiment) fails to authenticate
- Upgrade to CDKTF 0.13
- :white_check_mark: Proof of concept in AWS
- :white_check_mark: Create server in DigitalOcean using Terraform
    - Proof of concept with AWS client
- Save client and server IPs to test output (can probably just grab the `cdktf.json`, maybe parse it to a README)
- change shadowsocks port to non-standard port (i.e. _not_ 8080) bewteen 9000 and 11000
- run a test using obfs
- Define AWS VPC in terraform. Currently it's been created manually.
    - do this in CDKTF
- templatize client and server definitions and make it easy to swap them out
- Test TCPDump in AWS without running anything else to see if we need to filter any traffic. Run for ~5 minutes and pull the PCAP.
- Switch to Terraform CDK and run everything in Python?
    - Maybe look into Ansible (or some other tech) first to see what makes the most sense
    - need _some_ sort of frontend (probably CLI), so will likely use/need Python there at the very least
- Figure out best way to pull test logs of the server instance
    - need a reliable way to check when the experiment is complete
        - check the last line of the test log file? Is this guaranteed to be consistent?
    - do it in python?
    - Ansible?
- Enable variables for
    - location of client and server
    - number of sites visisted
    - which sites are visited?
        - do we want to vary the list of top sites base on the country in which we are testing? Presumably the top sites in the US will not be the same as some other countries
    - Protocol (shadowsocks, TOR, PT, etc.)
    - cloud hosting provider credentials
    - duration (is this similar to number of sites to visit? do we want both? mutually exclusive?)
- Abstract all the things
    - hosting providers. Will be difficuly (maybe not possible) since credentials need to be provided
    - https://www.terraform.io/language/modules/develop/composition#multi-cloud-abstractions
- Figure how we plan to run an analysis script on the VPS to analyze the PCAPs
- Test terraform code on a fresh AWS account, either RACE or UMASS.
- Create a consistent username (currently AWS uses `ubuntu` and DigitalOcean uses `root`) across service providers for easy ssh access.
- Automate ssh key generation. Make sure user and hostname are excluded, use something like `ssh-keygen -C ""`.

### Stretch Goals

- Conceptually, a client and server are just a resource running different images/scripts. Can I abstract this to minimize redundancy?
- Minify bash sent to EC2 instance as user-data
    - https://github.com/Zuzzuc/Bash-minifier
    - https://github.com/precious/bash_minifier
- Separate stacks for outputing various options that the user can choose from? i.e. run a command to see the options for:
    - zone
    - server size
    - other things they might want to configure?
- Dockerize this mess after realizing what a royal PITA it is setting up CDKTF on a new machine?




Ugh, bummer:
https://github.com/hashicorp/terraform-cdk/issues/1104

## References

[Selenium](https://pypi.org/project/selenium/)
[Selenium Python Docs](https://www.selenium.dev/selenium/docs/api/py/api.html)
