#!/usr/bin/env python3

import os
import sys
import datetime
import contextlib
import jenkins
import dominate
import dominate.tags as dt
from servers import servers, init_servers

def build_status(server, buildName):
    job_info = server.get_job_info(buildName)
    last  = job_info['lastBuild']['number']
    compl = job_info['lastCompletedBuild']['number']
    succ  = job_info['lastSuccessfulBuild']['number']
    if last > compl: # Not 100% sure if this is how I want to display it.
        compl_info = server.get_build_info(buildName, last)
    else:
        compl_info = server.get_build_info(buildName, compl)
    if compl != succ:
        return compl_info, server.get_build_info(buildName, succ)
    else:
        return compl_info, None

def failed_stages(server, buildName, howMany=50):
    job_info = server.get_job_info(buildName)
    last_completed = job_info['lastCompletedBuild']['number']
    for job in range(last_completed, last_completed-howMany, -1):
        stages = server.get_build_stages(buildName, job)
        failing = [stage for stage in stages['stages'] if stage['status'] == 'FAILED' and stage['name'] != 'Environment']
        if failing:
            print(failing[0])
            print(str(job)+" : ", ', '.join([stage['name'] for stage in failing][0:1]))

def run(htmlp=False):
    if htmlp:
        doc = dominate.document(title=None)
    else:
        doc = contextlib.nullcontext()
    with doc:
        for server in init_servers(servers):
            try:
                for buildName,prettyName in server['builds']:
                    compl_info, succ_info = build_status(server['connection'], buildName)
                    # I don't know why it insists on short name, but my use requires the FQDN.
                    url = compl_info['url']
                    started = datetime.datetime.fromtimestamp(round(compl_info['timestamp']/1000.0))
                    took = datetime.timedelta(milliseconds=round(compl_info['duration']/1000.0)*1000)
                    result = compl_info['result'] or 'still running'
                    if compl_info['duration'] == 0:
                        elapsed = datetime.datetime.now() - started
                        rounded = round(elapsed.total_seconds()/60.0)*60
                        elapsed = datetime.timedelta(seconds=rounded)
                        took = f"{elapsed} (so far)"
                    if htmlp:
                        style=None
                        if result == 'SUCCESS':
                            style = "color:green;"
                        elif result == 'FAILURE':
                            style = "color:red;"
                        dt.p(prettyName, dt.a(compl_info['id'], href=url), " : ",
                             dt.span(result, style=style),
                             f"  (started {started}, took {took})")
                    else:
                        print(url+" : ", result)
                        print(f"    started {started}, took {took}")
                    if succ_info:
                        succ_started = datetime.date.fromtimestamp(round(succ_info['timestamp']/1000.0))
                        if htmlp:
                            dt.p(f"(last successful:  {succ_info['number']} on {succ_started})",
                                 style="text-indent: 40px")
                        else:
                            print(f"    (last successful:  {succ_info['number']} on {succ_started})")
            except Exception as err:
                print(f"Error: {err}")
    if htmlp:
        print(doc)


if __name__ == '__main__':
    try:
        run(len(sys.argv) > 1)
    except Exception as err:
        print(f"Error: {err}")
