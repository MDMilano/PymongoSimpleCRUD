from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['task_manager']
tasks_collection = db['tasks']


# Routes
@app.route('/')
def index():
    tasks = list(tasks_collection.find())
    # Convert ObjectId to string for JSON serialization
    for task in tasks:
        task['_id'] = str(task['_id'])
    return render_template('index.html', tasks=tasks)


# Create task
@app.route('/tasks', methods=['POST'])
def create_task():
    title = request.form.get('title')
    description = request.form.get('description')

    if title:
        task = {
            'title': title,
            'description': description,
            'completed': False
        }
        tasks_collection.insert_one(task)

    return redirect(url_for('index'))


# Read task
@app.route('/tasks/<task_id>')
def get_task(task_id):
    task = tasks_collection.find_one({'_id': ObjectId(task_id)})
    if task:
        task['_id'] = str(task['_id'])
        return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404


# Update task
@app.route('/tasks/<task_id>', methods=['PUT', 'POST'])
def update_task(task_id):
    title = request.form.get('title')
    description = request.form.get('description')
    completed = request.form.get('completed') == 'on'

    update_data = {}
    if title:
        update_data['title'] = title
    if description:
        update_data['description'] = description
    update_data['completed'] = completed

    tasks_collection.update_one(
        {'_id': ObjectId(task_id)},
        {'$set': update_data}
    )

    return redirect(url_for('index'))


# Delete task
@app.route('/tasks/<task_id>/delete', methods=['POST'])
def delete_task(task_id):
    tasks_collection.delete_one({'_id': ObjectId(task_id)})
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)