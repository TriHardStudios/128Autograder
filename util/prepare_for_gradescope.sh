# usage should be prepare_for_gradescope <bin_dir> <generation_dir>

# manually copying these files as its more explit with what we are adding to the zip

cp $2/run.py $1/run.py
cp $2/setup.sh $1/setup.sh
cp $2/run_autograder $1/run_autograder
cp $2/requirements.txt $1/requirements.txt


# copy over unit tests
cp -r $2/tests $1/tests

