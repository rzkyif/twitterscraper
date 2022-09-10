import json
import os
import sys
import time

from collections import OrderedDict
from getpass import getpass
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.support.relative_locator import locate_with
from webdriver_manager.chrome import ChromeDriverManager

def get_input(thing, default=None, hidden=False):
  res = ''

  prompt = f'Enter {(thing + ("" if default is None else " (" + str(default) + ")")): <40}: '
  if hidden:
    res = getpass(prompt)
  else:
    res = input(prompt)

  if res == '':
    if default is None:
      sys.exit(f'Invalid {thing}!')
    else:
      res = str(default)

  return res

def main():

  # get user input

  print('Twitter Scraper by rzkyif')
  print('NOTE: Default values in parentheses will be set if you press ENTER without typing.\n')

  input_login_username = get_input('Twitter username for login')
  input_login_password = get_input('Twitter password for login', hidden=True)
  input_target_username = get_input('Twitter username for scraping', 'Twitter')
  input_target_amount = int(get_input('scraping tweet amount', 100))
  input_wait_change = float(get_input('page change wait time', 5))
  input_wait_scroll = float(get_input('page scroll wait time', 0.5))

  # prepare driver

  service = Service(executable_path=ChromeDriverManager().install())
  options = Options()
  driver = Chrome(service=service, options=options)

  try:

    # PHASE 1: fill out username

    driver.get('https://twitter.com/i/flow/login')

    time.sleep(input_wait_change)

    login_username = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete=username]')
    login_next = driver.find_element(locate_with(By.CSS_SELECTOR, 'div[role=button]').below({By.CSS_SELECTOR: 'input[autocomplete=username]'}))

    login_username.send_keys(input_login_username)
    login_next.click()

    time.sleep(input_wait_change)

    # PHASE 2: fill out password and login

    login_password = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete=current-password]')
    login_login = driver.find_element(locate_with(By.CSS_SELECTOR, 'div[role=button]').below({By.CSS_SELECTOR: 'input[autocomplete=current-password]'}))

    login_password.send_keys(input_login_password)
    login_login.click()

    time.sleep(input_wait_change)

    # PHASE 3: open profile page, start collecting tweets

    driver.get(f'https://twitter.com/{input_target_username}')

    time.sleep(input_wait_change)

    timeline = driver.find_element(By.CSS_SELECTOR, f'div[aria-label*="’s Tweets"]>div:first-child')
    scraped_tweets = OrderedDict()
    scroll_height = driver.execute_script("return window.screen.height;") * 1.5
    
    try:
      i = 0
      count = 0
      while count < input_target_amount:
        tweets = timeline.find_elements(By.CSS_SELECTOR, '[data-testid=tweet]')
        for tweet in tweets:

          tweet_texts = tweet.find_elements(By.CSS_SELECTOR, '[data-testid=tweetText]>:first-child')

          if len(tweet_texts) < 1: continue # handles tweets with no text

          tweet_text = tweet_texts[0].text
          textHash = hash(tweet_text)

          if textHash == 0 or textHash in scraped_tweets.keys(): continue # handles tweets that are empty or detected multiple times

          tweet_user = tweet.find_element(By.CSS_SELECTOR, '[data-testid=User-Names]>:nth-child(2)>:first-child>:first-child>:first-child').text[1:]
          date = tweet.find_element(By.CSS_SELECTOR, '[data-testid=User-Names]>:nth-child(2)>:first-child>:nth-child(3)>:first-child').text

          scraped_tweets[hash(tweet_text)] = {
            'user': tweet_user,
            'date': date,
            'tweet': tweet_text
          }

          count += 1
          if count >= input_target_amount: break
        print(f'Collected {count} tweets.')
        i += 1
        driver.execute_script(f'document.scrollingElement.scrollTo(0, {scroll_height}*{i});')
        time.sleep(input_wait_scroll)

    finally:
      file_number = 0
      while os.path.exists(f'tweets_{file_number}.json'):
        file_number += 1

      print(f'Scraping stopped, saving to tweets_{file_number}.json...')

      with open(f'tweets_{file_number}.json', 'w') as f:
        json.dump(dict(list(scraped_tweets.items())[:input_target_amount]), f, indent=2)

      print('Done!')

  finally:
    driver.quit()

if __name__ == '__main__':
  main()