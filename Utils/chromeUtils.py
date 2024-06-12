from playwright.sync_api import sync_playwright


def run_playwright(playwright, url):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # 监听所有请求
    requests_list = []

    def log_requests(request):
        print(f"request url:{request.url}")
        requests_list.append(request.url)

    page.on("request", log_requests)
    page.goto(url, wait_until='load')

    # 获取请求后的内容
    resp_content = page.content()
    browser.close()
    return requests_list, resp_content


if __name__ == '__main__':
    url = "https://www.baidu.com/"
    with sync_playwright() as playwright:
        requests_list, content = run_playwright(playwright, url=url)
