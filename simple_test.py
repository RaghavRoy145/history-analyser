import subprocess
import signal
import time
import pytest

def test_simple_output(capfd):
    process = subprocess.Popen(["python", "history_analyser.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)
    process.send_signal(signal.SIGINT)
    out, err = capfd.readouterr()
    # process.wait()
    # out, err = process.communicate()
    # print("ouput: '{}'".format(out))
    assert out == ""