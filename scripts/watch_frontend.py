import inotify.adapters
import re
import subprocess
import os

def files_to_watch():
    r = re.compile("^/code/frontend/(templates|src)")
    return lambda x: r.match(x[2])

def events_to_watch():
    skip_events = ['IN_ISDIR', 'IN_OPEN', 'IN_ACCESS', 'IN_CLOSE_NOWRITE']
    return lambda x: all(event not in x[1] for event in skip_events)

def comb(*args):
    return lambda x: all(f(x) for f in args)

def install_node_deps():
    os.chdir('frontend')
    subprocess.call(['npm','install'])
    os.chdir('..')

def main():
    install_node_deps()

    subprocess.call(['make', 'clean'])
    subprocess.call('make')

    i = inotify.adapters.InotifyTree("/code/frontend")
    grepper = comb(files_to_watch(), events_to_watch())

    while True:
        changes = list( filter(grepper, i.event_gen(timeout_s=0.5, yield_nones=False)) )
        if changes:
            print("Files updated rerunning")
            for c in changes:
                (_, type_names, path, filename) = c
                print("    PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(path, filename, type_names))
            subprocess.call('make')


if __name__ == '__main__':
    main()
