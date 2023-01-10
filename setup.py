from setuptools import setup

setup(
   name='vk_parser',
   version='1.0',
   description='Allows to find likes and comments of people on Vk.com, as well supports searching words and phrases and background searching',
   author='Doomcaster',
   author_email='webtalestoday@gmail.com',
   #packages=['vk_parser'],  #same as name
   install_requires=['psycopg2-binary', 'vkbottle', 'vk_api'], #external packages as dependencies
)
