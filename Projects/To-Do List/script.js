document.addEventListener('DOMContentLoaded', function() {
    const newTaskInput = document.getElementById('new-task-input');
    const addTaskButton = document.getElementById('add-task-button');
    const taskList = document.getElementById('task-list');

    function loadTasks() {
        const tasks = JSON.parse(localStorage.getItem('tasks')) || [];
        tasks.forEach(task => addTaskToDOM(task.text, task.completed));
    }

    function saveTasks() {
        const tasks = [];
        taskList.querySelectorAll('li').forEach(taskItem => {
            tasks.push({
                text: taskItem.querySelector('span').innerText,
                completed: taskItem.classList.contains('completed')
            });
        });
        localStorage.setItem('tasks', JSON.stringify(tasks));
    }

    function addTaskToDOM(text, completed = false) {
        const li = document.createElement('li');
        li.className = completed ? 'completed' : '';
        li.innerHTML = `
            <span contenteditable="true">${text}</span>
            <input type="checkbox" ${completed ? 'checked' : ''}>
            <button>Delete</button>
        `;

        li.querySelector('input[type="checkbox"]').addEventListener('change', function() {
            li.classList.toggle('completed');
            saveTasks();
        });

        li.querySelector('button').addEventListener('click', function() {
            li.remove();
            saveTasks();
        });

        li.querySelector('span').addEventListener('blur', saveTasks);

        taskList.appendChild(li);
    }

    addTaskButton.addEventListener('click', function() {
        const text = newTaskInput.value.trim();
        if (text !== '') {
            addTaskToDOM(text);
            saveTasks();
            newTaskInput.value = '';
        } else {
            alert('Task cannot be empty');
        }
    });

    loadTasks();
});
