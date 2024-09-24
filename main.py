import os
import time
import random
import requests
import datetime.datetime

from tabulate import tabulate
from playwright.sync_api import sync_playwright


USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")


HOME_URL = "https://linux.do/"
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a2e7817c-baf3-4773-a734-c38d9e5c71bc"


class LinuxDoBrowser:
    def __init__(self) -> None:
        self.pw = sync_playwright().start()
        self.browser = self.pw.firefox.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(HOME_URL)

    def login(self):
        self.page.click(".login-button .d-button-label")
        time.sleep(2)
        self.page.fill("#login-account-name", USERNAME)
        time.sleep(2)
        self.page.fill("#login-account-password", PASSWORD)
        time.sleep(2)
        self.page.click("#login-button")
        time.sleep(10)
        user_ele = self.page.query_selector("#current-user")
        if not user_ele:
            print("Login failed")
            return False
        else:
            print("Check in success")
            return True

    def click_topic(self):
        for topic in self.page.query_selector_all("#list-area .title"):
            page = self.context.new_page()
            page.goto(HOME_URL + topic.get_attribute("href"))
            time.sleep(3)
            if random.random() < 0.02:  # 100 * 0.02 * 30 = 60
                self.click_like(page)
            time.sleep(3)
            page.close()

    def run(self):
        if not self.login():
            return
        self.click_topic()
        self.print_connect_info()
        self.send_wecom_msg("Github action linuxdo签到完成", )

    def click_like(self, page):
        page.locator(".discourse-reactions-reaction-button").first.click()
        print("Like success")

    def print_connect_info(self):
        page = self.context.new_page()
        page.goto("https://connect.linux.do/")
        rows = page.query_selector_all("table tr")

        info = []

        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) >= 3:
                project = cells[0].text_content().strip()
                current = cells[1].text_content().strip()
                requirement = cells[2].text_content().strip()
                info.append([project, current, requirement])

        print("--------------Connect Info-----------------")
        print(tabulate(info, headers=["项目", "当前", "要求"], tablefmt="pretty"))

        page.close()

    def send_wecom_msg(self, content, webhook_url=webhook_url):
        if not webhook_url:
            print('未配置wecom_webhook_url，不发送信息')
            return
        if not content:
            print('未配置content，不发送信息')
            return
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": content + '\n服务器时间' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            r = requests.post(webhook_url, data=json.dumps(data), timeout=10)
            print(f'调用企业微信接口返回： {r.text}')
            print('成功发送企业微信')
        except Exception as e:
            print(e, '发送企业微信失败')

if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        print("Please set USERNAME and PASSWORD")
        exit(1)
    l = LinuxDoBrowser()
    l.run()
