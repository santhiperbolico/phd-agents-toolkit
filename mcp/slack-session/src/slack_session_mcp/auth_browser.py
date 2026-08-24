"""Interactive Slack credential extraction with Playwright."""

import time
from pathlib import Path

from slack_session_mcp.auth_capture import (
    AuthExtractError,
    CapturedCredentials,
    credentials_complete,
    parse_team_id_from_url,
    parse_token_from_playwright_request,
    pick_session_cookie,
    scrape_token_from_page_html,
)

DEFAULT_TIMEOUT_SECONDS = 300
POLL_INTERVAL_SECONDS = 1.0
SLACK_CLIENT_URL = "https://app.slack.com/client"
PAGE_TOKEN_SCRIPT = """
() => {
  const html = document.documentElement ? document.documentElement.innerHTML : "";
  const htmlMatch = html.match(/"api_token":"(xoxc-[^"]+)"/);
  if (htmlMatch) {
    return htmlMatch[1];
  }
  for (const key of Object.keys(localStorage)) {
    const value = localStorage.getItem(key) || "";
    const match = value.match(/xoxc-[A-Za-z0-9-]+/);
    if (match) {
      return match[0];
    }
  }
  return "";
}
"""


def profile_dir_for_alias(alias: str, base_dir: Path | None = None) -> Path:
    """
    Return the persistent browser profile directory for a workspace alias.

    Parameters
    ----------
    alias
        Workspace alias, for example ``euclid``.
    base_dir
        Optional parent directory. Defaults to ``~/.local/share/slack-session-tools/profiles``.

    Returns
    -------
    Path
        Directory that stores the Playwright user profile.
    """
    root = base_dir or Path.home() / ".local/share/slack-session-tools/profiles"
    return root / alias


def scrape_token_from_page(page: object) -> str:
    """
    Read a Slack ``xoxc`` token from the active page DOM or local storage.

    Parameters
    ----------
    page
        Playwright ``Page`` instance.

    Returns
    -------
    str
        Token value, or an empty string when absent.
    """
    try:
        token = page.evaluate(PAGE_TOKEN_SCRIPT)
        if isinstance(token, str) and token.startswith("xoxc-"):
            return token
    except Exception:
        pass
    try:
        html = page.content()
        return scrape_token_from_page_html(html)
    except Exception:
        return ""


def extract_credentials_with_playwright(
    alias: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    profile_base: Path | None = None,
    headed: bool = True,
) -> CapturedCredentials:
    """
    Open Slack in a browser, wait for login and capture session credentials.

    Parameters
    ----------
    alias
        Workspace alias to label the captured entry.
    timeout_seconds
        Maximum wait time for the user to finish login.
    profile_base
        Optional parent directory for persistent browser profiles.
    headed
        When true, show the browser window.

    Returns
    -------
    CapturedCredentials
        Team ID, ``xoxc`` token and ``xoxd`` cookie.

    Raises
    ------
    AuthExtractError
        If Playwright is missing or extraction times out.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise AuthExtractError(
            "Playwright is not installed. Run: "
            "pip install 'slack-session-mcp[auth]' && playwright install chromium"
        ) from exc

    profile_dir = profile_dir_for_alias(alias, profile_base)
    profile_dir.mkdir(parents=True, exist_ok=True)
    captured_token = ""
    deadline = time.monotonic() + timeout_seconds

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not headed,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        def remember_token(request: object) -> None:
            nonlocal captured_token
            if captured_token:
                return
            token = parse_token_from_playwright_request(request)
            if token:
                captured_token = token

        context.on("request", remember_token)
        page.goto(SLACK_CLIENT_URL, wait_until="domcontentloaded")

        while time.monotonic() < deadline:
            team_id = parse_team_id_from_url(page.url)
            if not captured_token:
                captured_token = scrape_token_from_page(page)
            try:
                session_cookie = pick_session_cookie(context.cookies())
            except Exception:
                session_cookie = ""
            if credentials_complete(team_id, captured_token, session_cookie):
                context.close()
                return CapturedCredentials(
                    alias=alias.strip(),
                    team_id=team_id,
                    token=captured_token,
                    session_cookie=session_cookie,
                )
            page.wait_for_timeout(int(POLL_INTERVAL_SECONDS * 1000))

        context.close()

    raise AuthExtractError(
        f"Timed out after {timeout_seconds}s waiting for Slack login for {alias!r}. "
        "Open a workspace in the browser window and try again."
    )
