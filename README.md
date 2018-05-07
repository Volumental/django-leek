# Django Leek
[![Build Status](https://travis-ci.com/Volumental/django-leek.svg?branch=master)](https://travis-ci.com/Volumental/django-leek)

**A simple async tasks queue via a django app and SocketServer, zero configs.**

[Why?](#why)     
[Overview](#overview)    
[Install](#install)     
[Settings](#settings)     
[Run the Tasks Queue Server](#run-the-tasks-queue-server)     
[Persistency](#persistency)     
[Failed Tasks](#failed-tasks)     
[Run the Tasks Queue on Another Server](#run-the-tasks-queue-on-another-server)     



## Why?

Although Celery is pretty much the standard for a django tasks queue solution, it can be complex to install and config.

The common case for a web application queue is to send emails: you don't want the django thread to wait until the SMTP, or email provider API, finishes. But to send emails from a site without a lot of traffic, or to run other similar simple tasks,  you don't need Celery. 

This queue app is a simple, up and running queueing solution.  The more complex distributed queues can wait until the website has a lot of traffic, and the scalability is really required.

## Overview


In a nutshell, a python SocketServer runs in the background, and listens to a tcp socket. SocketServer gets the request to run a task from it's socket, puts the task on a Queue. A Worker thread picks tasks from this Queue, and runs the tasks one by one.

You send a task request to the SocketServer with:

	
	from mysite.tasks_queue.API import push_task_to_queue
	...
	push_task_to_queue(a_callable,*args,**kwargs)
	
Sending email might look like:

	push_task_to_queue(send_mail,subject="foo",message="baz",recipient_list=[user.email])
	
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

Depends on the traffic: SocketServer is simple, but solid, and as the site gets more traffic, it's possible to move the django-queue server to another machine, separate database etc. At some point, probably, it's better to pick Celery. Until then, django-queue is a simple, solid, and no-hustle solution. 



## Install

1. Add the `tasks_queue` app to your django project
2. Replace `mysite` in the `tasks_queue/worker.py` with the full path to the `tasks_queue` in your project. It should look like the path in the project's manage.py. 
2. Add the tasks_queue app to `INSTALLED_APPS`
3. Migrate:

		$ manange.py migrate
	
4. The tasks_queue app has an API module, with a `push_task_to_queue` function. Use this function to send callables with args and kwargs to the queue, for the async run.


## Settings

To change the default django-queue settings, add a `TASKS_QUEUE` dictionary to your project main `settings.py` file.

This is the dictionary and the defaults:


	TASKS_QUEUE = {
		"MAX_RETRIES":3,
     	"TASKS_HOST":"localhost",
     	"TASKS_PORT":8002}

**MAX_RETRIES**    
The number of times the Worker thread will try to run a task before skipping it. The default is 3.

**TASKS_HOST**    
The host that runs the SocketServer. the default is 'localhost'.

**TASKS_PORT**    
The port that SocketServer listens to. The default is 8002.
	


## Run the Tasks Queue Server


###Start the Server  

From shell:

	$ python -m mysite.tasks_queue.service-start &
	
Provide the full path, without the .py extention. 


*Note: The tasks queue uses relative imports, and thus should run as a package. If you want to run it with the common `python service-start.py &`,
then edit the imports of the `tasks_queue` files, and convert all the imports to absolute imports.*

	
###Stop the Server

First stop the worker thread gracefully:

	$ python tasks_queue/service-stop-worker.py
	
This will send a stop event to the Worker thread.     
Check that the Worker thread stopped:

	$ python tasks_queue/shell.py ping
	Sent: ping
	Received: (False, 'Worker Off')
	
Now you can safely stop SocketServer:

	$ ps ax | grep tasks_queue
	12345 pts/1 S 7:20 python -m mysite.tasks_queue.service-start
	$ sudo kill 12345
	
	
###Ping the Server

From shell:

	$ python tasks_queue/shell.py ping
	Sent: ping
	Received: (True, "I'm OK")
	
### Tasks that are waiting on the Queue

From shell:

	$ python tasks_queue/shell.py waiting
	Sent: waiting
	Received: (True, 115)
	
115 tasks are waiting on the queue
	
### Count total tasks handled to the Queue

From shell:

	$ python tasks_queue/shell.py handled
	Sent: handled
	Received: (True, 862)
	
Total of 862 tasks were handled to the Queue from the moment the thread started
	

*Note: If you use the tasks server commands a lot, add shell aliases for these commands*

## Persistency

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
	
### Connections
If most of the tasks require a specific connection, such as SMTP or a database, you can edit the Worker class and add a ping or other check for this connection **before*8 the tasks runs. If the connection is not avaialable, just try to re-connect.

Otherwise the Worker will just run and fail a lot of tasks.

## Run the Tasks Queue on Another Server

The same `tasks_queue` app can run from another server, and provide a seprate server queue for the async tasks.

Here is a simple way to do it:

1. The queue server should be similar to the main django server, just without a webserver.
2. Deploy your django code to these two remotes: the main with the web-server, and the queue server
3. Open firewalls ports between the main django server, and the queue server, for the tasks_queue TASKS_PORT, and between the tasks_queue server and the databse server, for the database ports.
5. On the django main server, set TASKS_HOST to the tasks_queue server.

That's it! Now run the server in tasks_queue server with `service-start`, and the main django server will put the tasks to this tasks_queue server.

*Note: "main django server" can be more than one server that run django, and push message to the django queue server* 



Support this project with my affiliate link| 
-------------------------------------------|
https://www.linode.com/?r=cc1175deb6f3ad2f2cd6285f8f82cefe1f0b3f46|



	
	

	 
	

	







	

		
		
	



		
		

	






	
	
	
