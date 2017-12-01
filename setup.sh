setupATLAS
lsetup python
lsetup root

export base=`pwd`
export vpython=$base/venv

if [ -d "$vpython" ]; then
    echo "Activating virtual python environment"
    export VIRTUAL_ENV_DISABLE_PROMPT=1
    source $vpython/bin/activate
else
    echo "Creating virtual python environment"
    virtualenv -p `which python` $vpython
    source $vpython/bin/activate
    # update some core tools
    pip install --upgrade pip
    pip install --upgrade setuptools
    # install all the software
    pip install numpy scipy matplotlib rootpy    
fi

cd $base
export PYTHONPATH=$PYTHONPATH:`pwd`
