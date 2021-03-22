import json

class JSONtoSQLParser():
	def __init__(self, json_file_path, table_name):
		self.json = self.read_json_from_file(json_file_path)
		self.sql = "CREATE TABLE " + table_name + " ("

		self.columns = {}
		self.columns['company_id'] = 'bigint'
		self.columns['project_id'] = 'bigint'

	def read_json_from_file(self, file_name):
		json_file = open(file_name, 'r')
		json_data = json.load(json_file)
		json_file.close()
		return json_data

	def set_primary_keys(self):
		primary_keys = []
		sql_primary_key = "PRIMARY KEY ("

		print("Enter primary keys for table. Enter 'q' when done.")
		done = False
		while not done:
			print("Enter primary key:", end=" ")
			column = input()
			if column == 'q':
				done = True
			elif column in self.columns and column not in primary_keys:
				sql_primary_key += column + ", "
				primary_keys.append(column)

		if len(primary_keys) == 0:
			return ""
		else:
			return sql_primary_key + ")\n"

	def convert(self):
		for key in self.json:
			self.convert_pair(key, self.json[key])
		
		for k, v in self.columns.items():
			self.sql += "\n" + k + " " + v + ","

		self.sql += "\n" + self.set_primary_keys()
		
		self.sql += ");"

		return self.sql

	def convert_pair(self, name, data):
		type_codes = {
			'b': 'bit',
			'bi': 'bigint',
			'd': 'date',
			'dt': 'datetime',
			'f': 'float',
			'i': 'int',
			'm': 'money',
			'vl': 'varchar(MAX)',
			'vm': 'varchar(1000)',
			'vs': 'varchar(255)'
		}
		if type(data) is dict:
			for newKey in data:
				self.convert_pair(name + "_" + newKey, data[newKey])
		elif type(data) is list:
			self.columns[name + '_json'] = 'nvarchar(MAX)'
		else:
			valid_input = False
			while not valid_input:
				valid_input = True
				print("Enter datatype for " + name + ":", end=" ")
				datatype = input()
				if datatype in type_codes:
					self.columns[name] = type_codes[datatype]
				else:
					valid_input = False

if __name__=='__main__':
	json_file_path = 'data.json'
	sql_file_path = 'sql_create.txt'

	print("##################\nJSON to SQL Parser\n##################\n")
	print("Enter table name:")
	table_name = input()

	parser = JSONtoSQLParser(json_file_path, table_name)
	sql = parser.convert()

	print(sql, file=open(sql_file_path, 'w'))
	print("SQL 'CREATE' command saved to '" + sql_file_path + "'.")
