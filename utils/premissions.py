from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy


class RoleRequiredMixin(AccessMixin):
    """
    Mixin to check if the user has the required role.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # 检查用户的角色是否在允许的角色列表中
        user_role = request.session.get('user_role')
        if not (request.user.is_superuser or user_role in self.allowed_roles):
            return HttpResponseRedirect(reverse_lazy('user_login'))
        return super().dispatch(request, *args, **kwargs)


def role_required(*allowed_roles):
    """
    Decorator to check if the user has the required role.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # 实现验证
            user_role = request.session.get('user_role')
            if request.user.is_authenticated and user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({'status': 'error', 'message': '无权限访问'}, status=403)
        return _wrapped_view
    return decorator