def get_next_target(page):
	start_link = page.find('<a href=')
	if start_link == -1:
		return None, 0
	start_quote = page.find('"', start_link)
	end_quote = page.find('"', start_quote+1)
	url = page[start_quote+1: end_quote]
	return url, end_quote

def print_all_links(page):
	while True:
		url, end_quote = get_next_target(page)
		if url:
			print url
			page = page[end_quote:]
		else:
			break

print_all_links('from peter to cece: here is the link to what you ask <a href="www.udacity.com" and <a href="www.laioffer.com"')
