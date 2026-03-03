import pytest
import requests_mock
from app.services.upsc_summarizer import fetch_article_content

def test_fetch_article_content_the_hindu():
    url = "https://www.thehindu.com/news/national/some-news.html"
    html_content = """
    <html>
        <body>
            <div id="content-body-14263">
                <p>This is the first paragraph of The Hindu article.</p>
                <p>This is the second paragraph.</p>
            </div>
            <div class="advertisement">Ad content</div>
            <script>console.log("junk");</script>
        </body>
    </html>
    """

    with requests_mock.Mocker() as m:
        m.get(url, text=html_content)
        result = fetch_article_content(url)

    assert "This is the first paragraph of The Hindu article." in result
    assert "This is the second paragraph." in result
    assert "Ad content" not in result
    assert "junk" not in result

def test_fetch_article_content_indian_express():
    url = "https://indianexpress.com/article/india/some-news/"
    html_content = """
    <html>
        <body>
            <div class="story_details">
                <p>Express network content here.</p>
                <p>More details from IE.</p>
            </div>
            <div id="bottom-bar">Subscribe now!</div>
        </body>
    </html>
    """

    with requests_mock.Mocker() as m:
        m.get(url, text=html_content)
        result = fetch_article_content(url)

    assert "Express network content here." in result
    assert "More details from IE." in result
    assert "Subscribe now!" not in result

def test_fetch_article_content_pib():
    url = "https://pib.gov.in/PressReleasePage.aspx?PRID=12345"
    html_content = """
    <html>
        <body>
            <div class="innner-page-main-about-us-content-right-part">
                <p>Ministry of Defence</p>
                <p>Press release content here.</p>
            </div>
            <div class="social-share">Share on Twitter</div>
        </body>
    </html>
    """

    with requests_mock.Mocker() as m:
        m.get(url, text=html_content)
        result = fetch_article_content(url)

    assert "Ministry of Defence" in result
    assert "Press release content here." in result
    assert "Share on Twitter" not in result

def test_fetch_article_content_generic_fallback():
    url = "https://www.example-news.com/article"
    # The generic fallback looks for the div with the most paragraphs,
    # giving extra weight to paragraphs > 100 chars.
    long_text = "This is a very long paragraph that exceeds one hundred characters to test the scoring mechanism of the generic fallback extractor in the upsc summarizer service. " * 2
    html_content = f"""
    <html>
        <body>
            <div id="sidebar">
                <p>Short link 1</p>
                <p>Short link 2</p>
            </div>
            <div id="main-content">
                <p>Introduction paragraph.</p>
                <p>{long_text}</p>
                <p>Conclusion paragraph.</p>
            </div>
        </body>
    </html>
    """

    with requests_mock.Mocker() as m:
        m.get(url, text=html_content)
        result = fetch_article_content(url)

    assert "Introduction paragraph." in result
    assert "Conclusion paragraph." in result
    assert "Short link 1" not in result

def test_fetch_article_content_ultimate_fallback():
    url = "https://www.example-weird-site.com/article"
    # If no main div is found, it just concatenates all <p> tags
    html_content = """
    <html>
        <body>
            <p>Just a random paragraph.</p>
            <span>Some span</span>
            <p>Another random paragraph.</p>
        </body>
    </html>
    """

    with requests_mock.Mocker() as m:
        m.get(url, text=html_content)
        result = fetch_article_content(url)

    assert "Just a random paragraph." in result
    assert "Another random paragraph." in result

def test_fetch_article_content_network_error():
    url = "https://www.error-site.com"

    with requests_mock.Mocker() as m:
        m.get(url, exc=Exception("Connection timeout"))
        result = fetch_article_content(url)

    assert result == ""
