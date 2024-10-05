#!.venv/bin/python

from utils.processes import run_infrastructure, run_crawling_process, run_api

if __name__=="__main__":
    run_infrastructure()
    # for today's demo i'll turn this off
    # run_crawling_process()
    run_api()