import re

def convert(md_link):
    # Retrive first "[]" name
    name = re.findall(r'\[.*?\]', md_link)[0]
    # Retrieve last "()" link
    link = re.findall(r'\(.*?\)', md_link)[-1]

    # Insert contents in org link format
    org_link = "[[{link}][{name}]]".format(link=link[1:-1], name=name[1:-1])

    return org_link

if __name__=="__main__":
    with open("md_link.txt", "r") as f:
        lines = f.readlines()
    for md_link in lines:
        org_link = convert(md_link)
        print(org_link)