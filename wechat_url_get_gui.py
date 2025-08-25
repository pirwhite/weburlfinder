#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌸 微信开放平台接口提取工具 by p1r07 🌸 
✧*｡٩(ˊᗜˋ*)و✧*｡

作者：p1r07
版本：6.0.0
更新：2025-08-25
依托文档：https://developers.weixin.qq.com/doc/oplatform/developers/dev/api/

✨ 功能亮点：
✓ 自定义验证字段配置（适配微信API变更）
✓ 自动/手动双模式获取登录态
✓ 服务号/订阅号/小程序全类型支持
✓ 可视化字段验证规则配置
✓ 超萌二次元交互界面
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
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QFileDialog, QMessageBox, QProgressBar, QGroupBox,
                            QSpinBox, QRadioButton, QButtonGroup, QTabWidget, 
                            QComboBox, QTextEdit, QFormLayout, QFrame)
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# ====================== 日志配置 ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('wechat_api_crawler.log'), logging.StreamHandler()]
)

# ====================== 二次元样式类 ======================
class AnimeStyle:
    """超萌二次元风格配置 ✧(◍˃̶ᗜ˂̶◍)✩"""
    PINK_MAIN = "#FF85A2"       # 主粉色
    PINK_LIGHT = "#FFD1DC"      # 浅粉色
    PINK_DARK = "#E64A8A"       # 深粉色
    PINK_WHITE = "#FFF5F8"      # 粉白色
    PINK_BLACK = "#2D2327"      # 文字色

    @staticmethod
    def apply_style(app):
        """应用二次元风格 ✧ω✧"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(AnimeStyle.PINK_WHITE))
        palette.setColor(QPalette.WindowText, QColor(AnimeStyle.PINK_DARK))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(AnimeStyle.PINK_LIGHT))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(AnimeStyle.PINK_DARK))
        palette.setColor(QPalette.Text, QColor(AnimeStyle.PINK_BLACK))
        palette.setColor(QPalette.Button, QColor(AnimeStyle.PINK_MAIN))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(AnimeStyle.PINK_MAIN))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        app.setPalette(palette)

        style = f"""
        QMainWindow {{
            background-color: {AnimeStyle.PINK_WHITE};
            border: 3px solid {AnimeStyle.PINK_LIGHT};
            border-radius: 18px;
            margin: 5px;
        }}
        
        QPushButton {{
            background-color: {AnimeStyle.PINK_MAIN};
            color: white;
            border: none;
            border-radius: 12px;
            padding: 8px 15px;
            font-family: 'Microsoft YaHei', 'SimHei';
            font-size: 14px;
            min-width: 90px;
        }}
        QPushButton:hover {{
            background-color: {AnimeStyle.PINK_DARK};
            transform: scale(1.05);
        }}
        QPushButton:pressed {{
            background-color: {AnimeStyle.PINK_DARK};
            transform: scale(0.98);
        }}
        QPushButton:disabled {{
            background-color: {AnimeStyle.PINK_LIGHT};
            color: #ffffff80;
        }}
        
        QLineEdit, QTextEdit, QComboBox {{
            border: 2px solid {AnimeStyle.PINK_LIGHT};
            border-radius: 10px;
            padding: 8px;
            background-color: white;
            selection-background-color: {AnimeStyle.PINK_LIGHT};
            font-family: 'Microsoft YaHei';
        }}
        
        QTableWidget {{
            background-color: white;
            alternate-background-color: {AnimeStyle.PINK_LIGHT}30;
            gridline-color: {AnimeStyle.PINK_LIGHT};
            border-radius: 10px;
            border: 1px solid {AnimeStyle.PINK_LIGHT};
        }}
        QHeaderView::section {{
            background-color: {AnimeStyle.PINK_MAIN};
            color: white;
            padding: 6px;
            border: none;
            border-radius: 5px;
        }}
        
        QProgressBar {{
            border: 2px solid {AnimeStyle.PINK_LIGHT};
            border-radius: 8px;
            text-align: center;
            background-color: white;
            height: 12px;
        }}
        QProgressBar::chunk {{
            background-color: {AnimeStyle.PINK_MAIN};
            border-radius: 6px;
        }}
        
        QLabel {{
            color: {AnimeStyle.PINK_DARK};
            font-family: 'Microsoft YaHei', 'SimHei';
        }}
        .title {{
            color: {AnimeStyle.PINK_DARK};
            font-size: 24px;
            font-weight: bold;
            text-shadow: 1px 1px 2px {AnimeStyle.PINK_LIGHT};
        }}
        .subtitle {{
            color: {AnimeStyle.PINK_DARK};
            font-size: 16px;
            font-weight: bold;
        }}
        .status-success {{ color: #4CAF50; }}
        .status-warning {{ color: #FF9800; }}
        .status-error {{ color: #F44336; }}
        
        QGroupBox {{
            border: 2px solid {AnimeStyle.PINK_LIGHT};
            border-radius: 10px;
            margin-top: 15px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px;
            color: {AnimeStyle.PINK_DARK};
            font-weight: bold;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {AnimeStyle.PINK_LIGHT};
            border-radius: 8px;
            background-color: white;
        }}
        QTabBar::tab {{
            background-color: {AnimeStyle.PINK_LIGHT};
            color: {AnimeStyle.PINK_DARK};
            padding: 6px 15px;
            border-radius: 6px;
            margin-right: 3px;
        }}
        QTabBar::tab:selected {{
            background-color: {AnimeStyle.PINK_MAIN};
            color: white;
        }}
        
        QFrame {{
            border: 1px dashed {AnimeStyle.PINK_LIGHT};
            border-radius: 8px;
        }}
        """
        app.setStyleSheet(style)

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

# ====================== Cookie自动获取类 ======================
class WeChatCookieAutoGetter:
    """微信Cookie自动获取器 (๑＞ڡ＜)☆"""
    
    @staticmethod
    def get_wechat_cookies():
        """从本地微信客户端或浏览器获取Cookie"""
        try:
            methods = [
                WeChatCookieAutoGetter._get_from_chrome,
                WeChatCookieAutoGetter._get_from_edge,
                WeChatCookieAutoGetter._get_from_wechat_app
            ]
            
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
        return '=' in cookie_str and ';' in cookie_str
    
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
            import win32crypt
            import json
            import base64
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
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
            import win32crypt
            import json
            import base64
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
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
                logging.info(f"已获取第 {page+1} 页文章，共 {len(articles)} 篇")
                
                if not data.get('has_more', 0):
                    break
                
                page += 1
            except Exception as e:
                logging.error(f"获取第 {page+1} 页文章失败: {str(e)}")
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
            logging.warning(f"提取小程序链接失败: {str(e)}")
            return []

# ====================== 爬虫线程类 ======================
class APICrawlThread(QThread):
    """API爬取线程（不阻塞UI） (◍•ᴗ•◍)"""
    progress_updated = pyqtSignal(int)
    results_ready = pyqtSignal(list, str)
    error_occurred = pyqtSignal(str)
    status_updated = pyqtSignal(str)

    def __init__(self, crawler, keyword, max_pages, search_type='account', account_type='all'):
        super().__init__()
        self.crawler = crawler
        self.keyword = keyword
        self.max_pages = max_pages
        self.search_type = search_type  # 'account' 或 'miniprogram'
        self.account_type = account_type
        self.running = True

    def run(self):
        try:
            if self.search_type == 'account':
                self._search_accounts()
            elif self.search_type == 'miniprogram':
                self._search_miniprograms()
                
        except Exception as e:
            self.error_occurred.emit(f"爬取失败: {str(e)}")

    def _search_accounts(self):
        """搜索公众号并处理"""
        self.status_updated.emit("正在搜索公众号... ୧(๑•̀⌄•́๑)૭")
        accounts = self.crawler.search_public_accounts(self.keyword, self.account_type)
        
        if not accounts:
            self.error_occurred.emit(f"未找到关键词为「{self.keyword}」的账号 (╥_╥)")
            return

        target_account = accounts[0]
        self.status_updated.emit(f"找到账号: {target_account['nickname']} ✧*｡٩(ˊᗜˋ*)و✧*｡")
        
        self.status_updated.emit("正在获取历史文章... (◍•ᴗ•◍)")
        articles = self.crawler.get_all_articles(target_account['fakeid'], self.max_pages)
        
        if not articles:
            self.error_occurred.emit("该账号没有可获取的文章 (╯︵╰)")
            return

        results = []
        total = len(articles)
        for i, article in enumerate(articles):
            if not self.running:
                break
            
            progress = int((i + 1) / total * 100)
            self.progress_updated.emit(progress)
            
            title = article.get('title', '无标题')
            self.status_updated.emit(f"处理文章 {i+1}/{total}: {title[:15]}...")
            
            mini_links = self.crawler.extract_mini_links(article['link'])
            publish_time = datetime.fromtimestamp(article['update_time']).strftime('%Y-%m-%d %H:%M')
            
            results.append({
                'title': title,
                'link': article['link'],
                'mini_links': mini_links,
                'time': publish_time,
                'account': target_account['nickname']
            })
        
        if not self.running:
            self.status_updated.emit("任务已取消 (｡•́︿•̀｡)")
            return

        self.results_ready.emit(results, 'account')
    
    def _search_miniprograms(self):
        """搜索小程序并处理"""
        self.status_updated.emit("正在搜索小程序... ୧(๑•̀⌄•́๑)૭")
        miniprograms = self.crawler.search_miniprograms(self.keyword)
        
        if not miniprograms:
            self.error_occurred.emit(f"未找到关键词为「{self.keyword}」的小程序 (╥_╥)")
            return

        results = []
        total = len(miniprograms)
        for i, mini in enumerate(miniprograms):
            if not self.running:
                break
            
            progress = int((i + 1) / total * 100)
            self.progress_updated.emit(progress)
            
            name = mini.get('nickname', '无名小程序')
            self.status_updated.emit(f"处理小程序 {i+1}/{total}: {name}")
            
            results.append({
                'name': name,
                'appid': mini.get('appid', ''),
                'desc': mini.get('desc', '无描述'),
                'link': f"weixin://dl/business/?t={mini.get('username', '')}"
            })
        
        if not self.running:
            self.status_updated.emit("任务已取消 (｡•́︿•̀｡)")
            return

        self.results_ready.emit(results, 'miniprogram')

    def stop(self):
        """停止线程"""
        self.running = False

# ====================== GUI界面类 ======================
class WeChatAPIGUI(QMainWindow):
    """主界面类 (✧ω✧)"""
    def __init__(self):
        super().__init__()
        self.validation_config = ValidationConfig()  # 验证配置
        self.crawler = WeChatAPICrawler(self.validation_config)
        self.crawl_thread = None
        self.init_ui()
        self.setWindowTitle("🌸 微信开放平台接口提取工具 by p1r07🌸")
        self.setMinimumSize(1100, 800)

    def init_ui(self):
        """初始化界面 ✧◝(⁰▿⁰)◜✧"""
        # 主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 标题区域
        title_frame = QWidget()
        title_layout = QHBoxLayout(title_frame)
        title_label = QLabel("🌸 微信开放平台接口提取工具 by p1r07 🌸")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        main_layout.addWidget(title_frame)

        # 主标签页
        main_tab = QTabWidget()
        
        # 1. 核心功能标签
        core_tab = QWidget()
        core_layout = QVBoxLayout(core_tab)
        
        # 认证区域
        auth_group = QGroupBox("✧ 登录态认证 ✧")
        auth_layout = QVBoxLayout()
        
        # Cookie来源选择
        source_layout = QHBoxLayout()
        source_label = QLabel("Cookie来源:")
        self.source_combo = QComboBox()
        self.source_combo.addItems(["手动输入", "自动获取(Chrome)", "自动获取(Edge)", "自动获取(微信客户端)"])
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_combo)
        auth_layout.addLayout(source_layout)
        
        # Cookie输入
        cookie_layout = QHBoxLayout()
        cookie_label = QLabel("微信Cookie:")
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText("格式: key1=value1; key2=value2（参考验证规则配置）")
        cookie_layout.addWidget(cookie_label)
        cookie_layout.addWidget(self.cookie_input)
        auth_layout.addLayout(cookie_layout)
        
        # Token输入
        token_layout = QHBoxLayout()
        token_label = QLabel("Token(可选):")
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("自动提取失败时手动输入")
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        auth_layout.addLayout(token_layout)
        
        # 自动获取按钮
        auto_get_layout = QHBoxLayout()
        self.auto_get_btn = QPushButton("从选中来源获取Cookie ✧")
        self.auto_get_btn.clicked.connect(self.auto_get_cookie)
        auto_get_layout.addWidget(self.auto_get_btn)
        auth_layout.addLayout(auto_get_layout)
        
        # 验证状态
        self.auth_status = QLabel("认证状态: 未验证 (๑•́ω•̀๑)")
        self.auth_status.setObjectName("status-warning")
        auth_layout.addWidget(self.auth_status)
        
        # 验证按钮
        verify_btn = QPushButton("验证登录态 ✧")
        verify_btn.clicked.connect(self.verify_auth)
        auth_layout.addWidget(verify_btn)
        
        auth_group.setLayout(auth_layout)
        core_layout.addWidget(auth_group)

        # 搜索设置区域
        search_tab = QTabWidget()
        
        # 公众号搜索标签
        account_tab = QWidget()
        account_layout = QVBoxLayout(account_tab)
        
        keyword_layout = QHBoxLayout()
        keyword_label = QLabel("公众号关键词:")
        self.account_keyword = QLineEdit()
        self.account_keyword.setPlaceholderText("输入公众号名称或ID")
        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.account_keyword)
        account_layout.addLayout(keyword_layout)
        
        # 账号类型选择
        type_layout = QHBoxLayout()
        type_label = QLabel("账号类型:")
        self.account_type_group = QButtonGroup()
        
        all_radio = QRadioButton("全部")
        all_radio.setChecked(True)
        official_radio = QRadioButton("公众号")
        service_radio = QRadioButton("服务号")
        subscription_radio = QRadioButton("订阅号")
        
        self.account_type_group.addButton(all_radio, 0)
        self.account_type_group.addButton(official_radio, 1)
        self.account_type_group.addButton(service_radio, 2)
        self.account_type_group.addButton(subscription_radio, 3)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(all_radio)
        type_layout.addWidget(official_radio)
        type_layout.addWidget(service_radio)
        type_layout.addWidget(subscription_radio)
        type_layout.addStretch()
        account_layout.addLayout(type_layout)
        
        # 爬取设置
        settings_layout = QHBoxLayout()
        
        page_layout = QHBoxLayout()
        page_label = QLabel("最大页数:")
        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 20)
        self.page_spin.setValue(5)
        page_layout.addWidget(page_label)
        page_layout.addWidget(self.page_spin)
        
        delay_layout = QHBoxLayout()
        delay_label = QLabel("请求延迟:")
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 5)
        self.delay_spin.setValue(2)
        self.delay_spin.setSuffix("秒")
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_spin)
        
        settings_layout.addLayout(page_layout)
        settings_layout.addLayout(delay_layout)
        account_layout.addLayout(settings_layout)
        
        account_search_btn = QPushButton("搜索公众号文章 ✧")
        account_search_btn.clicked.connect(lambda: self.start_crawl('account'))
        account_layout.addWidget(account_search_btn)
        
        # 小程序搜索标签
        mini_tab = QWidget()
        mini_layout = QVBoxLayout(mini_tab)
        
        mini_keyword_layout = QHBoxLayout()
        mini_keyword_label = QLabel("小程序关键词:")
        self.mini_keyword = QLineEdit()
        self.mini_keyword.setPlaceholderText("输入小程序名称")
        mini_keyword_layout.addWidget(mini_keyword_label)
        mini_keyword_layout.addWidget(self.mini_keyword)
        mini_layout.addLayout(mini_keyword_layout)
        
        mini_search_btn = QPushButton("搜索小程序 ✧")
        mini_search_btn.clicked.connect(lambda: self.start_crawl('miniprogram'))
        mini_layout.addWidget(mini_search_btn)
        
        search_tab.addTab(account_tab, "公众号搜索")
        search_tab.addTab(mini_tab, "小程序搜索")
        core_layout.addWidget(search_tab)

        # 状态与进度
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪 (◍•ᴗ•◍)ゝ")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        core_layout.addLayout(status_layout)

        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setAlternatingRowColors(True)
        core_layout.addWidget(self.result_table)

        # 操作按钮
        btn_layout = QHBoxLayout()
        
        export_btn = QPushButton("导出CSV ✧")
        export_btn.clicked.connect(self.export_to_csv)
        btn_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("清空结果 ✧")
        clear_btn.clicked.connect(self.clear_results)
        btn_layout.addWidget(clear_btn)
        
        stop_btn = QPushButton("停止任务 ✧")
        stop_btn.clicked.connect(self.stop_crawl)
        btn_layout.addWidget(stop_btn)
        
        about_btn = QPushButton("关于 ✧")
        about_btn.clicked.connect(self.show_about)
        btn_layout.addWidget(about_btn)
        
        core_layout.addLayout(btn_layout)
        
        # 2. 验证规则配置标签
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        
        # 配置说明
        desc_label = QLabel("✧ 验证规则配置（基于微信开放平台文档）✧")
        desc_label.setObjectName("subtitle")
        config_layout.addWidget(desc_label)
        
        config_frame = QFrame()
        config_form = QFormLayout(config_frame)
        
        # 核心字段配置
        self.core_fields_edit = QLineEdit()
        self.core_fields_edit.setText(self.validation_config.core_fields)
        config_form.addRow("核心用户字段 (必填):", self.core_fields_edit)
        
        # 会话字段配置
        self.session_fields_edit = QLineEdit()
        self.session_fields_edit.setText(self.validation_config.session_fields)
        config_form.addRow("会话字段 (至少一个):", self.session_fields_edit)
        
        # Token正则配置
        self.token_pattern_edit = QLineEdit()
        self.token_pattern_edit.setText(self.validation_config.token_pattern)
        config_form.addRow("Token提取正则:", self.token_pattern_edit)
        
        # 超时配置
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setValue(self.validation_config.api_timeout)
        self.timeout_spin.setSuffix("秒")
        config_form.addRow("API超时时间:", self.timeout_spin)
        
        config_layout.addWidget(config_frame)
        
        # 配置按钮
        config_btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存配置 ✧")
        save_btn.clicked.connect(self.save_config)
        reset_btn = QPushButton("重置默认 ✧")
        reset_btn.clicked.connect(self.reset_config)
        config_btn_layout.addWidget(save_btn)
        config_btn_layout.addWidget(reset_btn)
        config_layout.addLayout(config_btn_layout)
        
        # 配置说明
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setPlainText("""配置说明（参考微信开放平台API文档）:
1. 核心用户字段：用户身份标识字段，多个用逗号分隔
2. 会话字段：会话维持字段，至少需要存在一个
3. Token提取正则：从页面中提取Token的正则表达式
4. API超时时间：接口请求超时阈值

当微信API接口变更时，可通过修改以上配置适配新规则
""")
        config_layout.addWidget(help_text)
        
        # 添加标签页
        main_tab.addTab(core_tab, "核心功能")
        main_tab.addTab(config_tab, "验证规则配置")
        main_layout.addWidget(main_tab)

    def save_config(self):
        """保存验证规则配置"""
        try:
            self.validation_config.core_fields = self.core_fields_edit.text().strip()
            self.validation_config.session_fields = self.session_fields_edit.text().strip()
            self.validation_config.token_pattern = self.token_pattern_edit.text().strip()
            self.validation_config.api_timeout = self.timeout_spin.value()
            
            # 更新爬虫配置
            self.crawler = WeChatAPICrawler(self.validation_config)
            
            self.status_label.setText("验证规则配置已保存 ✧*｡٩(ˊᗜˋ*)و✧*｡")
            QMessageBox.information(self, "保存成功", "验证规则配置已更新！")
        except Exception as e:
            self.status_label.setText(f"配置保存失败: {str(e)}")
            QMessageBox.warning(self, "保存失败", f"配置保存出错:\n{str(e)}")

    def reset_config(self):
        """重置为默认配置"""
        self.validation_config.reset_to_default()
        self.core_fields_edit.setText(self.validation_config.core_fields)
        self.session_fields_edit.setText(self.validation_config.session_fields)
        self.token_pattern_edit.setText(self.validation_config.token_pattern)
        self.timeout_spin.setValue(self.validation_config.api_timeout)
        
        # 更新爬虫配置
        self.crawler = WeChatAPICrawler(self.validation_config)
        
        self.status_label.setText("验证规则已重置为默认值 (◍•ᴗ•◍)")

    def auto_get_cookie(self):
        """自动获取Cookie"""
        self.status_label.setText("正在尝试获取Cookie... 请稍候 (◍•ᴗ•◍)")
        self.auto_get_btn.setEnabled(False)
        
        try:
            source = self.source_combo.currentIndex()
            cookies = None
            
            if source == 0:  # 手动输入
                QMessageBox.information(self, "提示", "请手动输入Cookie")
                self.status_label.setText("已切换到手动输入模式 (◍•ᴗ•◍)")
                self.auto_get_btn.setEnabled(True)
                return
                
            elif source == 1:  # Chrome
                self.status_label.setText("正在从Chrome浏览器获取Cookie... (◍•ᴗ•◍)")
                cookies = WeChatCookieAutoGetter._get_from_chrome()
                
            elif source == 2:  # Edge
                self.status_label.setText("正在从Edge浏览器获取Cookie... (◍•ᴗ•◍)")
                cookies = WeChatCookieAutoGetter._get_from_edge()
                
            elif source == 3:  # 微信客户端
                self.status_label.setText("正在从微信客户端获取Cookie... (◍•ᴗ•◍)")
                cookies = WeChatCookieAutoGetter._get_from_wechat_app()
            
            # 通用获取方法作为备份
            if not cookies:
                self.status_label.setText("尝试通用方法获取Cookie... (◍•ᴗ•◍)")
                cookies = WeChatCookieAutoGetter.get_wechat_cookies()
            
            if cookies and WeChatCookieAutoGetter._validate_cookie_basic(cookies):
                self.cookie_input.setText(cookies)
                self.status_label.setText("Cookie获取成功！请点击验证按钮 (✧ω✧)")
                self.auth_status.setText("认证状态: 已获取Cookie，等待验证 (๑•̀ㅂ•́)و✧")
                self.auth_status.setObjectName("status-warning")
                
                # 尝试自动提取Token
                try:
                    cookie_dict = WeChatCookieAutoGetter._cookie_str_to_dict(cookies)
                    self.crawler.session.cookies.update(cookie_dict)
                    response = self.crawler._request_with_delay("https://mp.weixin.qq.com/cgi-bin/home")
                    token_match = re.search(self.validation_config.token_pattern, response.text)
                    if token_match:
                        self.token_input.setText(token_match.group(1))
                        self.status_label.setText("Cookie和Token获取成功！请点击验证按钮 (✧ω✧)")
                except:
                    pass
                    
            else:
                self.status_label.setText("Cookie获取失败 (╥_╥)")
                self.auth_status.setText("认证状态: Cookie获取失败，请手动输入 (╥_╥)")
                self.auth_status.setObjectName("status-error")
                QMessageBox.warning(
                    self, "获取失败", 
                    "无法获取有效的Cookie，请确保已登录微信网页版或客户端\n"
                    "建议参考微信开放平台文档手动配置Cookie"
                )
                
        except Exception as e:
            self.status_label.setText(f"Cookie获取出错: {str(e)}")
            self.auth_status.setText(f"认证状态: 获取Cookie时出错 (╥_╥)")
            self.auth_status.setObjectName("status-error")
            QMessageBox.critical(self, "错误", f"获取Cookie失败:\n{str(e)}")
            
        finally:
            self.auto_get_btn.setEnabled(True)

    def verify_auth(self):
        """验证登录态"""
        cookie_text = self.cookie_input.text().strip()
        if not cookie_text:
            QMessageBox.warning(self, "警告 (｡•́︿•̀｡)", "请输入或获取微信Cookie！")
            return
        
        token = self.token_input.text().strip() or None
        
        try:
            self.status_label.setText("正在验证登录态... (◍•ᴗ•◍)")
            valid, msg = self.crawler.set_cookies_and_token(cookie_text, token)
            
            if valid:
                self.auth_status.setText(f"认证状态: 验证通过 ✔️ {msg}")
                self.auth_status.setObjectName("status-success")
                self.status_label.setText("登录态验证成功，可以开始搜索啦 (✧ω✧)")
                if self.crawler.token and not token:
                    self.token_input.setText(self.crawler.token)
            else:
                self.auth_status.setText(f"认证状态: 验证失败 - {msg}")
                self.auth_status.setObjectName("status-error")
                self.status_label.setText("登录态验证失败，请检查配置后重试 (╥_╥)")
                
        except Exception as e:
            self.auth_status.setText(f"认证状态: 验证出错 - {str(e)}")
            self.auth_status.setObjectName("status-error")
            self.status_label.setText(f"验证出错: {str(e)}")

    def start_crawl(self, search_type):
        """开始爬取"""
        if not self.crawler.token or not self.crawler.cookies:
            QMessageBox.warning(self, "警告", "请先验证登录态！")
            return
        
        if search_type == 'account':
            keyword = self.account_keyword.text().strip()
            type_index = self.account_type_group.checkedId()
            type_map = {0: 'all', 1: 'official', 2: 'service', 3: 'subscription'}
            account_type = type_map[type_index]
        else:
            keyword = self.mini_keyword.text().strip()
            account_type = 'all'
        
        if not keyword:
            QMessageBox.warning(self, "警告", f"请输入{('公众号' if search_type == 'account' else '小程序')}关键词！")
            return
        
        self.crawler.request_delay = (self.delay_spin.value(), self.delay_spin.value() + 1)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"开始搜索{('公众号' if search_type == 'account' else '小程序')}... (◍•ᴗ•◍)")
        
        self.crawl_thread = APICrawlThread(
            self.crawler, 
            keyword, 
            self.page_spin.value(),
            search_type,
            account_type
        )
        self.crawl_thread.progress_updated.connect(self.progress_bar.setValue)
        self.crawl_thread.results_ready.connect(self.show_results)
        self.crawl_thread.error_occurred.connect(self.show_error)
        self.crawl_thread.status_updated.connect(self.status_label.setText)
        self.crawl_thread.start()

    def show_results(self, results, result_type):
        """显示爬取结果"""
        self.result_table.setRowCount(0)
        
        if result_type == 'account':
            self.result_table.setColumnCount(4)
            self.result_table.setHorizontalHeaderLabels(['文章标题', '文章链接', '小程序链接', '发布时间'])
            self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            
            for row_idx, item in enumerate(results):
                self.result_table.insertRow(row_idx)
                self.result_table.setItem(row_idx, 0, QTableWidgetItem(item['title']))
                self.result_table.setItem(row_idx, 1, QTableWidgetItem(item['link']))
                mini_links = '\n'.join(item['mini_links']) if item['mini_links'] else "无"
                self.result_table.setItem(row_idx, 2, QTableWidgetItem(mini_links))
                self.result_table.setItem(row_idx, 3, QTableWidgetItem(item['time']))
                
            self.status_label.setText(f"爬取完成！共找到 {len(results)} 篇文章 ✧*｡٩(ˊᗜˋ*)و✧*｡")
            QMessageBox.information(self, "完成", f"成功获取 {len(results)} 篇文章！")
            
        elif result_type == 'miniprogram':
            self.result_table.setColumnCount(4)
            self.result_table.setHorizontalHeaderLabels(['小程序名称', 'AppID', '描述', '访问链接'])
            self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            self.result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            
            for row_idx, item in enumerate(results):
                self.result_table.insertRow(row_idx)
                self.result_table.setItem(row_idx, 0, QTableWidgetItem(item['name']))
                self.result_table.setItem(row_idx, 1, QTableWidgetItem(item['appid']))
                self.result_table.setItem(row_idx, 2, QTableWidgetItem(item['desc']))
                self.result_table.setItem(row_idx, 3, QTableWidgetItem(item['link']))
                
            self.status_label.setText(f"爬取完成！共找到 {len(results)} 个小程序 ✧*｡٩(ˊᗜˋ*)و✧*｡")
            QMessageBox.information(self, "完成", f"成功获取 {len(results)} 个小程序信息！")
        
        self.progress_bar.setValue(100)

    def show_error(self, message):
        """显示错误信息"""
        self.status_label.setText(message)
        self.status_label.setObjectName("status-error")
        self.progress_bar.setVisible(False)
        QMessageBox.warning(self, "出错啦", message)

    def stop_crawl(self):
        """停止爬取"""
        if self.crawl_thread and self.crawl_thread.isRunning():
            self.crawl_thread.stop()
            self.status_label.setText("正在停止任务... (◍•ᴗ•◍)")

    def export_to_csv(self):
        """导出CSV"""
        if self.result_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "没有数据可导出！")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存CSV文件", 
            f"wechat_api_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
            "CSV文件 (*.csv)"
        )
        
        if not filename:
            return
            
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                headers = []
                for col in range(self.result_table.columnCount()):
                    headers.append(self.result_table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                for row in range(self.result_table.rowCount()):
                    row_data = []
                    for col in range(self.result_table.columnCount()):
                        item = self.result_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    
                    writer.writerow(row_data)
            
            self.status_label.setText(f"数据已成功导出到 {filename} ✧*｡٩(ˊᗜˋ*)و✧*｡")
            QMessageBox.information(self, "导出成功", f"数据已导出到:\n{filename}")
        except Exception as e:
            self.status_label.setText(f"导出失败: {str(e)}")
            QMessageBox.critical(self, "导出失败", f"导出CSV失败:\n{str(e)}")

    def clear_results(self):
        """清空结果"""
        self.result_table.setRowCount(0)
        self.status_label.setText("结果已清空 (✧ω✧)")

    def show_about(self):
        """显示关于信息"""
        about_text = """
        <h2>🌸 微信开放平台接口提取工具🌸</h2>
        <p><b>版本:</b> 6.0.0</p>
        <p><b>作者:</b> p1r07</p>
        <p><b>依托文档:</b> <a href="https://developers.weixin.qq.com/doc/oplatform/developers/dev/api/">
        微信开放平台开发者API文档</a></p>
        <p><b>核心功能:</b></p>
        <ul>
            <li>✧ 自定义验证字段配置（适配API变更）</li>
            <li>✧ 自动/手动双模式获取登录态</li>
            <li>✧ 服务号/订阅号/小程序全类型支持</li>
            <li>✧ 可视化字段验证规则配置</li>
            <li>✧ 数据导出与结果分析</li>
        </ul>
        <p><b>使用提示:</b> 当微信API接口变更时，可通过验证规则配置页适配新接口</p>
        <p style="color: #E64A8A;">✧*｡٩(ˊᗜˋ*)و✧*｡ 二次元风格工具 by p1r07</p>
        """
        QMessageBox.about(self, "关于工具", about_text)

    def closeEvent(self, event):
        """关闭窗口时停止线程"""
        if self.crawl_thread and self.crawl_thread.isRunning():
            self.crawl_thread.stop()
            self.crawl_thread.wait()
        event.accept()

# ====================== 主程序入口 ======================
def main():
    """主函数 (✧ω✧)"""
    try:
        import PyQt5
        import requests
        import bs4
    except ImportError as e:
        print(f"缺少依赖库: {e} (╥_╥)")
        print("正在尝试自动安装... (◍•ᴗ•◍)")
        try:
            import pip
            pip.main(['install', 'PyQt5', 'requests', 'beautifulsoup4', 'cryptography', 'pywin32'])
        except:
            print("自动安装失败，请手动运行:")
            print("pip install PyQt5 requests beautifulsoup4 cryptography pywin32")
            return
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))
    
    AnimeStyle.apply_style(app)
    
    window = WeChatAPIGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()