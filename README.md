![Broken Link Hijacking](file_00000000afa88207a81699fd08fad7e6.png)

# 🔍 Broken Link Hijack v12.0

**Broken Link Hijack (BLH) adalah tools otomatis untuk mendeteksi broken social media links dan potensi hijacking pada domain target.**  
Dirancang khusus untuk **bug bounty**, **pentesting**, dan **security research**.

---

## ✨ Fitur Unggulan

| Fitur | Keterangan |
|-------|------------|
| **Multi-Domain Scan** | Scan beberapa domain sekaligus dari file (`-l targets.txt`) |
| **Subdomain Enumeration** | Otomatis pakai `subfinder` untuk menemukan semua subdomain |
| **HTTPX Integration** | Filter subdomain hidup (status 200/403/401) biar cepat |
| **Deep Crawl** | Crawl internal link hingga depth tertentu (bisa diatur) |
| **50+ Social Platforms** | Deteksi link ke Facebook, Twitter, Instagram, GitHub, Telegram, dll |
| **Social Media Verification** | Cek apakah akun benar-benar tidak terdaftar (bukan cuma 404) |
| **S3 Bucket Hijack** | Deteksi bucket S3 yang bisa diambil alih |
| **GitHub Takeover** | Cek repo/org yang hilang |
| **Domain Expired** | Cek domain expired via WHOIS |
| **Nuclei Integration** | Scan broken links pakai Nuclei |
| **Live Report Streaming** | Hasil langsung keluar di file `.live` |
| **Resume Capability** | Lanjutin scan kalo terputus |
| **Debug Mode** (`--debug`) | Tampilkan semua proses detail |
| **Output Multiple Formats** | JSON + HTML + CSV |

---

## 📥 Installasi

### 1. Clone Repository

```bash
git clone https://github.com/BimaBalance/Broken-link-HijackingVVP.git
cd Broken-link-HijackingVVP
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Isi `requirements.txt`:**

```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
colorama>=0.4.6
lxml>=4.9.0
rich>=13.0.0
```

### 3. Install Tools (Opsional, untuk fitur lanjutan)

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/tomnomnom/waybackurls@latest
```

---

## 🚀 Cara Pakai

### Basic Scan (Single Domain)

```bash
python broken.py -d target.com -o hasil.json
```

### Scan Multiple Domains

```bash
python broken.py -l targets.txt -o hasil.json --threads 30
```

### Dengan Debug Mode (Verbose)

```bash
python broken.py -d target.com -o hasil.json --debug
```

### Dengan Nuclei Integration

```bash
python broken.py -d target.com -o hasil.json --nuclei
```

---

## 📋 Contoh Hasil Output

### JSON Output

```json
{
  "domain": ["target.com"],
  "timestamp": "2026-07-26T12:00:00",
  "stats": {
    "total_domains": 1,
    "total_subdomains": 45,
    "critical": 2,
    "high": 5,
    "medium": 3
  },
  "results": [
    {
      "domain": "target.com",
      "subdomain": "www.target.com",
      "url": "https://twitter.com/deleted_account",
      "platform": "twitter.com",
      "vulnerable": true,
      "severity": "HIGH",
      "confidence": 90,
      "status": "twitter.com: this account doesn't exist"
    }
  ]
}
```

### HTML Report

Laporan HTML profesional dengan:
- Statistik ringkasan
- Tabel temuan vulnerability
- Link langsung ke URL yang ditemukan

### CSV Output

File CSV yang bisa dibuka di Excel / spreadsheet.

---

## 🛠️ Command Options

| Option | Deskripsi |
|--------|-----------|
| `-d, --domain` | Target domain tunggal |
| `-l, --list` | File berisi daftar domain (satu per baris) |
| `-o, --output` | Output file (JSON + HTML + CSV otomatis) |
| `--delay` | Delay antar request (default: 0.3) |
| `--retries` | Maksimal percobaan ulang (default: 3) |
| `--threads` | Jumlah thread (default: 20) |
| `--depth` | Kedalaman crawl (default: 3) |
| `--timeout` | Timeout per request (default: 10) |
| `--rate-delay` | Delay antar request (rate limiting) |
| `--no-httpx` | Nonaktifkan httpx filter |
| `--nuclei` | Aktifkan Nuclei scan |
| `--no-wayback` | Nonaktifkan Wayback Machine |
| `--no-deep` | Nonaktifkan deep crawl |
| `--no-verify` | Skip verifikasi (lebih cepat) |
| `--no-resume` | Nonaktifkan resume |
| `--no-live` | Nonaktifkan live report |
| `--debug` | Aktifkan debug/verbose mode |

---

## 🔧 Platform yang Dideteksi

| Platform | Severity |
|----------|----------|
| Facebook, Instagram, Twitter, GitHub, Telegram, Discord | HIGH |
| LinkedIn, YouTube, Twitch, Reddit, GitLab, Bitbucket | HIGH |
| TikTok, Patreon, Snapchat | MEDIUM |
| Pinterest, Tumblr, Medium, DeviantArt | LOW |
| Spotify, SoundCloud, Vimeo, Flickr | LOW |

---

## 📸 Screenshot & Video Demo

### 1. Proses Scanning
![Proses Scanning](./Screenshot_2026-07-26-23-05-09-98_84d3000e3f4017145260f7618db1d683.jpg)

### 2. HTML Report
![HTML Report](./docs/html_report.png)

### 3. Debug Mode
![Debug Mode](./docs/debug_mode.png)

---

## ⚠️ Disclaimer

> **Tools ini hanya untuk testing yang sah dan tujuan edukasi.**  
> Penggunaan tanpa izin terhadap sistem yang tidak dimiliki atau tidak memiliki izin eksplisit adalah **ILEGAL**.  
> Developer tidak bertanggung jawab atas penyalahgunaan tools ini.

---

## 👨‍💻 Developer

**Bima Balance** – [Telegram @BimaBalance](https://t.me/BimaBalance)  
Team: **IJJ × Ikan Julung Julung**

---

## 📝 Contributing

Pull request dan issue selalu diterima. Silakan buat issue untuk bug report atau feature request.

---

## 📄 License

MIT License – Lihat file [LICENSE](LICENSE) untuk detail.

---

**Happy Hunting! 🚀**
