#coding=utf-8
__author__ = '王健'

from django import forms

class EmailSubscribe(forms.Form):
    email=forms.EmailField(max_length=40)
  