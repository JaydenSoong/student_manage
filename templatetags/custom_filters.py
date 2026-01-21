from django import template

# 固定写法
register = template.Library()

@register.filter
def handleGender(value):
    return '男' if (value == 'M') else '女'