import tornado

class Project(tornado.web.UIModule):
    def render(
        self,
        project,
        config = None,
        show_tasks = None, # Provide a Task.status to render those tasks
        display = "jumbotron", # in ['jumbotron','panel']
    ):
        return self.render_string(
            "templates/module-project.html",
            config = config,
            project = project,
            show_tasks = show_tasks,
            display = display,
        )

class Task(tornado.web.UIModule):
    def render(
        self,
        task,
        config = None
    ):
        return self.render_string(
            "templates/module-task.html",
            config = config,
            task = task,
        )

class Comment(tornado.web.UIModule):
    def render(
        self,
        comment,
        config = None
    ):
        return self.render_string(
            "templates/module-comment.html",
            config = config,
            comment = comment,
        )
