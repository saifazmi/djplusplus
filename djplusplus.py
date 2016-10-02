from flask import Flask, render_template
app = Flask(__name__)

	
@app.route('/')
def index():
	return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
	if request.method == 'POST':
		 # change to our backend
		 # redirect to some page
	else:
		return abort(405) #method not allowed


if __name__ == '__main__':
	app.debug = True
	app.run()
