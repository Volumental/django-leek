# Django Leek
![Logo](logo.svg)

[![Build Status](https://travis-ci.com/Volumental/django-leek.svg?branch=master)](https://travis-ci.com/Volumental/django-leek)

The _simple_ and _slick_ way to run async tasks in Django.

* Django-friendly API
* Easy to start and stop

Based on [django-queue](https://github.com/Aviah/django-queue).


## Why?
With a healthy mix of vegetables, such as [Celery](celeryproject.org) and [Carrot](http://www.django-carrot.com/) aleady in the midst, what does `django-leek` bring?

The most "lightweight" library so far has "install Redis" as step one. Although, Redis is a fantastic software, sometimes you just want a simple way of offload the webserver and run a task async, such as sending an email.

Here `django-leek` comes to the rescue. Usage and architecture cannot be simpler, and with so few moving parts, it should be very stable, although it's still not battle tested as e.g. Celery.

With `django-leek` you can get up and running quickly The more complex distributed queues can wait until the website has a lot of traffic, and the scalability is really required.

## Getting started
1. Install `django-leek` with pip

	```bash
    $ pip install django-leek
	````

2. Add `django-leek` to `INSTALLED_APPS` in your `settings.py` file.

3. Create tables needed

    ```bash
	$ manange.py migrate
	```

4. Make sure the django-leek server is running.

	```bash
	$ python manage.py runleek
	```

5. Go nuts

    ```python
	push_task_to_queue(send_mail, to='foobar@example.com')	
    ```

## Technical overview
In a nutshell, a python SocketServer runs in the background, listening on a tcp socket. SocketServer gets the request to run a task from it's socket, puts the task on a Queue. A Worker thread picks tasks from this Queue, and runs the tasks one by one.

### Components

1. Python SocketServer that listens to a tcp socket.
2. A Worker thread.
3. A python Queue

### Workflow
The workflow that runs an async task:

1. When `SocketServer` starts, it initializes the `Worker` thread.
2. `SocketServer` listens to requests.
3. When `SocketServer` receives a request - a callables with args and kwargs -   it puts the request on a python `Queue`.
4. The `Worker` thread picks a task from the `Queue`.
5. The `Worker` thread runs the task.

### Can this queue scale to production?
Depends on the traffic: SocketServer is simple, but solid, and as the site gets more traffic, it's possible to move the django-queue server to another machine, separate database etc. At some point, probably, it's better to pick Celery. Until then, django-leek is a simple, solid, and no-hustle solution. 

## Settings
To change the default django-queue settings, add a `TASKS_QUEUE` dictionary to your project main `settings.py` file.

This is the dictionary and the defaults:

	TASKS_QUEUE = {
		"MAX_RETRIES": 3,
     	"TASKS_HOST": "localhost",
     	"TASKS_PORT": 8002}

**MAX_RETRIES**    
The number of times the Worker thread will try to run a task before skipping it. The default is 3.

**TASKS_HOST**    
The host that runs the SocketServer. the default is 'localhost'.

**TASKS_PORT**    
The port that SocketServer listens to. The default is 8002.

## Persistence

### Tasks saved in the database

**QueuedTasks**   
The model saves every tasks pushed to the queue.    
The task is pickled as a `tasks_queue.tasks.Task` object, which is a simple class with a `callable`,`args` and `kwargs` attributes, and one method: `run()`

**SuccessTasks**    
The Worker thread saves to this model the `task_id` of every task that was carried out successfuly. **task_id** is the task's `QueuedTasks` id.

**FailedTasks**    
After the Worker tries to run a task several times according to `MAX_RETRIES`, and the task still fails, the Worker saves it to this model. The failed taks is saved by the `task_id`, with the exception message. Only the exception from the last run is saved.


### Purge Tasks

According to your project needs, you can purge tasks that the Worker completed successfuly.

The SQL to delete these tasks:

	DELETE queued,success
	FROM tasks_queue_queuedtasks queued
	INNER JOIN tasks_queue_successtasks success
	ON success.task_id = queued.id;
	
In a similar way, delete the failed tasks.
You can run a cron script, or other script, to purge the tasks.

## Failed Tasks

### Retry failed tasks with a script

When the Worker fails to run the task `MAX_RETRIES` times, it saves the **task_id** and the exception message to the `FailedTasks` model.

To re-try failed tasks, after they are saved to the database, you can run this script, from shell:

	$ python tasks_queue/run_failed_tasks.py
	
*Note: The path is provided in the script with `mysite`. Edit this entry with the full path to the tasks_queue in your project, similar to the path provided in the project's manage.py*


## Authors
Aviah and Samuel Carlsson

See [contributors]( https://github.com/Volumental/django-leek/graphs/contributors) for full list.
