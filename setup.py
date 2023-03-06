from setuptools import setup

setup(
    name='insight_container_sync',
    version='0.0.1',
    author='saymurrmeow',
    install_requires=['fastapi[all]', 'docker'],
    include_package_data=True,
    packages=['app'],
    entry_points={
            'console_scripts': [
                'ci_app = app.main:main']},
)
