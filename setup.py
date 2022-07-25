from os.path import abspath, dirname, exists, join
from setuptools import find_packages, setup
from sys import version_info


def _check_python_version():
    """Check the used Python version."""
    if version_info[:2] < (3, 6):
        from logging import warning
        msg = 'The used Python version is not supported' \
              ' and tested, please upgrade Python >= 3.6'
        warning(msg)


def _read_text(path):
    """
    Read the content from a text file.

    Parameters
    ----------
    path : str
        The path to the file.

    Returns
    -------
    Return the content as string.
    """
    content = ''
    if exists(path):
        content = open(path, 'r', encoding='utf-8').read().strip()
    return content


def main():
    _check_python_version()

    name = 'sklearn-porter'
    desc = 'Transpile trained scikit-learn models ' \
           'to C, Java, JavaScript and others.'

    file_dir = abspath(dirname(__file__))

    # Read readme.md
    path_readme = join(file_dir, 'readme.md')
    long_desc = _read_text(path_readme)

    # Read __version__.txt
    path_version = join(file_dir, 'sklearn_porter', '__version__.txt')
    version = _read_text(path_version)

    setup(
        name=name,
        description=desc,
        long_description=long_desc,
        long_description_content_type='text/markdown',
        keywords=[
            'scikit-learn',
            'sklearn',
        ],
        url='https://github.com/nok/sklearn-porter',
        install_requires=[
            'scikit-learn>=0.17',
            'jinja2>=2.11',
            'joblib>=1',
            'loguru>=0.5',
            'tabulate>=0.8',
        ],
        extras_require={
            'development': [
                'codecov>=2.1',
                'jupytext>=1.10',
                'pylint>=2.7',
                'pytest-cov>=2.11',
                'pytest-xdist>=2.2',
                'pytest>=6.2',
                'twine>=3.3',
                'yapf>=0.30',
            ],
            'examples': [
                'notebook==5.*',
                'Pygments>=2.8'
            ],
        },
        packages=find_packages(exclude=['tests.*', 'tests']),
        test_suite='pytest',
        include_package_data=True,
        entry_points={
            'console_scripts': ['porter = sklearn_porter.cli.__main__:main'],
        },
        classifiers=[
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Topic :: Software Development',
            'Topic :: Scientific/Engineering',
        ],
        author='Darius Morawiec',
        author_email='nok@users.noreply.github.com',
        license='MIT',
        version=version,
    )


if __name__ == '__main__':
    main()
