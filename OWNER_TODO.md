# Things I Need You To Do

This is your personal checklist. I (the coding assistant) am building everything I
can on my own and pushing it to GitHub. This file lists the handful of things **only
you** can do, in plain language, roughly in the order you'll need them.

I keep this file up to date as we go. Nothing here is urgent unless it says
**NEEDED NOW**.

Legend: ✅ done · ⏳ needed soon · ⬜ needed later

---

## ✅ 1. Create the GitHub repo — DONE
You made https://github.com/aravgarg28/cv-nutrition-scanner and I've pushed all the
code there. From now on the code lives online and gets auto-tested on every push.
Nothing more to do here.

---

## ⏳ 2. Glance at the automatic tests (optional, 2 min)
Now that code is on GitHub, a robot runs tests every time I push.
- Go to the repo → **Actions** tab. Green check = healthy.
- If you ever see a red X, tell me and I'll fix it.
You don't have to do this — I watch the results too. It's just nice to know it's there.

---

## ⬜ 3. Approve the "safety-critical" parts when I ask (quick yes/no)
Some parts decide **what allergen warnings a user sees**. If those are wrong, someone
could get hurt, so I stop and ask you to confirm the wording/logic before it's final.
- This is a quick read-and-approve, not work.
- I'll point you to exactly what to look at each time.
- **Waiting on you now:** the list of allergen "status" labels (e.g. "declared",
  "may contain", "not found"). I already built it — just want your eyes on it when
  you have a moment. No rush; it won't block me.

---

## ⬜ 4. Sign up for a few FREE accounts (when we reach hosting/data/AI)
All free. I can't create accounts, so when we get here I'll give you exact links and
tell you which secret values to paste where. You'll need:
- A **database host** (to store users/scans online) — e.g. Neon (free).
- A **file storage** account (to store the photos) — e.g. Cloudflare R2 (free).
- A **USDA food-data key** (free, instant) — for nutrition facts.
- An **AI-assistant key** (free tier) — for the "ask a question" feature. I'll help
  you check its terms first (it must not train on our users' data).
- A **free email-sending** account — for "verify your email" messages.
👉 Not needed yet. I'll bundle these into one short setup session when the time comes.

---

## ⬜ 5. Take some test photos (when we build food recognition)
The food-recognition and label-reading features need real examples to test against:
- ~300–500 phone photos of everyday foods (for recognition).
- ~100 photos of packaged-food ingredient labels and nutrition panels (for the
  label reader), including some tricky ones: curved packages, shiny wrappers, small
  print, dim light.
- No faces or people in the shots; just the food/label.
👉 I'll give you a simple shot list when we get there.

---

## ⬜ 6. Run the AI model training (when the training code is ready)
This is the big one, but it's mostly the computer working, not you.
- I write all the training code and give you a ready-to-run notebook.
- You open it in a **free Google Colab or Kaggle account** (your login) and press run.
- It trains for a while (hours per run, spread over some days). You just restart it if
  the free session times out — I'll build it to pick up where it left off.
👉 Needs your Google/Kaggle login, which is why only you can start it.

---

## ⬜ 7. Curation sign-off (a couple of short review tasks)
Two small human-judgment checks I'll prepare for you:
- A table matching each food type to its nutrition record (make sure they look right).
- The list of "hidden allergen" words (e.g. "whey" = milk). I draft it; you sanity-check.

---

## What I'm doing without you (for context)
Everything else — the whole backend, the phone app, the label reader, the allergen
logic, the nutrition math, the assistant, the tests, the deployment setup — I build
and push myself. You'll see steady commits on GitHub. When I hit one of the items
above, I'll update this file and tell you plainly what I need.
