#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime
from enum import Enum

# Enum para Prioridade
class PriorityEnum(Enum):
    low = "baixa"
    medium = "média"
    high = "alta"

# Enum para Status
class StatusEnum(Enum):
    pending = "pendente"
    canceled = "cancelada"
    delayed = "atrasada"
    blocked = "bloqueada"
    concluded = "concluída"
    ongoing = "em progresso"

# Classe que representa uma única Tarefa
class Task:
    def __init__(self, title, description, deadline, priority):
        self.title = title
        self.description = description
        self.deadline = deadline  # Data no formato 'YYYY-MM-DD'
        self.priority = priority  # 'low', 'medium', 'high'
        self.status = StatusEnum.pending  # Status inicial

    def conclude(self):
        """Marca a tarefa como concluída."""
        self.status = StatusEnum.concluded

    def edit(self, title=None, description=None, deadline=None, priority=None):
        """Edita os dados da tarefa."""
        if title:
            self.title = title
        if description:
            self.description = description
        if deadline:
            self.deadline = deadline
        if priority:
            self.priority = priority

    def checkDelay(self):
        """Verifica se a tarefa está atrasada."""
        deadline = datetime.strptime(self.deadline, "%Y-%m-%d")
        today = datetime.today()
        if deadline < today and self.status != StatusEnum.concluded:
            self.status = StatusEnum.delayed

    def toDict(self):
        """Converte a tarefa para um dicionário para salvar em JSON."""
        return {
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline,
            "priority": self.priority.value,  # Salva como string (low, medium, high)
            "status": self.status.value  # Salva o status como string
        }

    @staticmethod
    def fromDict(data):
        """Cria uma tarefa a partir de um dicionário (ao carregar do JSON)."""
        
        # Mapeia os valores da prioridade de volta para o enum.
        priority_map = {
            'baixa': PriorityEnum.low,
            'média': PriorityEnum.medium,
            'alta': PriorityEnum.high
        }
        
        # Mapeia os valores do status de volta para o enum.
        status_map = {
            'pendente': StatusEnum.pending,
            'cancelada': StatusEnum.canceled,
            'atrasada': StatusEnum.delayed,
            'bloqueada': StatusEnum.blocked,
            'concluída': StatusEnum.concluded,
            'em progresso': StatusEnum.ongoing
        }
        
        # Converte o status e prioridade de volta para seus respectivos enums
        status = status_map.get(data["status"].lower(), StatusEnum.pending)  # Valor padrão 'pending'
        priority = priority_map.get(data["priority"].lower(), PriorityEnum.low)  # Valor padrão 'low'
        
        return Task(data["title"], data["description"], data["deadline"], priority)

# Classe que gerencia a lista de tarefas
class TaskManager:
    def __init__(self):
        self.tasks = []
        self.loadTasks()  # Carrega as tarefas ao iniciar o gerenciador

    def addTask(self, task):
        """Adiciona uma nova tarefa ao sistema."""
        self.tasks.append(task)
        self.saveTasks()

    def listTasks(self):
        """Retorna todas as tarefas cadastradas."""
        return self.tasks

    def filter(self, status):
        """Filtra tarefas por status."""
        return [task for task in self.tasks if task.status == status]

    def removeTask(self, task):
        """Remove uma tarefa da lista."""
        if task in self.tasks:
            self.tasks.remove(task)
            self.saveTasks()

    def concludeTask(self, task):
        """Marca uma tarefa como concluída."""
        task.conclude()
        self.saveTasks()

    def saveTasks(self):
        """Salva todas as tarefas em um arquivo JSON."""
        tasksDict = [task.toDict() for task in self.tasks]
        with open("tasks.json", "w") as f:
            json.dump(tasksDict, f)

    def loadTasks(self):
        """Carrega tarefas de um arquivo JSON."""
        try:
            with open("tasks.json", "r") as f:
                tasksDict = json.load(f)
                self.tasks = [Task.fromDict(t) for t in tasksDict]
        except FileNotFoundError:
            self.tasks = []

    def updateTaskList(self, treeview):
        """Atualiza a lista de tarefas na interface gráfica."""
        for item in treeview.get_children():
            treeview.delete(item)

        for task in self.listTasks():
            treeview.insert("", "end", values=(task.title, task.status.value, task.deadline, task.priority.value))

# Funções da interface gráfica

# Função para adicionar uma nova tarefa
def addTaskGUI():
    title = entryTitle.get()
    description = entryDescription.get()
    deadline = entryDeadline.get()
    priority = comboPriority.get()

    if not title or not description or not deadline or not priority:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    task = Task(title, description, deadline, PriorityEnum[priority.lower()])
    taskManager.addTask(task)
    taskManager.updateTaskList(taskList)

    # Limpar os campos
    entryTitle.delete(0, tk.END)
    entryDescription.delete(0, tk.END)
    entryDeadline.delete(0, tk.END)

# Função para remover a tarefa selecionada
def removeTaskGUI():
    selected = taskList.selection()
    if not selected:
        messagebox.showerror("Error", "Select a task to remove.")
        return

    for item in selected:
        title = taskList.item(item)["values"][0]
        task = next((t for t in taskManager.listTasks() if t.title == title), None)
        if task:
            taskManager.removeTask(task)

    taskManager.updateTaskList(taskList)

# Função para marcar a tarefa como concluída
def concludedTaskGUI():
    selected = taskList.selection()
    if not selected:
        messagebox.showerror("Error", "Select a task to conclude.")
        return

    for item in selected:
        title = taskList.item(item)["values"][0]
        task = next((t for t in taskManager.listTasks() if t.title == title), None)
        if task:
            taskManager.concludeTask(task)

    taskManager.updateTaskList(taskList)

# Configuração da interface gráfica
root = tk.Tk()
root.title("Gerenciador de Tarefas")

# Criando o Gerenciador de Tarefas
taskManager = TaskManager()

# Labels e Campos de Entrada
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

# Botões
buttonAdd = tk.Button(root, text="Adicionar Tarefa", command=addTaskGUI)
buttonAdd.grid(row=4, column=1)

buttonConcluded = tk.Button(root, text="Concluir Tarefa", command=concludedTaskGUI)
buttonConcluded.grid(row=5, column=0)

buttonRemove = tk.Button(root, text="Remover Tarefa", command=removeTaskGUI)
buttonRemove.grid(row=5, column=1)

# Lista de Tarefas
taskList = ttk.Treeview(root, columns=("Título", "Status", "Prazo", "Prioridade"), show="headings")
taskList.grid(row=6, column=0, columnspan=2)

taskList.heading("Título", text="Título")
taskList.heading("Status", text="Status")
taskList.heading("Prazo", text="Prazo")
taskList.heading("Prioridade", text="Prioridade")

# Atualizar a lista de tarefas na interface
taskManager.updateTaskList(taskList)

# Iniciar a interface
root.mainloop()
