import os

from selenium import webdriver

HUB_HOST = os.environ.get('HUB_HOST')
HUB_PORT = os.environ.get('HUB_PORT')
BROWSER_NAME = os.environ.get('BROWSER')

def sample():
	print("Setting up driver.")
	caps = {
		'browserName': BROWSER_NAME
	}
	driver = webdriver.Remote(
        command_executor=f'http://{HUB_HOST}:{HUB_PORT}/wd/hub',
        desired_capabilities=caps
    )
	print("Calling the URL.")
	driver.get("http://www.python.org")
	assert "Python" in driver.title
	print("Closing the driver.")
	driver.quit()


if __name__ == '__main__':
	sample()
