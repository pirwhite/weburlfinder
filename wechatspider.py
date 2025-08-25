#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌸 微信开放平台接口提取工具 by p1r07 🌸 
✧*｡٩(ˊᗜˋ*)و✧*｡

作者：p1r07
版本：6.0.0 (命令行版)
更新：2025-08-25
依托文档：https://developers.weixin.qq.com/doc/oplatform/developers/dev/api/

✨ 功能亮点：
✓ 自定义验证字段配置（适配微信API变更）
✓ 自动/手动双模式获取登录态
✓ 服务号/订阅号/小程序全类型支持
✓ 灵活的字段验证规则配置
✓ 简洁高效的命令行操作体验
"""

import os
import sys
import csv
import re
import time
import random
import logging
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# ====================== 日志配置 ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('wechat_api_crawler.log'), logging.StreamHandler()]
)

# ====================== 二次元样式与图标 ======================
class AnimeStyle:
    """超萌二次元风格配置 ✧(◍˃̶ᗜ˂̶◍)✩"""
    # 图标集合
    ICONS = {
        "success": "✅",
        "error": "❌",
        "info": "ℹ️",
        "warning": "⚠️",
        "search": "🔍",
        "file": "📄",
        "config": "⚙️",
        "cookie": "🍪",
        "token": "🔑",
        "article": "📝",
        "mini": "📱",
        "export": "💾",
        "clear": "🧹",
        "exit": "🚪",
        "about": "ℹ️"
    }
    
    @staticmethod
    def print_title():
        """打印标题"""
        print("\n" + "=" * 60)
        print(f"🌸 微信开放平台接口提取工具 by p1r07 🌸".center(60))
        print(f"✧*｡٩(ˊᗜˋ*)و✧*｡ 版本: 6.0.0 (命令行版)".center(60))
        print("=" * 60 + "\n")
    
    @staticmethod
    def print_menu():
        """打印主菜单"""
        menu = f"""
{AnimeStyle.ICONS['info']}  请选择操作 (输入数字1-9):
1.  {AnimeStyle.ICONS['cookie']}  获取/输入微信Cookie
2.  {AnimeStyle.ICONS['token']}  验证登录态
3.  {AnimeStyle.ICONS['search']}  搜索公众号文章
4.  {AnimeStyle.ICONS['mini']}   搜索小程序
5.  {AnimeStyle.ICONS['export']}  导出结果到CSV
6.  {AnimeStyle.ICONS['clear']}   清空当前结果
7.  {AnimeStyle.ICONS['config']}  配置验证规则
8.  {AnimeStyle.ICONS['about']}   关于本工具
9.  {AnimeStyle.ICONS['exit']}    退出工具
        """
        print(menu)
        print("-" * 60)

# ====================== 配置管理类 ======================
class ValidationConfig:
    """验证规则配置管理 (◍•ᴗ•◍)"""
    def __init__(self):
        # 默认验证字段（基于微信开放平台文档）
        self.default_core_fields = "wxuin, mm_lang"  # 核心用户标识字段
        self.default_session_fields = "wxsid, slave_sid, sessionid"  # 会话字段
        self.default_token_pattern = r'token=(\d+)'  # Token提取正则
        self.default_api_timeout = 15  # API超时时间（秒）
        
        # 当前配置
        self.core_fields = self.default_core_fields
        self.session_fields = self.default_session_fields
        self.token_pattern = self.default_token_pattern
        self.api_timeout = self.default_api_timeout
        self.config_file = "wechat_api_config.ini"
        
        # 尝试加载配置文件
        self.load_config()

    def get_core_fields_list(self):
        """获取核心字段列表"""
        return [f.strip() for f in self.core_fields.split(',') if f.strip()]

    def get_session_fields_list(self):
        """获取会话字段列表"""
        return [f.strip() for f in self.session_fields.split(',') if f.strip()]

    def reset_to_default(self):
        """重置为默认配置"""
        self.core_fields = self.default_core_fields
        self.session_fields = self.default_session_fields
        self.token_pattern = self.default_token_pattern
        self.api_timeout = self.default_api_timeout
        self.save_config()
        return "配置已重置为默认值 ✧*｡٩(ˊᗜˋ*)و✧*｡"

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(f"core_fields={self.core_fields}\n")
                f.write(f"session_fields={self.session_fields}\n")
                f.write(f"token_pattern={self.token_pattern}\n")
                f.write(f"api_timeout={self.api_timeout}\n")
            return f"{AnimeStyle.ICONS['success']} 配置已保存到 {self.config_file}"
        except Exception as e:
            return f"{AnimeStyle.ICONS['error']} 保存配置失败: {str(e)}"

    def load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            if key == 'core_fields':
                                self.core_fields = value
                            elif key == 'session_fields':
                                self.session_fields = value
                            elif key == 'token_pattern':
                                self.token_pattern = value
                            elif key == 'api_timeout':
                                self.api_timeout = int(value)
                return f"{AnimeStyle.ICONS['success']} 已加载配置文件"
            return f"{AnimeStyle.ICONS['info']} 未找到配置文件，使用默认配置"
        except Exception as e:
            return f"{AnimeStyle.ICONS['warning']} 加载配置失败: {str(e)}，使用默认配置"

    def print_config(self):
        """打印当前配置"""
        print("\n" + "-" * 50)
        print(f"{AnimeStyle.ICONS['config']} 当前验证规则配置:")
        print(f"1. 核心用户字段 (必填): {self.core_fields}")
        print(f"2. 会话字段 (至少一个): {self.session_fields}")
        print(f"3. Token提取正则: {self.token_pattern}")
        print(f"4. API超时时间: {self.api_timeout}秒")
        print("-" * 50 + "\n")

    def configure_interactive(self):
        """交互式配置"""
        self.print_config()
        
        print(f"{AnimeStyle.ICONS['info']} 按回车保留当前值，输入新值进行修改")
        
        # 核心字段配置
        core_fields = input(f"核心用户字段 [{self.core_fields}]: ").strip()
        if core_fields:
            self.core_fields = core_fields
            
        # 会话字段配置
        session_fields = input(f"会话字段 [{self.session_fields}]: ").strip()
        if session_fields:
            self.session_fields = session_fields
            
        # Token正则配置
        token_pattern = input(f"Token提取正则 [{self.token_pattern}]: ").strip()
        if token_pattern:
            self.token_pattern = token_pattern
            
        # 超时配置
        try:
            timeout = input(f"API超时时间 [{self.api_timeout}]: ").strip()
            if timeout:
                self.api_timeout = int(timeout)
        except ValueError:
            print(f"{AnimeStyle.ICONS['warning']} 无效的超时时间，保持原值")
            
        return self.save_config()

# ====================== Cookie自动获取类 ======================
class WeChatCookieAutoGetter:
    """微信Cookie自动获取器 (๑＞ڡ＜)☆"""
    
    @staticmethod
    def get_wechat_cookies(source=0):
        """从指定来源获取Cookie"""
        try:
            methods = [
                WeChatCookieAutoGetter._get_from_chrome,
                WeChatCookieAutoGetter._get_from_edge,
                WeChatCookieAutoGetter._get_from_wechat_app
            ]
            
            if 1 <= source <= len(methods):
                # 使用指定的方法
                cookies = methods[source-1]()
                if cookies and WeChatCookieAutoGetter._validate_cookie_basic(cookies):
                    logging.info("成功获取微信Cookie")
                    return cookies
                return None
            else:
                # 尝试所有方法
                for method in methods:
                    cookies = method()
                    if cookies and WeChatCookieAutoGetter._validate_cookie_basic(cookies):
                        logging.info("成功获取微信Cookie")
                        return cookies
            
            logging.warning("所有获取Cookie的方法都失败了")
            return None
            
        except Exception as e:
            logging.error(f"获取Cookie时出错: {str(e)}")
            return None
    
    @staticmethod
    def _validate_cookie_basic(cookie_str):
        """基础Cookie格式验证"""
        return cookie_str and '=' in cookie_str and ';' in cookie_str
    
    @staticmethod
    def _cookie_str_to_dict(cookie_str):
        """Cookie字符串转字典"""
        cookies = {}
        for item in cookie_str.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key.strip()] = value.strip()
        return cookies
    
    @staticmethod
    def _dict_to_cookie_str(cookie_dict):
        """Cookie字典转字符串"""
        return '; '.join([f"{k}={v}" for k, v in cookie_dict.items()])
    
    @staticmethod
    def _get_from_chrome():
        """从Chrome浏览器获取Cookie"""
        try:
            # 尝试导入必要的库
            try:
                import win32crypt
                import json
                import base64
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            except ImportError:
                logging.warning("缺少Chrome Cookie获取所需的库")
                return None
                
            appdata = os.getenv('LOCALAPPDATA')
            chrome_cookie_path = Path(appdata) / "Google" / "Chrome" / "User Data" / "Default" / "Cookies"
            if not chrome_cookie_path.exists():
                return None
                
            # 获取加密密钥
            local_state_path = Path(appdata) / "Google" / "Chrome" / "User Data" / "Local State"
            with open(local_state_path, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]
            key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            
            # 查询微信相关Cookie
            import sqlite3
            conn = sqlite3.connect(str(chrome_cookie_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%mp.weixin.qq.com%'")
            
            cookies = {}
            for name, encrypted_value in cursor.fetchall():
                if not encrypted_value:
                    continue
                    
                try:
                    nonce = encrypted_value[3:15]
                    ciphertext = encrypted_value[15:]
                    aesgcm = AESGCM(key)
                    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
                    cookies[name] = decrypted.decode('utf-8')
                except:
                    continue
            
            conn.close()
            return WeChatCookieAutoGetter._dict_to_cookie_str(cookies) if cookies else None
            
        except Exception as e:
            logging.warning(f"Chrome Cookie获取失败: {str(e)}")
            return None
    
    @staticmethod
    def _get_from_edge():
        """从Edge浏览器获取Cookie"""
        try:
            # 尝试导入必要的库
            try:
                import win32crypt
                import json
                import base64
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            except ImportError:
                logging.warning("缺少Edge Cookie获取所需的库")
                return None
                
            appdata = os.getenv('LOCALAPPDATA')
            edge_cookie_path = Path(appdata) / "Microsoft" / "Edge" / "User Data" / "Default" / "Cookies"
            if not edge_cookie_path.exists():
                return None
                
            # 获取加密密钥
            local_state_path = Path(appdata) / "Microsoft" / "Edge" / "User Data" / "Local State"
            with open(local_state_path, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]
            key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            
            # 查询微信相关Cookie
            import sqlite3
            conn = sqlite3.connect(str(edge_cookie_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%mp.weixin.qq.com%'")
            
            cookies = {}
            for name, encrypted_value in cursor.fetchall():
                if not encrypted_value:
                    continue
                    
                try:
                    nonce = encrypted_value[3:15]
                    ciphertext = encrypted_value[15:]
                    aesgcm = AESGCM(key)
                    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
                    cookies[name] = decrypted.decode('utf-8')
                except:
                    continue
            
            conn.close()
            return WeChatCookieAutoGetter._dict_to_cookie_str(cookies) if cookies else None
            
        except Exception as e:
            logging.warning(f"Edge Cookie获取失败: {str(e)}")
            return None
    
    @staticmethod
    def _get_from_wechat_app():
        """从微信客户端获取Cookie"""
        try:
            appdata = os.getenv('APPDATA')
            wechat_paths = [
                Path(appdata) / "Tencent" / "WeChat" / "XPlugin" / "Plugins" / "WeChatBrowser" / "User Data" / "Default" / "Cookies",
                Path(appdata) / "Tencent" / "WeChat" / "WeChat Files" / "All Users" / "Cookies"
            ]
            
            for cookie_path in wechat_paths:
                if cookie_path.exists():
                    import sqlite3
                    conn = sqlite3.connect(str(cookie_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, value FROM cookies WHERE host LIKE '%mp.weixin.qq.com%'")
                    
                    cookies = {}
                    for name, value in cursor.fetchall():
                        if name and value:
                            cookies[name] = value
                    
                    conn.close()
                    return WeChatCookieAutoGetter._dict_to_cookie_str(cookies) if cookies else None
            
            return None
            
        except Exception as e:
            logging.warning(f"微信客户端Cookie获取失败: {str(e)}")
            return None

# ====================== 爬虫核心类 ======================
class WeChatAPICrawler:
    """微信API爬虫核心 ✧థ౪థ✧"""
    def __init__(self, config: ValidationConfig):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'https://mp.weixin.qq.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.config = config  # 验证配置
        self.cookies = {}
        self.token = None
        self.last_request_time = 0
        self.request_delay = (1.5, 2.5)  # 防Ban延迟
        self.results = []  # 存储爬取结果

    def set_request_delay(self, delay):
        """设置请求延迟"""
        self.request_delay = (delay, delay + 1)

    def _request_with_delay(self, url, params=None, method='GET', data=None):
        """带延迟的API请求"""
        delay = random.uniform(*self.request_delay)
        elapsed = time.time() - self.last_request_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        
        try:
            if method == 'GET':
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=self.headers, 
                    timeout=self.config.api_timeout
                )
            else:
                response = self.session.post(
                    url, 
                    params=params, 
                    data=data, 
                    headers=self.headers, 
                    timeout=self.config.api_timeout
                )
            
            self.last_request_time = time.time()
            
            if response.status_code not in [200, 404]:
                error_map = {
                    401: "未授权访问（Cookie无效）",
                    403: "访问被拒绝（权限不足）",
                    429: "请求过于频繁（触发限流）",
                    500: "服务器错误（API异常）"
                }
                error_msg = error_map.get(response.status_code, f"HTTP错误 {response.status_code}")
                raise Exception(f"API请求失败: {error_msg}")
            
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")

    def validate_cookie_format(self, cookies):
        """基于自定义规则验证Cookie格式"""
        core_fields = self.config.get_core_fields_list()
        session_fields = self.config.get_session_fields_list()
        
        # 验证核心字段
        missing_core = [f for f in core_fields if f not in cookies]
        if missing_core:
            return False, f"缺少核心字段: {', '.join(missing_core)}（参考微信开放平台文档）"
        
        # 验证会话字段（至少存在一个）
        has_session = any(f in cookies for f in session_fields)
        if not has_session:
            return False, f"缺少会话字段（至少需要一个）: {', '.join(session_fields)}"
            
        return True, "Cookie格式验证通过 ✧◝(⁰▿⁰)◜✧"

    def set_cookies_and_token(self, cookies, token=None):
        """设置并验证登录态"""
        # 解析Cookie
        cookie_dict = {k.strip(): v.strip() for item in cookies.split(';') 
                      for k, v in [item.split('=', 1)] if '=' in item}
        
        # 格式验证
        format_valid, format_msg = self.validate_cookie_format(cookie_dict)
        if not format_valid:
            return False, format_msg
        
        self.cookies = cookie_dict
        self.session.cookies.update(cookie_dict)
        
        # 手动设置Token
        if token:
            self.token = token
            return True, "Token已手动设置 ✔️"
        
        # 自动提取Token（使用自定义正则）
        try:
            token_pages = [
                "https://mp.weixin.qq.com/cgi-bin/home",
                "https://mp.weixin.qq.com/cgi-bin/menu?t=menu/list&token=&lang=zh_CN",
                "https://mp.weixin.qq.com/"
            ]
            
            for page in token_pages:
                response = self._request_with_delay(page)
                if "loginpage" in response.url:
                    return False, "Cookie无效或已过期，需重新登录"
                
                # 使用自定义正则提取Token
                token_match = re.search(self.config.token_pattern, response.text)
                if token_match:
                    self.token = token_match.group(1)
                    return True, f"Token自动提取成功: {self.token} ✨"
            
            return False, f"无法匹配Token（正则: {self.config.token_pattern}）"
        except Exception as e:
            return False, f"Token提取失败: {str(e)}"

    def search_public_accounts(self, keyword, account_type='all'):
        """搜索公众号（支持类型筛选）"""
        if not self.token:
            raise Exception("Token未设置，请先验证登录态")
        
        # 账号类型映射（基于微信API文档）
        type_map = {
            'all': 0,       # 全部
            'official': 1,  # 公众号
            'service': 2,   # 服务号
            'subscription': 3  # 订阅号
        }
        search_type = type_map.get(account_type, 0)
            
        search_urls = [
            "https://mp.weixin.qq.com/cgi-bin/searchbiz",
            "https://mp.weixin.qq.com/api/searchbiz"
        ]
        
        params = {
            'action': 'search_biz',
            'token': self.token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'query': keyword,
            'begin': '0',
            'count': '10',
            'type': search_type
        }
        
        for url in search_urls:
            try:
                response = self._request_with_delay(url, params=params)
                data = response.json()
                
                if 'base_resp' in data and data['base_resp']['ret'] != 0:
                    err_msg = data['base_resp'].get('err_msg', '未知错误')
                    if data['base_resp']['ret'] == 200013:  # 频率限制
                        time.sleep(5)
                        continue
                    raise Exception(f"搜索失败: {err_msg}")
                
                if 'list' in data and len(data['list']) > 0:
                    return data['list']
            except Exception as e:
                logging.warning(f"搜索接口 {url} 失败: {str(e)}")
                continue
        
        return []
    
    def search_miniprograms(self, keyword):
        """搜索小程序"""
        if not self.token:
            raise Exception("Token未设置，请先验证登录态")
            
        search_url = "https://mp.weixin.qq.com/wxa-api/search/wxaapp"
        
        params = {
            'action': 'search',
            'token': self.token,
            'lang': 'zh_CN',
            'keyword': keyword,
            'page': 1,
            'num': 10
        }
        
        try:
            response = self._request_with_delay(search_url, params=params)
            data = response.json()
            
            if data.get('base_resp', {}).get('ret', -1) != 0:
                err_msg = data.get('base_resp', {}).get('err_msg', '未知错误')
                raise Exception(f"小程序搜索失败: {err_msg}")
                
            return data.get('app_list', [])
        except Exception as e:
            logging.error(f"小程序搜索失败: {str(e)}")
            raise

    def get_all_articles(self, fakeid, max_pages=10):
        """获取公众号全部文章"""
        if not self.token:
            raise Exception("Token未设置，请先验证登录态")
            
        articles = []
        url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        page = 0
        
        while page < max_pages:
            params = {
                'action': 'list_ex',
                'begin': str(page * 10),
                'count': '10',
                'fakeid': fakeid,
                'type': '9',
                'token': self.token,
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': '1'
            }
            
            try:
                response = self._request_with_delay(url, params=params)
                data = response.json()
                
                if 'base_resp' in data and data['base_resp']['ret'] != 0:
                    err_msg = data['base_resp'].get('err_msg', '未知错误')
                    raise Exception(f"获取文章失败: {err_msg}")
                
                current_articles = data.get('app_msg_list', [])
                if not current_articles:
                    break
                
                articles.extend(current_articles)
                print(f"{AnimeStyle.ICONS['info']} 已获取第 {page+1} 页文章，共 {len(articles)} 篇")
                
                if not data.get('has_more', 0):
                    break
                
                page += 1
            except Exception as e:
                print(f"{AnimeStyle.ICONS['warning']} 获取第 {page+1} 页文章失败: {str(e)}")
                if page == 0:
                    raise
                time.sleep(3)
                continue
        
        return articles

    def extract_mini_links(self, article_url):
        """提取文章中的小程序链接"""
        try:
            response = self._request_with_delay(article_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            mini_links = set()
            
            # 提取<a>标签中的小程序链接
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(key in href for key in ['miniprogram', 'wxurl', 'weapp', 'appmsg']):
                    if href.startswith('//'):
                        href = f"https:{href}"
                    elif not href.startswith('http'):
                        href = f"https://mp.weixin.qq.com{href}"
                    mini_links.add(href)
            
            # 提取脚本中的链接
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    patterns = [
                        r'https?://[^\s"\']+?miniprogram[^\s"\']*',
                        r'https?://[^\s"\']+?weixin\.qq\.com/[^\s"\']+?appid[^\s"\']*'
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, str(script.string))
                        for match in matches:
                            mini_links.add(match)
            
            return list(mini_links)
        except Exception as e:
            print(f"{AnimeStyle.ICONS['warning']} 提取小程序链接失败: {str(e)}")
            return []

    def search_account_articles(self, keyword, account_type='all', max_pages=5):
        """搜索公众号文章并提取小程序链接"""
        print(f"{AnimeStyle.ICONS['search']} 正在搜索关键词为「{keyword}」的{self._get_account_type_name(account_type)}...")
        accounts = self.search_public_accounts(keyword, account_type)
        
        if not accounts:
            return False, f"未找到关键词为「{keyword}」的账号 (╥_╥)"

        # 显示找到的账号并让用户选择
        print(f"\n{AnimeStyle.ICONS['success']} 找到以下账号:")
        for i, account in enumerate(accounts[:5], 1):
            print(f"{i}. {account['nickname']} - {account.get('alias', '无别名')}")
        
        try:
            choice = input("\n请选择要查看的账号 (1-5，默认1): ").strip()
            index = int(choice) - 1 if choice else 0
            if index < 0 or index >= min(5, len(accounts)):
                index = 0
        except ValueError:
            index = 0
            
        target_account = accounts[index]
        print(f"\n{AnimeStyle.ICONS['info']} 已选择账号: {target_account['nickname']} ✧*｡٩(ˊᗜˋ*)و✧*｡")
        
        print(f"{AnimeStyle.ICONS['article']} 正在获取历史文章... (最多{max_pages}页)")
        articles = self.get_all_articles(target_account['fakeid'], max_pages)
        
        if not articles:
            return False, "该账号没有可获取的文章 (╯︵╰)"

        results = []
        total = len(articles)
        print(f"\n{AnimeStyle.ICONS['info']} 开始提取小程序链接 ({total}篇文章):")
        
        for i, article in enumerate(articles):
            print(f"\n{AnimeStyle.ICONS['article']} 处理文章 {i+1}/{total}:")
            title = article.get('title', '无标题')
            print(f"标题: {title}")
            
            mini_links = self.crawler.extract_mini_links(article['link'])
            publish_time = datetime.fromtimestamp(article['update_time']).strftime('%Y-%m-%d %H:%M')
            
            print(f"发布时间: {publish_time}")
            print(f"文章链接: {article['link']}")
            
            if mini_links:
                print(f"{AnimeStyle.ICONS['mini']} 找到 {len(mini_links)} 个小程序链接:")
                for link in mini_links:
                    print(f"- {link}")
            else:
                print(f"{AnimeStyle.ICONS['info']} 未找到小程序链接")
            
            results.append({
                'type': 'article',
                'title': title,
                'link': article['link'],
                'mini_links': mini_links,
                'time': publish_time,
                'account': target_account['nickname']
            })
        
        self.results = results
        return True, f"处理完成！共分析 {len(results)} 篇文章"

    def search_mini_programs(self, keyword):
        """搜索小程序并保存结果"""
        print(f"{AnimeStyle.ICONS['mini']} 正在搜索关键词为「{keyword}」的小程序...")
        miniprograms = self.search_miniprograms(keyword)
        
        if not miniprograms:
            return False, f"未找到关键词为「{keyword}」的小程序 (╥_╥)"

        results = []
        total = len(miniprograms)
        print(f"\n{AnimeStyle.ICONS['success']} 找到 {total} 个小程序:")
        
        for i, mini in enumerate(miniprograms):
            name = mini.get('nickname', '无名小程序')
            appid = mini.get('appid', '')
            desc = mini.get('desc', '无描述')
            link = f"weixin://dl/business/?t={mini.get('username', '')}"
            
            print(f"\n{i+1}. {name}")
            print(f"   AppID: {appid}")
            print(f"   描述: {desc}")
            print(f"   访问链接: {link}")
            
            results.append({
                'type': 'miniprogram',
                'name': name,
                'appid': appid,
                'desc': desc,
                'link': link
            })
        
        self.results = results
        return True, f"搜索完成！共找到 {len(results)} 个小程序"

    def _get_account_type_name(self, account_type):
        """获取账号类型名称"""
        type_names = {
            'all': '所有账号',
            'official': '公众号',
            'service': '服务号',
            'subscription': '订阅号'
        }
        return type_names.get(account_type, '账号')

    def export_results(self, filename=None):
        """导出结果到CSV"""
        if not self.results:
            return False, "没有结果可导出 (╥_╥)"
            
        if not filename:
            filename = f"wechat_api_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入表头
                if self.results[0]['type'] == 'article':
                    writer.writerow(['文章标题', '公众号', '发布时间', '文章链接', '小程序链接'])
                else:
                    writer.writerow(['小程序名称', 'AppID', '描述', '访问链接'])
                
                # 写入数据
                for item in self.results:
                    if item['type'] == 'article':
                        mini_links = '\n'.join(item['mini_links']) if item['mini_links'] else ""
                        writer.writerow([
                            item['title'],
                            item['account'],
                            item['time'],
                            item['link'],
                            mini_links
                        ])
                    else:
                        writer.writerow([
                            item['name'],
                            item['appid'],
                            item['desc'],
                            item['link']
                        ])
            
            return True, f"数据已成功导出到 {filename} {AnimeStyle.ICONS['success']}"
        except Exception as e:
            return False, f"导出失败: {str(e)} {AnimeStyle.ICONS['error']}"

    def clear_results(self):
        """清空结果"""
        self.results = []
        return "已清空当前结果 {AnimeStyle.ICONS['clear']}"

# ====================== 主程序类 ======================
class WeChatAPICLI:
    """命令行交互主类 (✧ω✧)"""
    def __init__(self):
        self.config = ValidationConfig()
        self.crawler = WeChatAPICrawler(self.config)
        self.cookie = ""
        self.token = ""
        self.init_message()

    def init_message(self):
        """初始化消息"""
        print(f"{AnimeStyle.ICONS['info']} {self.config.load_config()}")
        print(f"{AnimeStyle.ICONS['info']} 提示：请先获取并验证Cookie，然后再进行搜索操作")

    def run(self):
        """运行主循环"""
        while True:
            AnimeStyle.print_title()
            
            # 显示当前状态
            self.print_status()
            
            # 显示菜单
            AnimeStyle.print_menu()
            
            # 获取用户选择
            try:
                choice = input("请输入操作编号: ").strip()
                
                # 根据选择执行相应功能
                if choice == '1':
                    self.handle_get_cookie()
                elif choice == '2':
                    self.handle_verify_auth()
                elif choice == '3':
                    self.handle_search_accounts()
                elif choice == '4':
                    self.handle_search_miniprograms()
                elif choice == '5':
                    self.handle_export()
                elif choice == '6':
                    self.handle_clear()
                elif choice == '7':
                    self.handle_config()
                elif choice == '8':
                    self.handle_about()
                elif choice == '9':
                    print(f"\n{AnimeStyle.ICONS['exit']} 感谢使用微信开放平台接口提取工具，再见！")
                    print("✧*｡٩(ˊᗜˋ*)و✧*｡\n")
                    break
                else:
                    print(f"{AnimeStyle.ICONS['warning']} 无效的选择，请输入1-9之间的数字")
            
            except KeyboardInterrupt:
                print(f"\n{AnimeStyle.ICONS['warning']} 检测到中断，返回主菜单")
            except Exception as e:
                print(f"{AnimeStyle.ICONS['error']} 操作出错: {str(e)}")
            
            # 等待用户按回车继续
            input("\n按回车键继续...")
            self.clear_screen()

    def print_status(self):
        """打印当前状态"""
        status = []
        status.append(f"{AnimeStyle.ICONS['cookie']} Cookie状态: {'已设置' if self.cookie else '未设置'}")
        status.append(f"{AnimeStyle.ICONS['token']} Token状态: {'已获取' if self.crawler.token else '未获取'}")
        status.append(f"{AnimeStyle.ICONS['file']} 结果数量: {len(self.crawler.results)}")
        print(" | ".join(status))
        print("-" * 60)

    def clear_screen(self):
        """清屏"""
        if sys.platform.startswith('win32'):
            os.system('cls')
        else:
            os.system('clear')

    def handle_get_cookie(self):
        """处理获取Cookie"""
        print(f"\n{AnimeStyle.ICONS['cookie']} 获取/输入微信Cookie")
        print("-" * 50)
        
        print("请选择Cookie来源:")
        print("1. 手动输入")
        print("2. 自动获取(Chrome浏览器)")
        print("3. 自动获取(Edge浏览器)")
        print("4. 自动获取(微信客户端)")
        
        try:
            source = input("请选择 (1-4，默认1): ").strip()
            source = int(source) if source else 1
            
            if source == 1:
                # 手动输入
                cookie = input("\n请输入微信Cookie: ").strip()
                if cookie:
                    self.cookie = cookie
                    print(f"{AnimeStyle.ICONS['success']} Cookie已保存")
                    
                    # 询问是否输入Token
                    token = input("是否手动输入Token? (y/n，默认n): ").strip().lower()
                    if token == 'y':
                        self.token = input("请输入Token: ").strip()
                        print(f"{AnimeStyle.ICONS['info']} Token已保存")
                    else:
                        self.token = ""
                        
            else:
                # 自动获取
                print(f"\n{AnimeStyle.ICONS['info']} 正在从来源{source}获取Cookie... 这可能需要几秒钟")
                print(f"{AnimeStyle.ICONS['info']} 请确保已登录微信网页版或客户端")
                
                cookies = WeChatCookieAutoGetter.get_wechat_cookies(source)
                
                if cookies:
                    self.cookie = cookies
                    print(f"\n{AnimeStyle.ICONS['success']} Cookie获取成功！")
                    
                    # 尝试自动提取Token
                    try:
                        print(f"{AnimeStyle.ICONS['info']} 尝试自动提取Token...")
                        cookie_dict = WeChatCookieAutoGetter._cookie_str_to_dict(cookies)
                        self.crawler.session.cookies.update(cookie_dict)
                        response = self.crawler._request_with_delay("https://mp.weixin.qq.com/cgi-bin/home")
                        token_match = re.search(self.config.token_pattern, response.text)
                        
                        if token_match:
                            self.token = token_match.group(1)
                            print(f"{AnimeStyle.ICONS['success']} Token自动提取成功: {self.token}")
                        else:
                            print(f"{AnimeStyle.ICONS['warning']} 无法自动提取Token，请手动输入或验证时自动提取")
                            self.token = ""
                    except Exception as e:
                        print(f"{AnimeStyle.ICONS['warning']} Token提取失败: {str(e)}")
                        self.token = ""
                else:
                    print(f"{AnimeStyle.ICONS['error']} 无法获取有效的Cookie")
                    print(f"{AnimeStyle.ICONS['info']} 请尝试手动输入Cookie")
                    
        except ValueError:
            print(f"{AnimeStyle.ICONS['error']} 无效的输入")
        except Exception as e:
            print(f"{AnimeStyle.ICONS['error']} 操作出错: {str(e)}")

    def handle_verify_auth(self):
        """处理验证登录态"""
        if not self.cookie:
            print(f"{AnimeStyle.ICONS['warning']} 请先获取或输入Cookie")
            return
        
        try:
            print(f"\n{AnimeStyle.ICONS['token']} 正在验证登录态...")
            valid, msg = self.crawler.set_cookies_and_token(self.cookie, self.token)
            
            if valid:
                print(f"{AnimeStyle.ICONS['success']} {msg}")
                if self.crawler.token and not self.token:
                    self.token = self.crawler.token
                    print(f"自动提取的Token: {self.token}")
            else:
                print(f"{AnimeStyle.ICONS['error']} 验证失败: {msg}")
                
        except Exception as e:
            print(f"{AnimeStyle.ICONS['error']} 验证出错: {str(e)}")

    def handle_search_accounts(self):
        """处理搜索公众号文章"""
        if not self.crawler.token or not self.crawler.cookies:
            print(f"{AnimeStyle.ICONS['warning']} 请先验证登录态！")
            return
        
        try:
            keyword = input("\n请输入公众号关键词: ").strip()
            if not keyword:
                print(f"{AnimeStyle.ICONS['warning']} 关键词不能为空")
                return
            
            print("\n请选择账号类型:")
            print("1. 全部")
            print("2. 公众号")
            print("3. 服务号")
            print("4. 订阅号")
            
            type_choice = input("请选择 (1-4，默认1): ").strip()
            type_map = {
                '1': 'all',
                '2': 'official',
                '3': 'service',
                '4': 'subscription'
            }
            account_type = type_map.get(type_choice, 'all')
            
            try:
                max_pages = input("请输入最大页数 (1-20，默认5): ").strip()
                max_pages = int(max_pages) if max_pages else 5
                if max_pages < 1 or max_pages > 20:
                    max_pages = 5
            except ValueError:
                max_pages = 5
                
            try:
                delay = input("请输入请求延迟(秒) (1-5，默认2): ").strip()
                delay = int(delay) if delay else 2
                if delay < 1 or delay > 5:
                    delay = 2
            except ValueError:
                delay = 2
                
            self.crawler.set_request_delay(delay)
            
            # 执行搜索
            success, msg = self.crawler.search_account_articles(keyword, account_type, max_pages)
            if success:
                print(f"\n{AnimeStyle.ICONS['success']} {msg}")
            else:
                print(f"\n{AnimeStyle.ICONS['error']} {msg}")
                
        except Exception as e:
            print(f"{AnimeStyle.ICONS['error']} 搜索出错: {str(e)}")

    def handle_search_miniprograms(self):
        """处理搜索小程序"""
        if not self.crawler.token or not self.crawler.cookies:
            print(f"{AnimeStyle.ICONS['warning']} 请先验证登录态！")
            return
        
        try:
            keyword = input("\n请输入小程序关键词: ").strip()
            if not keyword:
                print(f"{AnimeStyle.ICONS['warning']} 关键词不能为空")
                return
            
            try:
                delay = input("请输入请求延迟(秒) (1-5，默认2): ").strip()
                delay = int(delay) if delay else 2
                if delay < 1 or delay > 5:
                    delay = 2
            except ValueError:
                delay = 2
                
            self.crawler.set_request_delay(delay)
            
            # 执行搜索
            success, msg = self.crawler.search_mini_programs(keyword)
            if success:
                print(f"\n{AnimeStyle.ICONS['success']} {msg}")
            else:
                print(f"\n{AnimeStyle.ICONS['error']} {msg}")
                
        except Exception as e:
            print(f"{AnimeStyle.ICONS['error']} 搜索出错: {str(e)}")

    def handle_export(self):
        """处理导出结果"""
        try:
            filename = input("\n请输入导出文件名 (默认自动生成): ").strip()
            success, msg = self.crawler.export_results(filename if filename else None)
            print(msg)
        except Exception as e:
            print(f"{AnimeStyle.ICONS['error']} 导出出错: {str(e)}")

    def handle_clear(self):
        """处理清空结果"""
        confirm = input(f"\n确定要清空当前结果吗? (y/n): ").strip().lower()
        if confirm == 'y':
            msg = self.crawler.clear_results()
            print(msg)
        else:
            print(f"{AnimeStyle.ICONS['info']} 已取消清空操作")

    def handle_config(self):
        """处理配置验证规则"""
        print(f"\n{AnimeStyle.ICONS['config']} 验证规则配置")
        print("-" * 50)
        print("1. 查看当前配置")
        print("2. 修改配置")
        print("3. 重置为默认配置")
        print("4. 返回主菜单")
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == '1':
            self.config.print_config()
        elif choice == '2':
            msg = self.config.configure_interactive()
            print(msg)
            # 更新爬虫配置
            self.crawler = WeChatAPICrawler(self.config)
        elif choice == '3':
            confirm = input("确定要重置为默认配置吗? (y/n): ").strip().lower()
            if confirm == 'y':
                msg = self.config.reset_to_default()
                print(msg)
                # 更新爬虫配置
                self.crawler = WeChatAPICrawler(self.config)
            else:
                print(f"{AnimeStyle.ICONS['info']} 已取消重置操作")
        elif choice == '4':
            print(f"{AnimeStyle.ICONS['info']} 返回主菜单")
        else:
            print(f"{AnimeStyle.ICONS['warning']} 无效的选择")

    def handle_about(self):
        """处理关于信息"""
        about_text = f"""
{AnimeStyle.ICONS['about']} 微信开放平台接口提取工具 v6.0.0 (命令行版)

