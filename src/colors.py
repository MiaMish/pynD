from texttable import get_color_string


def colored_table_entry(entry, bcolor):
	return get_color_string(bcolor, entry)


def colored_row(row, bcolor):
	return [colored_table_entry(item, bcolor) for item in row]
