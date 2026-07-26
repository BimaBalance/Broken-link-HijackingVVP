#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BROKEN LINK HIJACK - v12.0 ULTIMATE FINAL
Dev: Bima Balance | Team: IJJ × Ikan Julung Julung
FIX: verified_links | Double HTTPS | Better Error Handling | Progress Bar
"""

import os
import sys
import re
import json
import csv
import time
import random
import argparse
import subprocess
import pickle
import threading
import signal
import logging
from datetime import datetime
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeout
from collections import defaultdict
from typing import List, Dict, Optional, Tuple, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from colorama import init, Fore, Style, Back

init(autoreset=True)

# Optional rich for better progress
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ====================== LOGGING ======================
logging.basicConfig(
    filename='blh_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BLH')

# ====================== BANNER ======================
BANNER = f"""
{Fore.CYAN}╔{'═'*80}╗
{Fore.CYAN}║{Fore.WHITE}  ██████  ██      ██   ██    ██  ██   ██ ██   ██ ██   ██  {Fore.CYAN}║
{Fore.CYAN}║{Fore.WHITE}  ██    ██ ██      ██   ██    ██  ██   ██ ██   ██ ██   ██  {Fore.CYAN}║
{Fore.CYAN}║{Fore.WHITE}  ██    ██ ██      ██   ██    ██  ███████ ███████ ███████  {Fore.CYAN}║
{Fore.CYAN}║{Fore.WHITE}  ██    ██ ██      ██   ██    ██  ██   ██ ██   ██ ██   ██  {Fore.CYAN}║
{Fore.CYAN}║{Fore.WHITE}   ██████  ███████ ██   ████████  ██   ██ ██   ██ ██   ██  {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}  BROKEN LINK HIJACK {Fore.RED}v12.0 {Fore.WHITE}- ULTIMATE FINAL  {Fore.CYAN}║
{Fore.CYAN}║{Fore.GREEN}  Dev: Bima Balance | Team: IJJ × Ikan Julung Julung {Fore.CYAN}║
{Fore.CYAN}║{Fore.MAGENTA}  FIX ALL | PROGRESS BAR | MULTI-THREAD | HTML+CSV+JSON  {Fore.CYAN}║
{Fore.CYAN}╚{'═'*80}╝{Style.RESET_ALL}
"""

# ====================== SOCIAL PLATFORMS ======================
SOCIAL_PLATFORMS = {
    'facebook.com': {'valid': ['facebook.com/', 'fb.com/'], 'invalid': ['content not found', 'this content isn\'t available'], 'severity': 'HIGH'},
    'instagram.com': {'valid': ['instagram.com/p/', 'instagram.com/reel/'], 'invalid': ['page not found', 'sorry, this page isn\'t available'], 'severity': 'HIGH'},
    'twitter.com': {'valid': ['twitter.com/', 'x.com/'], 'invalid': ['this account doesn\'t exist', 'account suspended'], 'severity': 'HIGH'},
    'x.com': {'valid': ['x.com/'], 'invalid': ['this account doesn\'t exist', 'account suspended'], 'severity': 'HIGH'},
    'youtube.com': {'valid': ['youtube.com/@', 'youtube.com/channel/'], 'invalid': ['this channel doesn\'t exist', '404 not found'], 'severity': 'MEDIUM'},
    'linkedin.com': {'valid': ['linkedin.com/in/', 'linkedin.com/company/'], 'invalid': ['page not found', 'this profile is unavailable'], 'severity': 'HIGH'},
    't.me': {'valid': ['t.me/'], 'invalid': ['sorry, this username doesn\'t exist', 'username not found'], 'severity': 'HIGH'},
    'telegram.org': {'valid': ['telegram.org/'], 'invalid': ['sorry, this username doesn\'t exist'], 'severity': 'HIGH'},
    'discord.com': {'valid': ['discord.com/'], 'invalid': ['this user has no avatar', 'user not found'], 'severity': 'HIGH'},
    'twitch.tv': {'valid': ['twitch.tv/'], 'invalid': ['sorry, unless you\'ve got a time machine', 'we couldn\'t find this page'], 'severity': 'MEDIUM'},
    'reddit.com': {'valid': ['reddit.com/u/', 'reddit.com/r/'], 'invalid': ['there doesn\'t seem to be anything here', 'page not found'], 'severity': 'MEDIUM'},
    'github.com': {'valid': ['github.com/'], 'invalid': ['404 — file not found', 'there isn\'t a github pages site here'], 'severity': 'HIGH'},
    'gitlab.com': {'valid': ['gitlab.com/'], 'invalid': ['page not found', 'the page you\'re looking for could not be found'], 'severity': 'HIGH'},
    'bitbucket.org': {'valid': ['bitbucket.org/'], 'invalid': ['404', 'page not found', 'not found'], 'severity': 'HIGH'},
    'tiktok.com': {'valid': ['tiktok.com/@'], 'invalid': ['couldn\'t find this account', 'user not found'], 'severity': 'MEDIUM'},
    'pinterest.com': {'valid': ['pinterest.com/'], 'invalid': ['page not found', 'sorry, we couldn\'t find that page'], 'severity': 'LOW'},
    'patreon.com': {'valid': ['patreon.com/'], 'invalid': ['404', 'page not found', 'could not find'], 'severity': 'MEDIUM'},
    'tumblr.com': {'valid': ['tumblr.com/'], 'invalid': ['404', 'page not found', 'not found'], 'severity': 'LOW'},
    'snapchat.com': {'valid': ['snapchat.com/add/'], 'invalid': ['404', 'not found', 'could not find'], 'severity': 'MEDIUM'},
    'medium.com': {'valid': ['medium.com/@'], 'invalid': ['404 - page not found', 'out of nothing, something'], 'severity': 'LOW'},
    'deviantart.com': {'valid': ['deviantart.com/'], 'invalid': ['404', 'page not found', 'not found'], 'severity': 'LOW'},
    'behance.net': {'valid': ['behance.net/'], 'invalid': ['404', 'page not found', 'not found'], 'severity': 'LOW'},
    'dribbble.com': {'valid': ['dribbble.com/'], 'invalid': ['404', 'page not found', 'shot not found'], 'severity': 'LOW'},
    'vimeo.com': {'valid': ['vimeo.com/'], 'invalid': ['404', 'page not found', 'the page you were looking for'], 'severity': 'LOW'},
    'spotify.com': {'valid': ['open.spotify.com/', 'spotify.com/'], 'invalid': ['404', 'page not found', 'not found'], 'severity': 'LOW'},
    'soundcloud.com': {'valid': ['soundcloud.com/'], 'invalid': ['404', 'page not found', 'we couldn\'t find'], 'severity': 'LOW'},
    'imgur.com': {'valid': ['imgur.com/'], 'invalid': ['404', 'page not found', 'not found'], 'severity': 'LOW'},
    'flickr.com': {'valid': ['flickr.com/people/', 'flickr.com/photos/'], 'invalid': ['404', 'page not found', 'not found'], 'severity': 'LOW'},
}

DEFAULT_PLATFORM = {'valid': [], 'invalid': ['404','not found','error','unavailable','does not exist','suspended','deactivated'], 'severity': 'MEDIUM'}

# ====================== UTILITY ======================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 Version/17.6 Mobile/15E148 Safari/604.1",
]

def debug_print(msg: str, debug: bool = False, color: str = Fore.CYAN):
    if debug:
        print(f"{color}[DEBUG] {msg}{Style.RESET_ALL}")

def color_severity(severity: str) -> str:
    colors = {
        'CRITICAL': f"{Fore.RED}🔥 CRITICAL{Style.RESET_ALL}",
        'HIGH': f"{Fore.YELLOW}⚠️ HIGH{Style.RESET_ALL}",
        'MEDIUM': f"{Fore.MAGENTA}📌 MEDIUM{Style.RESET_ALL}",
        'LOW': f"{Fore.CYAN}ℹ️ LOW{Style.RESET_ALL}",
        'INFO': f"{Fore.GREEN}📋 INFO{Style.RESET_ALL}",
    }
    return colors.get(severity.upper(), severity)

def print_table(headers: List[str], rows: List[List[str]], title: str = None):
    if not rows: return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                clean = re.sub(r'\x1b\[[0-9;]*m', '', str(cell))
                col_widths[i] = max(col_widths[i], len(clean) + 2)
    border = '┌' + '┬'.join(['─' * w for w in col_widths]) + '┐'
    print(f"{Fore.CYAN}{border}{Style.RESET_ALL}")
    header_row = '│' + '│'.join([f" {h.center(w-2)} " for h, w in zip(headers, col_widths)]) + '│'
    print(f"{Fore.WHITE}{Back.BLUE}{header_row}{Style.RESET_ALL}")
    sep = '├' + '┼'.join(['─' * w for w in col_widths]) + '┤'
    print(f"{Fore.CYAN}{sep}{Style.RESET_ALL}")
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cells.append(f" {cell:<{col_widths[i]-2}} ")
        print('│' + '│'.join(cells) + '│')
    bottom = '└' + '┴'.join(['─' * w for w in col_widths]) + '┘'
    print(f"{Fore.CYAN}{bottom}{Style.RESET_ALL}")

# ====================== MAIN SCANNER ======================
class BLHScannerUltimate:
    def __init__(self, targets: List[str], output: str = None, delay: float = 0.3,
                 retries: int = 3, threads: int = 20, deep_crawl: bool = True,
                 depth: int = 3, no_verify: bool = False, httpx: bool = True,
                 nuclei: bool = False, wayback: bool = True, resume: bool = True,
                 timeout: int = 10, rate_delay: float = 0.5, live_report: bool = True,
                 debug: bool = False):
        
        self.targets = targets
        self.output = output
        self.delay = delay
        self.retries = retries
        self.threads = threads
        self.deep_crawl = deep_crawl
        self.depth = depth
        self.no_verify = no_verify
        self.use_httpx = httpx
        self.use_nuclei = nuclei
        self.use_wayback = wayback
        self.resume = resume
        self.timeout = timeout
        self.rate_delay = rate_delay
        self.live_report = live_report
        self.debug = debug
        
        self.session = self._create_session()
        self.all_results = []
        self.all_links = set()
        self.visited = set()
        self.resume_file = "blh_resume.pkl"
        self.lock = threading.Lock()
        self.stats = {
            'total_domains': len(targets),
            'total_subdomains': 0,
            'scanned': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0,
            'start_time': datetime.now(),
            'errors': 0,
            'timeouts': 0,
            'verified_links': 0,
        }
        self._running = True
        signal.signal(signal.SIGINT, self._signal_handler)
        
        if resume and os.path.exists(self.resume_file):
            self._load_resume()
        
        if self.live_report and self.output:
            self._init_live_report()

    def _signal_handler(self, sig, frame):
        print(f"\n{Fore.YELLOW}[!] Interrupted. Saving progress...{Style.RESET_ALL}")
        self._running = False
        self._save_resume()
        sys.exit(0)

    def _create_session(self) -> requests.Session:
        sess = requests.Session()
        retry_strategy = Retry(
            total=self.retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        sess.mount("http://", adapter)
        sess.mount("https://", adapter)
        sess.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        return sess

    def _req(self, url: str, method: str = 'GET') -> Optional[requests.Response]:
        # Fix double https
        if url.startswith('https://https://'):
            url = url.replace('https://https://', 'https://')
        elif url.startswith('http://http://'):
            url = url.replace('http://http://', 'http://')
        if not url.startswith('http'):
            url = f'https://{url}'
            
        debug_print(f"Request: {method} {url}", self.debug, Fore.CYAN)
        for attempt in range(self.retries + 1):
            try:
                self.session.headers['User-Agent'] = random.choice(USER_AGENTS)
                if method == 'HEAD':
                    r = self.session.head(url, timeout=self.timeout, allow_redirects=True)
                    if r.status_code == 405:
                        return self._req(url, 'GET')
                    if r.status_code == 429:
                        wait = min(2 ** attempt, 30)
                        debug_print(f"Rate limit hit, waiting {wait}s", self.debug, Fore.YELLOW)
                        time.sleep(wait)
                        continue
                    return r
                r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                if r.status_code == 429:
                    wait = min(2 ** attempt, 30)
                    debug_print(f"Rate limit hit, waiting {wait}s", self.debug, Fore.YELLOW)
                    time.sleep(wait)
                    continue
                if r.status_code in [500, 502, 503, 504]:
                    debug_print(f"Server error {r.status_code}, retrying...", self.debug, Fore.YELLOW)
                    time.sleep(min(2 ** attempt, 10))
                    continue
                debug_print(f"Response: {r.status_code} from {url}", self.debug, Fore.GREEN)
                return r
            except requests.exceptions.Timeout:
                with self.lock:
                    self.stats['timeouts'] += 1
                logger.error(f"Timeout on {url} (attempt {attempt+1})")
                debug_print(f"Timeout on {url}", self.debug, Fore.RED)
                if attempt < self.retries:
                    time.sleep(self.rate_delay * (attempt + 1))
                    continue
                return None
            except Exception as e:
                logger.error(f"Error on {url}: {e}")
                debug_print(f"Error: {e} on {url}", self.debug, Fore.RED)
                if attempt < self.retries:
                    time.sleep(self.rate_delay * (attempt + 1))
                    continue
                return None
        return None

    def _clean_domain(self, domain: str) -> str:
        """Hilangkan protokol dari domain."""
        domain = domain.split('://')[-1].rstrip('/')
        return domain

    def _is_social(self, url: str) -> bool:
        try:
            netloc = urlparse(url).netloc.lower().replace('www.', '')
            return any(p in netloc for p in SOCIAL_PLATFORMS.keys())
        except:
            return False

    def _extract_social(self, html: str, base_url: str) -> List[str]:
        links = set()
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=True):
                if self._is_social(a['href']):
                    links.add(a['href'])
            pattern = re.compile(r'https?://(?:www\.)?(?:' + '|'.join(re.escape(p) for p in SOCIAL_PLATFORMS.keys()) + r')[^\s"\'<>)}$$]+', re.I)
            for match in pattern.findall(html):
                links.add(match.rstrip('.,;)'))
            final = set()
            for link in links:
                if link.startswith('/'): link = urljoin(base_url, link)
                clean = link.split('?')[0].split('#')[0].rstrip('/')
                if self._is_social(clean):
                    final.add(clean)
            debug_print(f"Extracted {len(final)} social links from {base_url}", self.debug, Fore.GREEN)
            return list(final)
        except Exception as e:
            logger.error(f"Error extracting social links from {base_url}: {e}")
            return []

    def _verify_link(self, url: str) -> Tuple[bool, str, str, str, int]:
        try:
            head_resp = self._req(url, 'HEAD')
            if head_resp and head_resp.status_code == 404:
                return (False, 'HTTP 404 Not Found', 'deleted', 'CRITICAL', 95)
            handler, platform = self._get_platform(url)
            resp = self._req(url, 'GET')
            if not resp:
                return (False, 'Connection Failed', 'unknown', 'MEDIUM', 50)
            body = resp.text.lower()
            for indicator in handler.get('invalid', []):
                if indicator.lower() in body:
                    severity = handler.get('severity', 'MEDIUM').upper()
                    return (False, f'{platform}: {indicator}', 'deleted', severity, 90)
            if any(indicator.lower() in url.lower() for indicator in handler.get('valid', [])):
                return (True, f'{platform}: Active', 'active', 'INFO', 90)
            return (False, f'{platform}: Inactive/Deleted', 'deleted', 'HIGH', 80)
        except Exception as e:
            logger.error(f"Error verifying {url}: {e}")
            return (False, f'Error: {str(e)[:30]}', 'unknown', 'MEDIUM', 40)

    def _get_platform(self, url: str) -> Tuple[Dict, str]:
        try:
            netloc = urlparse(url).netloc.lower().replace('www.', '')
            for platform, handler in SOCIAL_PLATFORMS.items():
                if platform in netloc:
                    return handler, platform
        except:
            pass
        return DEFAULT_PLATFORM, 'unknown'

    def _filter_alive(self, subdomains: List[str]) -> List[str]:
        if not self.use_httpx or not subdomains:
            return subdomains
        debug_print(f"Filtering {len(subdomains)} subdomains with httpx...", self.debug, Fore.CYAN)
        print(f"{Fore.YELLOW}[*] Filtering alive subdomains with httpx...{Style.RESET_ALL}")
        try:
            cmd = ['httpx', '-mc', '200,403,401', '-silent', '-timeout', str(self.timeout)]
            result = subprocess.run(cmd, input='\n'.join(subdomains), capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                alive = [l.strip() for l in result.stdout.splitlines() if l.strip()]
                debug_print(f"httpx found {len(alive)} alive subdomains", self.debug, Fore.GREEN)
                print(f"{Fore.GREEN}✓ {len(alive)} alive subdomains{Style.RESET_ALL}")
                # Clean domains
                alive = [self._clean_domain(a) for a in alive]
                return alive
        except Exception as e:
            logger.error(f"httpx failed: {e}")
            debug_print(f"httpx failed: {e}", self.debug, Fore.RED)
            print(f"{Fore.RED}✗ httpx failed: {e}{Style.RESET_ALL}")
        return [self._clean_domain(s) for s in subdomains]

    def _get_wayback_links(self, domain: str) -> List[str]:
        if not self.use_wayback:
            return []
        debug_print(f"Getting Wayback links for {domain}", self.debug, Fore.CYAN)
        try:
            cmd = ['waybackurls', domain]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                links = [l.strip() for l in result.stdout.splitlines() if l.strip() and self._is_social(l)]
                debug_print(f"Wayback found {len(links)} social links", self.debug, Fore.GREEN)
                return links
        except Exception as e:
            logger.error(f"waybackurls failed for {domain}: {e}")
        return []

    def _enum_subfinder(self, domain: str) -> List[str]:
        debug_print(f"Enumerating subdomains for {domain}", self.debug, Fore.CYAN)
        try:
            result = subprocess.run(['subfinder', '-d', domain, '-silent', '-timeout', str(self.timeout)], capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                subs = [l.strip() for l in result.stdout.splitlines() if l.strip()]
                debug_print(f"subfinder found {len(subs)} subdomains", self.debug, Fore.GREEN)
                return subs
        except Exception as e:
            logger.error(f"subfinder failed for {domain}: {e}")
            debug_print(f"subfinder failed: {e}", self.debug, Fore.RED)
        return [domain]

    def _crawl(self, url: str, depth: int) -> List[str]:
        if depth > self.depth or url in self.visited:
            return []
        self.visited.add(url)
        debug_print(f"Crawling {url} (depth {depth})", self.debug, Fore.CYAN)
        try:
            resp = self._req(url)
            if not resp or resp.status_code != 200:
                debug_print(f"Crawl failed: {resp.status_code if resp else 'No response'}", self.debug, Fore.RED)
                return []
            social = self._extract_social(resp.text, url)
            if depth < self.depth:
                soup = BeautifulSoup(resp.text, 'html.parser')
                internal = set()
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('/') or any(d in href for d in self.targets):
                        full = urljoin(url, href)
                        if any(d in full for d in self.targets) and full not in self.visited:
                            internal.add(full)
                children = []
                debug_print(f"Found {len(internal)} internal links", self.debug, Fore.CYAN)
                for link in list(internal)[:20]:
                    try:
                        children.extend(self._crawl(link, depth + 1))
                    except Exception as e:
                        logger.error(f"Error crawling {link}: {e}")
                social.extend(children)
            return social
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return []

    def _process_domain(self, domain: str) -> List[Dict]:
        results = []
        domain = self._clean_domain(domain)
        debug_print(f"Processing domain: {domain}", self.debug, Fore.MAGENTA)
        print(f"\n{Fore.CYAN}[*] Processing {domain}{Style.RESET_ALL}")
        
        # 1. Subdomain enumeration
        subs = self._enum_subfinder(domain)
        self.stats['total_subdomains'] += len(subs)
        
        # 2. Filter alive (clean domains inside)
        alive = self._filter_alive(subs) if self.use_httpx else [self._clean_domain(s) for s in subs]
        if not alive:
            alive = [domain]
        
        # 3. Wayback links
        wayback_links = []
        if self.use_wayback:
            wayback_links = self._get_wayback_links(domain)
        for link in wayback_links:
            if self._is_social(link):
                results.append({
                    'domain': domain,
                    'source': 'wayback',
                    'url': link,
                    'platform': urlparse(link).netloc.replace('www.', ''),
                    'vulnerable': True,
                    'severity': 'HIGH',
                    'confidence': 85,
                    'status': 'Historical link - requires verification',
                    'timestamp': datetime.now().isoformat()
                })
        
        # 4. Crawl each alive subdomain
        found = set()
        for sub in alive:
            sub = self._clean_domain(sub)
            debug_print(f"Crawling subdomain: {sub}", self.debug, Fore.CYAN)
            paths = ['/', '/about', '/contact', '/footer', '/home', '/sitemap', '/robots.txt']
            if self.deep_crawl:
                paths = ['/']
            for path in paths:
                try:
                    full_url = f"https://{sub}{path}"
                    resp = self._req(full_url)
                    if not resp or resp.status_code != 200:
                        continue
                    social_urls = []
                    if self.deep_crawl and path == '/':
                        social_urls = self._crawl(full_url, 0)
                    else:
                        social_urls = self._extract_social(resp.text, full_url)
                    for link in social_urls:
                        if link in found:
                            continue
                        found.add(link)
                        
                        debug_print(f"Verifying social link: {link}", self.debug, Fore.CYAN)
                        
                        if not self.no_verify:
                            vulnerable, status, state, severity, confidence = self._verify_link(link)
                        else:
                            vulnerable, status, state, severity, confidence = False, 'Skipped', 'unknown', 'INFO', 50
                        
                        if vulnerable:
                            if confidence >= 90:
                                severity = 'CRITICAL'
                            elif confidence >= 75:
                                severity = 'HIGH'
                            else:
                                severity = 'MEDIUM'
                        else:
                            severity = 'INFO'
                        
                        self.stats['verified_links'] += 1
                        
                        results.append({
                            'domain': domain,
                            'subdomain': sub,
                            'source_url': full_url,
                            'url': link,
                            'platform': urlparse(link).netloc.replace('www.', ''),
                            'vulnerable': vulnerable,
                            'severity': severity,
                            'confidence': confidence,
                            'status': status,
                            'state': state,
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception as e:
                    logger.error(f"Error processing {sub}{path}: {e}")
                    debug_print(f"Error: {e}", self.debug, Fore.RED)
                if found:
                    break
        
        # Update stats
        for r in results:
            if r.get('vulnerable'):
                sev = r.get('severity', 'INFO')
                if sev == 'CRITICAL': self.stats['critical'] += 1
                elif sev == 'HIGH': self.stats['high'] += 1
                elif sev == 'MEDIUM': self.stats['medium'] += 1
                elif sev == 'LOW': self.stats['low'] += 1
                else: self.stats['info'] += 1
        
        self.stats['scanned'] += 1
        self._save_resume()
        self._update_live_report(results)
        debug_print(f"Domain {domain} processed: {len(results)} results", self.debug, Fore.GREEN)
        return results

    def _init_live_report(self):
        if not self.output:
            return
        try:
            with open(self.output + '.live', 'w') as f:
                f.write(f"BLH v12.0 Live Report - {datetime.now().isoformat()}\n")
                f.write("="*60 + "\n\n")
        except Exception as e:
            logger.error(f"Could not create live report: {e}")

    def _update_live_report(self, new_results: List[Dict]):
        if not self.live_report or not self.output:
            return
        try:
            with open(self.output + '.live', 'a') as f:
                for r in new_results:
                    if r.get('vulnerable'):
                        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {r.get('severity','INFO')} | {r.get('url')} | {r.get('status','')}\n")
        except Exception as e:
            logger.error(f"Live report update failed: {e}")

    def _save_resume(self):
        if not self.resume:
            return
        try:
            data = {
                'targets': self.targets,
                'results': self.all_results,
                'visited': list(self.visited),
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.resume_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error(f"Resume save failed: {e}")

    def _load_resume(self):
        try:
            with open(self.resume_file, 'rb') as f:
                data = pickle.load(f)
                if data.get('targets') == self.targets:
                    self.all_results = data.get('results', [])
                    self.visited = set(data.get('visited', []))
                    self.stats = data.get('stats', self.stats)
                    print(f"{Fore.CYAN}[*] Resume loaded: {len(self.all_results)} results{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Resume load failed: {e}")
            self.all_results = []

    def run(self):
        print(f"\n{Fore.YELLOW}[*] Scanning {len(self.targets)} domains...{Style.RESET_ALL}")
        all_results = []
        with ThreadPoolExecutor(max_workers=min(self.threads, len(self.targets))) as executor:
            futures = {executor.submit(self._process_domain, d): d for d in self.targets}
            for future in as_completed(futures):
                domain = futures[future]
                try:
                    result = future.result(timeout=300)
                    if result:
                        all_results.extend(result)
                        self.all_results.extend(result)
                        print(f"{Fore.GREEN}✓ {domain} -> {len(result)} links{Style.RESET_ALL}")
                except FuturesTimeout:
                    logger.error(f"Timeout processing {domain}")
                    print(f"{Fore.RED}✗ {domain} -> TIMEOUT (skipped){Style.RESET_ALL}")
                except Exception as e:
                    logger.error(f"Error processing {domain}: {e}")
                    print(f"{Fore.RED}✗ {domain} -> ERROR: {str(e)[:50]}{Style.RESET_ALL}")
        self.all_results = all_results
        return self.all_results

    def display(self):
        duration = (datetime.now() - self.stats['start_time']).total_seconds()
        print(f"\n{Fore.CYAN}╔{'═'*80}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.WHITE}{' SCAN COMPLETE ':^78}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═'*80}╝{Style.RESET_ALL}")
        
        stats_data = [
            ['Domains', str(self.stats['total_domains'])],
            ['Subdomains Found', str(self.stats['total_subdomains'])],
            ['Scanned', str(self.stats['scanned'])],
            ['Verified Links', str(self.stats.get('verified_links', 0))],
            ['Total Links Found', str(len(self.all_results))],
            ['Duration', f"{duration:.1f}s"],
            ['🔥 CRITICAL', str(self.stats['critical'])],
            ['⚠️ HIGH', str(self.stats['high'])],
            ['📌 MEDIUM', str(self.stats['medium'])],
            ['ℹ️ LOW', str(self.stats['low'])],
            ['📋 INFO', str(self.stats['info'])],
            ['⏱️ Timeouts', str(self.stats['timeouts'])],
            ['❌ Errors', str(self.stats['errors'])],
        ]
        print_table(['Metric', 'Value'], stats_data)
        
        if not self.all_results:
            print(f"\n{Fore.GREEN}✅ No vulnerable links found!{Style.RESET_ALL}")
            return
        
        vuln = [r for r in self.all_results if r.get('vulnerable')]
        if not vuln:
            print(f"\n{Fore.GREEN}✅ No vulnerable links.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.WHITE}📋 DETAILED RESULTS (VULNERABLE ONLY){Style.RESET_ALL}")
        table_data = []
        for r in vuln[:30]:
            sev = color_severity(r.get('severity', 'INFO'))
            platform = r.get('platform', 'Unknown')[:20]
            url_short = r['url'][:50] + ('...' if len(r['url']) > 50 else '')
            table_data.append([sev, platform, r.get('subdomain', r.get('domain', ''))[:25], url_short])
        print_table(['Severity', 'Platform', 'Source', 'URL'], table_data)
        if len(vuln) > 30:
            print(f"\n{Fore.YELLOW}... and {len(vuln)-30} more vulnerable links.{Style.RESET_ALL}")

    def export(self):
        if not self.output:
            return
        stats_copy = self.stats.copy()
        if 'start_time' in stats_copy:
            stats_copy['start_time'] = stats_copy['start_time'].isoformat()
        data = {
            'domain': self.targets,
            'timestamp': datetime.now().isoformat(),
            'stats': stats_copy,
            'results': self.all_results
        }
        try:
            with open(self.output, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n{Fore.GREEN}✅ JSON results saved to {self.output}{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Export JSON failed: {e}")
            print(f"{Fore.RED}❌ Failed to save JSON: {e}{Style.RESET_ALL}")
        
        try:
            html_file = self.output.replace('.json', '.html') if self.output.endswith('.json') else self.output + '.html'
            self._export_html(html_file)
        except Exception as e:
            logger.error(f"HTML export failed: {e}")
        
        try:
            csv_file = self.output.replace('.json', '.csv') if self.output.endswith('.json') else self.output + '.csv'
            self._export_csv(csv_file)
        except Exception as e:
            logger.error(f"CSV export failed: {e}")

    def _export_html(self, filename: str):
        vuln = [r for r in self.all_results if r.get('vulnerable')]
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>BLH Report - {', '.join(self.targets)}</title>
<style>
body {{font-family: 'Segoe UI', Arial; background:#0a0e17; color:#c8d6e5; padding:20px;}}
.container {{max-width:1200px; margin:0 auto;}}
h1 {{color:#00d2ff; border-bottom:2px solid #00d2ff; padding-bottom:10px;}}
.stats {{display:grid; grid-template-columns:repeat(auto-fit, minmax(150px,1fr)); gap:15px; margin:20px 0;}}
.stat-box {{background:#131d2e; padding:15px; border-radius:8px; text-align:center;}}
.stat-box .num {{font-size:28px; font-weight:bold;}}
.stat-box .label {{color:#8395a7; font-size:12px; text-transform:uppercase;}}
.critical .num {{color:#ff6b6b;}}
.high .num {{color:#feca57;}}
.medium .num {{color:#a29bfe;}}
.low .num {{color:#54a0ff;}}
.info .num {{color:#1dd1a1;}}
table {{width:100%; border-collapse:collapse; margin-top:20px;}}
th {{background:#1a2a3a; color:#00d2ff; padding:12px; text-align:left;}}
td {{padding:10px; border-bottom:1px solid #1a2a3a;}}
.severity-CRITICAL {{color:#ff6b6b; font-weight:bold;}}
.severity-HIGH {{color:#feca57; font-weight:bold;}}
.severity-MEDIUM {{color:#a29bfe;}}
.severity-LOW {{color:#54a0ff;}}
.severity-INFO {{color:#1dd1a1;}}
.footer {{margin-top:30px; text-align:center; color:#8395a7; font-size:12px;}}
</style>
</head>
<body>
<div class="container">
<h1>🔍 Broken Link Hijack Report</h1>
<p><strong>Targets:</strong> {', '.join(self.targets)}</p>
<p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<div class="stats">
    <div class="stat-box"><div class="num">{self.stats['total_domains']}</div><div class="label">Domains</div></div>
    <div class="stat-box"><div class="num">{self.stats['total_subdomains']}</div><div class="label">Subdomains</div></div>
    <div class="stat-box"><div class="num">{len(self.all_results)}</div><div class="label">Total Links</div></div>
    <div class="stat-box critical"><div class="num">{self.stats['critical']}</div><div class="label">CRITICAL</div></div>
    <div class="stat-box high"><div class="num">{self.stats['high']}</div><div class="label">HIGH</div></div>
    <div class="stat-box medium"><div class="num">{self.stats['medium']}</div><div class="label">MEDIUM</div></div>
    <div class="stat-box"><div class="num">{self.stats.get('verified_links', 0)}</div><div class="label">Verified</div></div>
</div>
<h2>📋 Vulnerable Links</h2>
<table>
<tr><th>Severity</th><th>Confidence</th><th>Domain</th><th>URL</th><th>Platform</th><th>Status</th></tr>
"""
        for r in vuln[:100]:
            sev = r.get('severity', 'INFO')
            conf = r.get('confidence', 0)
            html += f"""
        <tr>
            <td class="severity-{sev}">{sev}</td>
            <td>{conf}%</td>
            <td>{r.get('domain', r.get('subdomain', 'N/A'))}</td>
            <td><a href="{r['url']}" target="_blank" style="color:#00d2ff;">{r['url'][:60]}...</a></td>
            <td>{r.get('platform', 'N/A')}</td>
            <td>{r.get('status', 'N/A')}</td>
        </tr>
"""
        html += f"""
</table>
<div class="footer">Generated by BLH v12.0 | Dev: Bima Balance | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
</body>
</html>
"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"{Fore.GREEN}✅ HTML report saved to {filename}{Style.RESET_ALL}")

    def _export_csv(self, filename: str):
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Domain', 'Subdomain', 'URL', 'Platform', 'Vulnerable', 'Severity', 'Confidence', 'Status', 'Timestamp'])
            for r in self.all_results:
                writer.writerow([
                    r.get('domain', ''),
                    r.get('subdomain', ''),
                    r.get('url', ''),
                    r.get('platform', ''),
                    r.get('vulnerable', False),
                    r.get('severity', ''),
                    r.get('confidence', 0),
                    r.get('status', ''),
                    r.get('timestamp', '')
                ])
        print(f"{Fore.GREEN}✅ CSV report saved to {filename}{Style.RESET_ALL}")

# ====================== MAIN ======================
def main():
    parser = argparse.ArgumentParser(description='BLH v12.0 - Ultimate Final')
    parser.add_argument('-d', '--domain', help='Single target domain')
    parser.add_argument('-l', '--list', help='File with list of domains (one per line)')
    parser.add_argument('-o', '--output', default='blh_results.json', help='Output file (JSON + HTML + CSV)')
    parser.add_argument('--delay', type=float, default=0.3, help='Request delay between attempts')
    parser.add_argument('--retries', type=int, default=3, help='Max retries per request')
    parser.add_argument('--threads', type=int, default=20, help='Thread count')
    parser.add_argument('--depth', type=int, default=3, help='Crawl depth')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    parser.add_argument('--rate-delay', type=float, default=0.5, help='Delay between requests (rate limiting)')
    parser.add_argument('--no-httpx', action='store_true', help='Disable httpx filter')
    parser.add_argument('--nuclei', action='store_true', help='Enable Nuclei scan')
    parser.add_argument('--no-wayback', action='store_true', help='Disable Wayback')
    parser.add_argument('--no-deep', action='store_true', help='Disable deep crawl')
    parser.add_argument('--no-verify', action='store_true', help='Skip verification')
    parser.add_argument('--no-resume', action='store_true', help='Disable resume')
    parser.add_argument('--no-live', action='store_true', help='Disable live report')
    parser.add_argument('--debug', action='store_true', help='Enable debug/verbose mode')
    args = parser.parse_args()

    targets = []
    if args.domain:
        targets = [args.domain]
    elif args.list:
        try:
            with open(args.list, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"{Fore.RED}Error reading list file: {e}{Style.RESET_ALL}")
            sys.exit(1)
    else:
        print(f"{Fore.RED}Error: Need -d or -l{Style.RESET_ALL}")
        sys.exit(1)

    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"{Fore.WHITE}Targets: {len(targets)} domains")
    print(f"{Fore.WHITE}Threads: {args.threads}")
    print(f"{Fore.WHITE}Timeout: {args.timeout}s")
    print(f"{Fore.WHITE}Retries: {args.retries}")
    print(f"{Fore.WHITE}Deep Crawl: {not args.no_deep}")
    print(f"{Fore.WHITE}HTTPX: {not args.no_httpx}")
    print(f"{Fore.WHITE}Nuclei: {args.nuclei}")
    print(f"{Fore.WHITE}Wayback: {not args.no_wayback}")
    print(f"{Fore.WHITE}Debug: {args.debug}")
    print(f"{Fore.WHITE}{'='*80}{Style.RESET_ALL}")

    scanner = BLHScannerUltimate(
        targets=targets,
        output=args.output,
        delay=args.delay,
        retries=args.retries,
        threads=args.threads,
        depth=args.depth,
        deep_crawl=not args.no_deep,
        httpx=not args.no_httpx,
        nuclei=args.nuclei,
        wayback=not args.no_wayback,
        no_verify=args.no_verify,
        resume=not args.no_resume,
        timeout=args.timeout,
        rate_delay=args.rate_delay,
        live_report=not args.no_live,
        debug=args.debug
    )

    try:
        scanner.run()
        scanner.display()
        scanner.export()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Scan interrupted by user.{Style.RESET_ALL}")
        scanner._save_resume()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)

    print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Scan complete!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️ Use only for authorized testing!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")

if __name__ == '__main__':
    main()
