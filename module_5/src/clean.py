"""
This module provides a function for cleaning and extracting data
from a BeautifulSoup object.
"""
import re


def _extract_university_info(uni_row):
    """
    Extracts the university name from a table row.
    """
    uni_name_div = uni_row.find(
        "div", class_="tw-font-medium tw-text-gray-900 tw-text-sm"
    )
    if uni_name_div:
        return uni_name_div.get_text(strip=True)
    return None


def _extract_program_info(uni_row, university):
    """
    Extracts program and degree information.
    """
    entry = {}
    prog_div = uni_row.find_next("td", class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500")
    if prog_div:
        spans = prog_div.find_all("span")
        if spans:
            entry["program"] = f"{spans[0].get_text(strip=True)}, {university}"
        if len(spans) > 1:
            entry["Degree"] = spans[1].get_text(strip=True)
    return entry


def _extract_status_and_date(uni_row):
    """
    Extracts application status and date added.
    """
    entry = {}
    date_td = uni_row.find("td", class_=re.compile("tw-whitespace-nowrap"))
    if date_td:
        entry["date_added"] = date_td.get_text(strip=True)

    status_div = uni_row.find("div", class_=re.compile("tw-inline-flex.*tw-font-medium"))
    if status_div:
        status_text = status_div.get_text(" ", strip=True)
        match = re.search(
            r"(Accepted on .*|Rejected on .*|Wait listed on .*|Interview on .*)",
            status_text,
        )
        if match:
            entry["status"] = match.group(1)
    return entry


def _extract_gre_and_gpa(tag):
    """
    Extracts GRE and GPA scores from a tag.
    """
    entry = {}
    gpa_match = re.search(r"GPA\s+([\d.]+)", tag, re.I)
    if gpa_match:
        entry["GPA"] = gpa_match.group(1)

    gre_match = re.search(r"GRE\s+(\d+)$", tag, re.I)
    if gre_match:
        entry["GRE"] = gre_match.group(1)

    gre_v_match = re.search(r"GRE V\s+(\d+)", tag, re.I)
    if gre_v_match:
        entry["GRE V"] = gre_v_match.group(1)

    gre_aw_match = re.search(r"GRE AW\s+(\d+)", tag, re.I)
    if gre_aw_match:
        entry["GRE AW"] = gre_aw_match.group(1)
    return entry


def _extract_details(detail_row):
    """
    Extracts additional details like GPA, GRE, term, and location.
    """
    entry = {}
    if not detail_row:
        return entry

    tags = detail_row.find_all("div", class_=re.compile("tw-inline-flex"))
    for tag in tags:
        text = tag.get_text(strip=True)

        # Get semester for term
        if "Fall" in text or "Spring" in text:
            entry["term"] = text

        # Get International / American
        if text in ["International", "American"]:
            entry["US/International"] = text

        entry.update(_extract_gre_and_gpa(text))
    return entry


def _extract_comments(detail_row):
    """
    Extracts comments from the table row sibling.
    """
    entry = {}
    if not detail_row:
        return entry

    comment_row = detail_row.find_next_sibling("tr", class_="tw-border-none")
    if comment_row:
        comment_p = comment_row.find("p", class_="tw-text-gray-500 tw-text-sm tw-my-0")
        if comment_p:
            entry["comments"] = re.sub(r"\s+", " ", comment_p.get_text(strip=True))
    return entry


def clean_data(soup):
    """
    Cleans and extracts information from a BeautifulSoup output.
    """
    results = []

    # Iterate through table rows in soup object
    for uni_row in soup.find_all("tr"):
        university = _extract_university_info(uni_row)
        if not university:
            continue

        entry = {"url": None}

        # Get University and Program info
        entry.update(_extract_program_info(uni_row, university))

        # Get date and status
        entry.update(_extract_status_and_date(uni_row))

        # Get the url tag and concatenate with base url
        url_tag = uni_row.find("a", href=re.compile(r"/result/\d+"))
        if url_tag:
            entry["url"] = f"https://www.thegradcafe.com{url_tag.get('href')}"

        # Go through sibling table rows for details
        detail_row = uni_row.find_next_sibling("tr", class_="tw-border-none")
        entry.update(_extract_details(detail_row))
        entry.update(_extract_comments(detail_row))

        results.append(entry)

    return results
