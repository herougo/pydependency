from flask import Flask, request
from pydependency.dependency_finder import DependencyFinder


app = Flask(__name__)

df = DependencyFinder()

@app.route("/", methods=['POST'])
def get_header():
	try:
		data = dict(request.form)
		file_path = data['file_path']
	except Exception as ex:
		return 'Exception: {}\nInvalid input: {}'.format(ex, request.form)
	df.set_current_file(file_path)
	header = df.extract_missing_dependency_header()
	return header
