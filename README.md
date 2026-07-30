# RaceStay — ATM 2026 (static prototype)

หน้า prototype เดี่ยว (self-contained HTML) ของ RaceStay สำหรับงาน **Amazing Thailand Marathon Bangkok 2026**
publish เป็นเว็บสาธิตบน **GitHub Pages**

- `index.html` — หน้าเว็บทั้งหมด (CSS/JS/โลโก้ inline อยู่ในไฟล์เดียว — เปิดไฟล์นี้ได้เลย)
- `logo.svg` — โลโก้ RACESTAY (ใช้เป็น favicon; ตัวโลโก้ใน nav ฝัง inline อยู่แล้ว)
- `.nojekyll` — บอก GitHub Pages ไม่ต้องประมวลผลด้วย Jekyll

> หมายเหตุ: ราคา/ข้อมูลโรงแรมในหน้านี้เป็น **ตัวอย่างสาธิต** และแผนที่ใช้ Stay22 โดยยัง `aid=affiliateid` (ยังไม่ใช่ Partner ID จริง) — ก่อนใช้จริงต้องแทน `affiliateid` ด้วย Stay22 aid ของคุณ

---

## Publish ขึ้น GitHub Pages (สำหรับ Claude Code)

**ต้องมีก่อน:** `git` + `gh` (GitHub CLI) และล็อกอินแล้ว (`gh auth login` — ต้องมีสิทธิ์ scope `repo` และ `workflow`)

รันทีเดียวจบด้วยสคริปต์:

```bash
bash publish.sh
```

หรือรันทีละคำสั่ง:

```bash
# 1) สร้าง git repo ในโฟลเดอร์นี้
git init -b main
git add -A
git commit -m "RaceStay ATM 2026 — static prototype"

# 2) สร้าง repo บน GitHub (public) แล้ว push (ตั้งชื่อ repo = racestay)
gh repo create racestay --public --source=. --remote=origin --push

# 3) เปิด GitHub Pages ให้ serve จาก branch main / root
OWNER=$(gh api user -q .login)
gh api --method POST "repos/$OWNER/racestay/pages" \
  -f "source[branch]=main" -f "source[path]=/"

# 4) ดู URL ที่ได้ (รอสัก 1–2 นาทีให้ build เสร็จ)
gh api "repos/$OWNER/racestay/pages" -q .html_url
```

เว็บจะออกที่: `https://<github-username>.github.io/racestay/`

### อัปเดตหน้าเว็บภายหลัง

```bash
git add -A && git commit -m "update" && git push
```
GitHub Pages จะ build ใหม่อัตโนมัติภายในไม่กี่นาที

### ถ้าอยากเปิด Pages จากหน้าเว็บแทน (ไม่ใช้คำสั่งข้อ 3)
ไปที่ repo → **Settings → Pages → Build and deployment → Source = Deploy from a branch → Branch = `main` / `/ (root)` → Save**

---

## Custom domain (ถ้ามีโดเมนของตัวเอง)

```bash
echo "yourdomain.com" > CNAME
git add CNAME && git commit -m "add custom domain" && git push
```
แล้วตั้ง DNS ที่ผู้ให้บริการโดเมน: CNAME ชี้ `<github-username>.github.io` (หรือ A records ของ GitHub Pages)
