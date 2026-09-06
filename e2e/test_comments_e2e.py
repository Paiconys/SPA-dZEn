"""End-to-end tests for SPA Comments (UI + API).

Requires running stack:
  docker compose up --build -d

Run from repo root:
  cd e2e && pip install -r requirements.txt && playwright install chromium
  pytest -v
"""

from __future__ import annotations

import re
import uuid

import pytest
import requests
from playwright.sync_api import Page, expect

from helpers import captcha_answer, fetch_new_captcha, png_bytes


def _unique_user() -> str:
    return f"e2e{uuid.uuid4().hex[:8]}"


def _open_new_discussion(page: Page) -> None:
    page.get_by_role("button", name="Добавить обсуждение").click()
    expect(page.get_by_role("heading", name="Add comment")).to_be_visible()


def _solve_visible_captcha(page: Page) -> None:
    form = page.locator("form.comment-form")
    form.locator(".captcha img").wait_for(state="visible")
    with page.expect_response(re.compile(r"/api/captcha/")) as captcha_resp:
        page.get_by_role("button", name="Refresh captcha").click()
    assert captcha_resp.value.ok
    # Wait until Vue wrote the new key onto the form
    key = captcha_resp.value.json()["captcha_key"]
    page.wait_for_function(
        """(expected) => {
          const el = document.querySelector('form.comment-form');
          return el && el.dataset.captchaKey === expected;
        }""",
        arg=key,
    )
    page.get_by_label("CAPTCHA", exact=True).fill(captcha_answer(key))


def test_api_list_roots_only(api_url: str):
    res = requests.get(f"{api_url}/api/comments/", timeout=10)
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "count" in data
    for item in data["results"]:
        assert item.get("parent") in (None, "")


def test_api_captcha_and_create_comment(api_url: str):
    key, value = fetch_new_captcha()
    username = _unique_user()
    res = requests.post(
        f"{api_url}/api/comments/",
        data={
            "username": username,
            "email": f"{username}@example.com",
            "text": "API e2e <strong>ok</strong>",
            "captcha_key": key,
            "captcha": value,
        },
        timeout=15,
    )
    assert res.status_code in (200, 201), res.text
    body = res.json()
    assert body["username"] == username
    assert "<strong>ok</strong>" in body["text"]
    assert body["parent"] is None


def test_api_create_with_image_resize(api_url: str, tmp_path):
    key, value = fetch_new_captcha()
    username = _unique_user()
    img_path = tmp_path / "big.png"
    img_path.write_bytes(png_bytes((500, 400)))

    res = requests.post(
        f"{api_url}/api/comments/",
        data={
            "username": username,
            "email": f"{username}@example.com",
            "text": "with image",
            "captcha_key": key,
            "captcha": value,
        },
        files={"file": ("big.png", img_path.read_bytes(), "image/png")},
        timeout=30,
    )
    assert res.status_code in (200, 201), res.text
    body = res.json()
    assert body["attachments"], body
    file_url = body["attachments"][0]["file"]
    assert "media" in file_url or file_url.startswith("/")


def test_home_loads_and_websocket_badge(page: Page):
    expect(page.get_by_role("heading", name="Comments").first).to_be_visible()
    expect(page.locator("text=WS:")).to_be_visible()
    expect(page.locator("text=WS: on")).to_be_visible(timeout=10_000)


def test_sorting_controls(page: Page):
    page.get_by_role("button", name="User Name").click()
    expect(page.get_by_role("button", name=re.compile(r"User Name"))).to_contain_text(
        re.compile(r"[↑↓]")
    )
    page.get_by_role("button", name=re.compile(r"^Date")).click()
    expect(page.get_by_role("button", name=re.compile(r"^Date"))).to_contain_text(
        re.compile(r"[↑↓]")
    )


def test_pagination_when_available(page: Page, api_url: str):
    count = requests.get(f"{api_url}/api/comments/", timeout=10).json()["count"]
    next_btn = page.get_by_role("button", name="Next")
    if count <= 25:
        expect(next_btn).to_be_disabled()
        return
    expect(next_btn).to_be_enabled()
    next_btn.click()
    expect(page.get_by_role("button", name="Prev")).to_be_enabled()
    page.get_by_role("button", name="Prev").click()
    expect(page.get_by_role("button", name="Prev")).to_be_disabled()


def test_expand_replies_toggle(page: Page):
    expand_btns = page.get_by_role("button", name=re.compile(r"Развернуть ответы"))
    # Replies may be on later pages if many fresh roots exist
    for _ in range(5):
        if expand_btns.count() > 0:
            break
        next_btn = page.get_by_role("button", name="Next")
        if not next_btn.is_enabled():
            break
        next_btn.click()
        page.wait_for_timeout(300)
        expand_btns = page.get_by_role(
            "button", name=re.compile(r"Развернуть ответы")
        )
    if expand_btns.count() == 0:
        pytest.skip("No nested replies in current data")
    expand_btns.first.click()
    expect(page.get_by_role("button", name="Свернуть ответы").first).to_be_visible()
    page.get_by_role("button", name="Свернуть ответы").first.click()
    expect(
        page.get_by_role("button", name=re.compile(r"Развернуть ответы")).first
    ).to_be_visible()


