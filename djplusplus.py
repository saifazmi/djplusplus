from flask import Flask, render_template
from analytics import read_music
app = Flask(__name__)

	
@app.route('/')
def index():
	return render_template('index.html')


@app.route('/submit')
def submit():
	read_music()
	return render_template('index.html')

if __name__ == '__main__':
	app.debug = True
	app.run()
