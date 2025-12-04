#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime
from enum import Enum

class PriorityEnum(Enum):
    low = "baixa"
    medium = "média"
    high = "alta"

class StatusEnum(Enum):
    pending = "pendente"
    canceled = "cancelada"
    delayed = "atrasada"
    blocked = "bloqueada"
    concluded = "concluída"
    ongoing = "em progresso"

class Task:
    def __init__(self, title, description, deadline, priority):
        self.title = title
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.status = StatusEnum.pending

    def conclude(self):
        self.status = StatusEnum.concluded

    def edit(self, title=None, description=None, deadline=None, priority=None):
        if title:
            self.title = title
        if description:
            self.description = description
        if deadline:
            self.deadline = deadline
        if priority:
            self.priority = priority

    def checkDelay(self):
        deadline = datetime.strptime(self.deadline, "%Y-%m-%d")
        today = datetime.today()
        if deadline < today and self.status != StatusEnum.concluded:
            self.status = StatusEnum.delayed

    def toDict(self):
        return {
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline,
            "priority": self.priority.value,
            "status": self.status.value
        }

    @staticmethod
    def fromDict(data):
        priority_map = {
            'baixa': PriorityEnum.low,
            'média': PriorityEnum.medium,
            'alta': PriorityEnum.high
        }

        status_map = {
            'pendente': StatusEnum.pending,
            'cancelada': StatusEnum.canceled,
            'atrasada': StatusEnum.delayed,
            'bloqueada': StatusEnum.blocked,
            'concluída': StatusEnum.concluded,
            'em progresso': StatusEnum.ongoing
        }
        
        status = status_map.get(data["status"].lower(), StatusEnum.pending)
        priority = priority_map.get(data["priority"].lower(), PriorityEnum.low)
        
        return Task(data["title"], data["description"], data["deadline"], priority)

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.loadTasks()

    def addTask(self, task):
        self.tasks.append(task)
        self.saveTasks()

    def listTasks(self):
        return self.tasks

    def filter(self, status):
        return [task for task in self.tasks if task.status == status]

    def removeTask(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
            self.saveTasks()

    def concludeTask(self, task):
        task.conclude()
        self.saveTasks()

    def saveTasks(self):
        tasksDict = [task.toDict() for task in self.tasks]
        with open("tasks.json", "w") as file:
            json.dump(tasksDict, file)

    def loadTasks(self):
        try:
            with open("tasks.json", "r") as file:
                tasksDict = json.load(file)
                self.tasks = [Task.fromDict(task) for task in tasksDict]
        except FileNotFoundError:
            self.tasks = []

    def updateTaskList(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)

        for task in self.listTasks():
            treeview.insert("", "end", values=(task.title, task.status.value, task.deadline, task.priority.value))

def addTaskGUI():
    title = entryTitle.get()
    description = entryDescription.get()
    deadline = entryDeadline.get()
    priority = comboPriority.get()

    if not title or not description or not deadline or not priority:
        messagebox.showerror("Error", "Preencha todos os campos.")
        return

    try:
        priority_enum = PriorityEnum(priority)
    except ValueError:
        messagebox.showerror("Error", "Prioridade inválida.")
        return
    
    task = Task(title, description, deadline, priority_enum)
    taskManager.addTask(task)
    taskManager.updateTaskList(taskList)

    entryTitle.delete(0, tk.END)
    entryDescription.delete(0, tk.END)
    entryDeadline.delete(0, tk.END)

def removeTaskGUI():
    selected = taskList.selection()
    if not selected:
        messagebox.showerror("Error", "Selecione uma tarefa para remover.")
        return

    for item in selected:
        title = taskList.item(item)["values"][0]
        task = next((t for t in taskManager.listTasks() if t.title == title), None)
        if task:
            taskManager.removeTask(task)

    taskManager.updateTaskList(taskList)

def concludedTaskGUI():
    selected = taskList.selection()
    if not selected:
        messagebox.showerror("Error", "Selecione uma tarefa para concluir.")
        return

    for item in selected:
        title = taskList.item(item)["values"][0]
        task = next((t for t in taskManager.listTasks() if t.title == title), None)
        if task:
            taskManager.concludeTask(task)

    taskManager.updateTaskList(taskList)

root = tk.Tk()
root.title("Gerenciador de Tarefas")

taskManager = TaskManager()

labelTitle = tk.Label(root, text="Título:")
labelTitle.grid(row=0, column=0)

entryTitle = tk.Entry(root, width=40)
entryTitle.grid(row=0, column=1)

labelDescription = tk.Label(root, text="Descrição:")
labelDescription.grid(row=1, column=0)

entryDescription = tk.Entry(root, width=40)
entryDescription.grid(row=1, column=1)

labelDeadline = tk.Label(root, text="Prazo (DD-MM-AAAA):")
labelDeadline.grid(row=2, column=0)

entryDeadline = tk.Entry(root, width=40)
entryDeadline.grid(row=2, column=1)

labelPriority = tk.Label(root, text="Prioridade:")
labelPriority.grid(row=3, column=0)

comboPriority = ttk.Combobox(root, values=["baixa", "média", "alta"], width=37)
comboPriority.grid(row=3, column=1)

buttonAdd = tk.Button(root, text="Adicionar Tarefa", command=addTaskGUI)
buttonAdd.grid(row=4, column=1)

buttonConcluded = tk.Button(root, text="Concluir Tarefa", command=concludedTaskGUI)
buttonConcluded.grid(row=5, column=0)

buttonRemove = tk.Button(root, text="Remover Tarefa", command=removeTaskGUI)
buttonRemove.grid(row=5, column=1)


taskList = ttk.Treeview(root, columns=("Título", "Status", "Prazo", "Prioridade"), show="headings")
taskList.grid(row=6, column=0, columnspan=2)

taskList.heading("Título", text="Título")
taskList.heading("Status", text="Status")
taskList.heading("Prazo", text="Prazo")
taskList.heading("Prioridade", text="Prioridade")

taskManager.updateTaskList(taskList)

root.bind("<Escape>", lambda event: root.destroy())

root.mainloop()
