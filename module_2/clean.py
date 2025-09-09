import re
from bs4 import BeautifulSoup


def clean_data(soup):
    """
    Cleans and extracts information from a BeautifulSoup output.
    """
    results = []
    
    # Iterate through table rows in soup object
    for uni_row in soup.find_all("tr"):
        uni_name_div = uni_row.find("div", class_="tw-font-medium tw-text-gray-900 tw-text-sm")
        if not uni_name_div:
            continue  

        entry = {}

        #  Get University info
        university = uni_name_div.get_text(strip=True)

        # Get Program name info
        prog_div = uni_row.find_next("td", class_="tw-px-3 tw-py-5 tw-text-sm tw-text-gray-500")
        if prog_div:
            spans = prog_div.find_all("span")
            if spans:
                entry["program"] = f"{spans[0].get_text(strip=True)}, {university}"
            if len(spans) > 1:
                entry["Degree"] = spans[1].get_text(strip=True)  # Masters or PhD

        # Get date when this entry was added
        date_td = uni_row.find("td", class_=re.compile("tw-whitespace-nowrap"))
        if date_td:
            entry["date_added"] = date_td.get_text(strip=True)

        # Get the application status
        status_div = uni_row.find("div", class_=re.compile("tw-inline-flex.*tw-font-medium"))
        if status_div:
            status_text = status_div.get_text(" ", strip=True)
            match = re.search(r"(Accepted on .*|Rejected on .*|Wait listed on .*|Interview on .*)", status_text)
            if match:
                entry["status"] = match.group(1)

        # Get the url tag and concatenate with base url
        url_tag = uni_row.find("a", href=re.compile(r"/result/\d+"))
        if url_tag:
            entry["url"] = f"https://www.thegradcafe.com{url_tag.get("href")}"

        # Go through sibling table rows
        detail_row = uni_row.find_next_sibling("tr", class_="tw-border-none")
        if detail_row:
            
            # Check division tag
            tags = detail_row.find_all("div", class_=re.compile("tw-inline-flex"))
            for tag in tags:
                text = tag.get_text(strip=True)

                # Get semester for term
                if "Fall" in text or "Spring" in text:
                    entry["term"] = text

                # Get International / American
                if text in ["International", "American"]:
                    entry["US/International"] = text

                # Get GPA
                gpa_match = re.search(r"GPA\s+([\d\.]+)", text, re.I)
                if gpa_match:
                    entry["GPA"] = gpa_match.group(1)

                # Get GRE total
                gre_match = re.search(r"GRE\s+(\d+)$", text, re.I)
                if gre_match:
                    entry["GRE"] = gre_match.group(1)

                # Get GRE V
                gre_v_match = re.search(r"GRE V\s+(\d+)", text, re.I)
                if gre_v_match:
                    entry["GRE V"] = gre_v_match.group(1)

                # Get GRE AW
                gre_aw_match = re.search(r"GRE AW\s+(\d+)", text, re.I)
                if gre_aw_match:
                    entry["GRE AW"] = gre_aw_match.group(1)
                    
            # Check the second sibling table row for comments
            comment_row = detail_row.find_next_sibling("tr", class_="tw-border-none")
            if comment_row:
                comment_p = comment_row.find("p", class_="tw-text-gray-500 tw-text-sm tw-my-0")
                if comment_p:
                    # Flatten into one line
                    entry["comments"] = re.sub(r"\s+", " ", comment_p.get_text(strip=True))
                    
        # Append all entry results together
        results.append(entry)

    return results
