from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    自定义权限：只允许对象的所有者访问
    """
    
    def has_object_permission(self, request, view, obj):
        # 检查obj.user是否是请求用户
        return obj.user == request.user
        
class IsAdminUser(permissions.BasePermission):
    """
    自定义权限：只允许管理员访问
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
        
class ReadOnly(permissions.BasePermission):
    """
    自定义权限：只允许GET请求
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS 