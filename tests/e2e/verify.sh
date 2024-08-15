#!/bin/bash

pushd tests/integration > /dev/null

for f in *; do 
  if [ -d $f  -a ! -h $f ];  
  then  
      cd -- "$f";  
      echo -n "Running verify.py for $f...";
      python3 verify.py > output 2>&1
      if [ $? -ne 0 ];
      then 
          echo "Failed"
          echo "Failure Reason:"
          cat output
          exit 1;
      else
          echo "Passed"
          rm output
      fi;
      cd ..;
  fi;
done;

popd > /dev/null
