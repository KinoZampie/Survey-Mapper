import os
'''
This document just resets the 'database'
being used for this project
'''

os.system("rm users/*.json")

with open('completed_users.txt', "w") as f:
    f.write("")

with open('completed_ssns.txt', "w") as f:
    f.write("")

with open('scores/economic.txt', "w") as f:
    f.write("")

with open('scores/diplomatic.txt', "w") as f:
    f.write("")

with open('scores/civil.txt', "w") as f:
    f.write("")

with open('scores/societal.txt', "w") as f:
    f.write("")
