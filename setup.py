from setuptools import setup

setup(
    name='THISDLChatBot',
    version='2.0.15A',
    description='A chatbot framework for THISDL chat rooms',
    url='https://github.com/huangdihd/THISDLChatBot',
    author='huangdihd',
    author_email='hd20100104@163.com',
    license='GPLv3',
    packages=['THISDLChatBot'],
    install_requires=['colorama', 'httpx', 'pillow', 'beautifulsoup4']
)