作者: p1r07
更新: 2025-08-25
依托文档: https://developers.weixin.qq.com/doc/oplatform/developers/dev/api/

✨ 功能亮点:
✓ 自定义验证字段配置（适配微信API变更）
✓ 自动/手动双模式获取登录态
✓ 服务号/订阅号/小程序全类型支持
✓ 灵活的字段验证规则配置
✓ 简洁高效的命令行操作体验

使用提示:
- 请先获取并验证Cookie，然后再进行搜索
- 当微信API接口变更时，可通过配置功能适配新规则
- 导出的结果以CSV格式保存，可使用Excel等工具打开

✧*｡٩(ˊᗜˋ*)و✧*｡ 二次元风格工具 by p1r07
        """
        print(about_text)

# ====================== 主程序入口 ======================
def main():
    """主函数 (✧ω✧)"""
    try:
        # 检查必要的库
        import requests
        import bs4
    except ImportError as e:
        print(f"{AnimeStyle.ICONS['error']} 缺少依赖库: {e} (╥_╥)")
        print(f"{AnimeStyle.ICONS['info']} 正在尝试自动安装... (◍•ᴗ•◍)")
        try:
            import pip
            pip.main(['install', 'requests', 'beautifulsoup4', 'cryptography'])
            # Windows系统需要pywin32
            if sys.platform.startswith('win32'):
                pip.main(['install', 'pywin32'])
        except:
            print(f"{AnimeStyle.ICONS['error']} 自动安装失败，请手动运行:")
            print("pip install requests beautifulsoup4 cryptography")
            if sys.platform.startswith('win32'):
                print("pip install pywin32")
            return
    
    # 运行命令行界面
    cli = WeChatAPICLI()
    cli.run()

if __name__ == '__main__':
    main()
    