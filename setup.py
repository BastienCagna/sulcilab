import setuptools
import os.path as op
import re


def get_property(prop, project):
    result = re.findall(r'^{}\s*=\s*[\'"]([^\'"]*)[\'"]$'.format(
        prop), open(project + '/__init__.py').read(), re.MULTILINE)
    # if more than one matches, result.group(1) is a list
    v = result[0]
    assert type(v) == str
    return v


with open(op.join(op.split(__file__)[0], "README.md"), "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='sulcilab',
    version=get_property('__version__', 'sulcilab'),
    description="A WEB project to study Folding",
    author='Bastien Cagna',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='bastien.cagna@cea.fr',
    url='',

    packages=['sulcilab', 'sulcilab_gui'],
    install_requires=['Cython', 'fastapi', 'sqlalchemy', 'numpy', 'pandas', 'nibabel', 'matplotlib', 'PyJWT', 'python-decouple', 'tqdm', 'pyqt5'],
    extras_require={
        'dev': [
            'pytest'
        ]
    },
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ]
)