def test_new_discussion_form_preview_and_tags(page: Page):
    _open_new_discussion(page)
    text = page.get_by_label("Text", exact=True)
    text.fill("hello")
    text.click()
    text.press("ControlOrMeta+A")
    page.get_by_role("button", name="[strong]").click()
    assert "<strong>" in text.input_value()
    expect(page.get_by_role("heading", name="Preview")).to_be_visible()
    page.get_by_role("button", name="Cancel").click()
    expect(page.get_by_role("button", name="Добавить обсуждение")).to_be_visible()


def test_create_root_comment_via_ui(page: Page):
    username = _unique_user()
    body_text = f"E2E UI root {username}"
    _open_new_discussion(page)
    _solve_visible_captcha(page)

    page.get_by_label("User Name", exact=True).fill(username)
    page.get_by_label("E-mail", exact=True).fill(f"{username}@example.com")
    page.get_by_label("Text", exact=True).fill(f"{body_text} <i>comment</i>")

    with page.expect_response(
        lambda r: r.request.method == "POST" and "/api/comments/" in r.url
    ) as create_resp:
        page.get_by_role("button", name="Send").click()
    assert create_resp.value.ok, create_resp.value.text()

    expect(page.get_by_text(username, exact=True).first).to_be_visible(timeout=15_000)
    expect(page.get_by_text(body_text).first).to_be_visible()


def test_reply_form_appears_under_comment(page: Page):
    page.get_by_role("button", name="↩ Reply").first.click()
    expect(page.get_by_role("heading", name=re.compile(r"Reply to #"))).to_be_visible()
    expect(page.get_by_text(re.compile(r"Replying to"))).to_be_visible()
    page.get_by_role("button", name="Cancel").click()


def test_create_reply_via_ui(page: Page):
    username = _unique_user()
    page.get_by_role("button", name="↩ Reply").first.click()
    expect(page.get_by_role("heading", name=re.compile(r"Reply to #"))).to_be_visible()
    _solve_visible_captcha(page)

    page.get_by_label("User Name", exact=True).fill(username)
    page.get_by_label("E-mail", exact=True).fill(f"{username}@example.com")
    page.get_by_label("Text", exact=True).fill("E2E nested reply")

    with page.expect_response(
        lambda r: r.request.method == "POST" and "/api/comments/" in r.url
    ) as create_resp:
        page.get_by_role("button", name="Send").click()
    assert create_resp.value.ok, create_resp.value.text()
    body = create_resp.value.json()
    assert body.get("parent") is not None


def test_upload_image_and_lightbox(page: Page, sample_image: str):
    username = _unique_user()
    _open_new_discussion(page)
    _solve_visible_captcha(page)

    page.get_by_label("User Name", exact=True).fill(username)
    page.get_by_label("E-mail", exact=True).fill(f"{username}@example.com")
    page.get_by_label("Text", exact=True).fill("E2E with image")
    page.get_by_label("Attachment (JPG/GIF/PNG or TXT ≤ 100KB)").set_input_files(
        sample_image
    )

    with page.expect_response(
        lambda r: r.request.method == "POST" and "/api/comments/" in r.url
    ) as create_resp:
        page.get_by_role("button", name="Send").click()
    assert create_resp.value.ok, create_resp.value.text()

    expect(page.get_by_text(username, exact=True).first).to_be_visible(timeout=15_000)
    thumb = page.locator("button.att img.thumb").first
    expect(thumb).to_be_visible(timeout=10_000)
    thumb.click()
    expect(page.get_by_role("button", name="×")).to_be_visible()
    page.get_by_role("button", name="×").click()


def test_upload_txt_attachment(page: Page, sample_txt: str):
    username = _unique_user()
    _open_new_discussion(page)
    _solve_visible_captcha(page)

    page.get_by_label("User Name", exact=True).fill(username)
    page.get_by_label("E-mail", exact=True).fill(f"{username}@example.com")
    page.get_by_label("Text", exact=True).fill("E2E with txt")
    page.get_by_label("Attachment (JPG/GIF/PNG or TXT ≤ 100KB)").set_input_files(
        sample_txt
    )

    with page.expect_response(
        lambda r: r.request.method == "POST" and "/api/comments/" in r.url
    ) as create_resp:
        page.get_by_role("button", name="Send").click()
    assert create_resp.value.ok, create_resp.value.text()
    expect(page.get_by_text("e2e_note.txt")).to_be_visible(timeout=15_000)


def test_client_validation_blocks_bad_username(page: Page):
    _open_new_discussion(page)
    page.get_by_label("User Name", exact=True).fill("bad user!")
    page.get_by_label("E-mail", exact=True).fill("ok@example.com")
    page.get_by_label("Text", exact=True).fill("x")
    page.get_by_label("CAPTCHA", exact=True).fill("abc")
    page.get_by_role("button", name="Send").click()
    expect(page.get_by_text("Only latin letters and digits")).to_be_visible()


def test_websocket_live_refresh(page: Page, api_url: str):
    expect(page.locator("text=WS: on")).to_be_visible(timeout=10_000)

    key, value = fetch_new_captcha()
    username = _unique_user()
    res = requests.post(
        f"{api_url}/api/comments/",
        data={
            "username": username,
            "email": f"{username}@example.com",
            "text": "ws live e2e",
            "captcha_key": key,
            "captcha": value,
        },
        timeout=15,
    )
    assert res.status_code in (200, 201), res.text
    expect(page.get_by_text(username, exact=True).first).to_be_visible(timeout=15_000)
