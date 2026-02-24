# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TodoTask(models.Model):
    """
    Todo Task Model - Odoo'da ilk modelim!
    
    Bu model bir PostgreSQL tablosu oluşturur: todo_task
    """
    _name = 'todo.task'
    _description = 'Todo Task'
    _order = 'priority desc, id desc'
    
    # Fields (Alanlar) - Her alan bir veritabanı kolonudur
    name = fields.Char(
        string='Task Name',
        required=True,
        help='Yapılacak işin adı'
    )
    
    description = fields.Text(
        string='Description',
        help='Detaylı açıklama'
    )
    
    is_done = fields.Boolean(
        string='Done?',
        default=False,
        help='Task tamamlandı mı?'
    )
    
    priority = fields.Selection(
        [
            ('0', 'Low'),
            ('1', 'Normal'),
            ('2', 'High'),
            ('3', 'Very High'),
        ],
        string='Priority',
        default='1',
    )
    
    due_date = fields.Date(
        string='Due Date',
        help='Bitiş tarihi'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        help='Bu görevi yapacak kişi'
    )
    
    # Computed field - otomatik hesaplanan alan
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    
    # Method - İş mantığı
    def action_mark_done(self):
        """Task'ı tamamla"""
        for task in self:
            task.is_done = True
        return True
    
    def action_mark_undone(self):
        """Task'ı tekrar aktif yap"""
        for task in self:
            task.is_done = False
        return True
