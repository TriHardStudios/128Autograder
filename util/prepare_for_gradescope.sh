# usage should be prepare_for_gradescope <bin_dir> <generation_dir>

# clean any __pycache__
find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete


# manually copying these files as its more explit with what we are adding to the zip

cp "$2"/run.py "$1"/run.py
cp "$2"/setup.sh "$1"/setup.sh
cp "$2"/run_autograder "$1"/run_autograder
cp "$2"/requirements.txt "$1"/requirements.txt

# copy over testing framework
cp -r "$2"/TestingFramework "$1"/TestingFramework
cp -r "$2"/StudentSubmission "$1"/StudentSubmission

# copy over unit tests
mkdir "$1"/studentTests 
cp "$2"/studentTests/test* "$1"/studentTests/

if [ -d "$2/studentTests/data/files" ]
then
    cp -r "$2"/studentTests/data/files/ "$1"/studentTests/data/files/
fi


