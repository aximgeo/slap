rm -rf dist
mkdir dist
python setup.py sdist bdist_wheel
twine upload -r $1 -u firkinim -p Obfu5c473! dist/*
